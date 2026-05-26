from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Any

from product.backend.aspects_v2 import ASPECT_V2_SPECS, render_aspects_v2_from_package
from product.backend.llm import DeepSeekAPIError, DeepSeekClient, load_env_file
from product.backend.phone_summary import DEEPSEEK_PHONE_SUMMARY_ERROR, render_phone_summary_from_package
from product.backend.stability import render_stability_from_package

PHONE_SUMMARY_MODEL = "deepseek-v4-pro"


def build_product_review_render(package: dict[str, Any], *, tone_pack: str = "customer") -> dict[str, Any]:
    return build_product_review_core_render(package, tone_pack=tone_pack, include_aspects=True)


def build_product_review_core_render(
    package: dict[str, Any],
    *,
    tone_pack: str = "customer",
    include_aspects: bool = False,
) -> dict[str, Any]:
    client, configured_model = _resolve_render_client()

    rendered_sections, phone_summary = _render_core_sections_v2(
        package,
        client=client,
        configured_model=configured_model,
        tone_pack=tone_pack,
        include_aspects=include_aspects,
    )

    public_sections = {
        key: _strip_internal_render_fields(section)
        for key, section in rendered_sections.items()
    }
    public_phone_summary = _strip_internal_render_fields(phone_summary)
    meta = {
        "render_mode": "llm",
        "render_strategy": "v2",
        "configured_model": configured_model,
        "generated_at": _utc_now(),
        "tone_pack": tone_pack,
        "llm_sections": ["phone_summary", "stability", *[item["aspect_key"] for item in ASPECT_V2_SPECS]],
        "used_llm": True,
    }

    return {
        "meta": meta,
        "phone_summary": public_phone_summary,
        "sections": public_sections,
    }


def build_product_review_aspects_render(
    package: dict[str, Any],
    *,
    tone_pack: str = "customer",
    on_result: Any | None = None,
) -> dict[str, dict[str, Any]]:
    client, configured_model = _resolve_render_client()

    def handle_result(aspect_key: str, result: Any) -> None:
        if not callable(on_result):
            return
        on_result(aspect_key, _strip_internal_render_fields(result.to_dict()))

    rendered_aspects = render_aspects_v2_from_package(
        package,
        tone_pack=tone_pack,
        client=client,
        model=configured_model,
        thinking_enabled=False,
        max_tokens=_get_aspects_max_tokens(),
        on_result=handle_result if callable(on_result) else None,
    )
    return {
        key: _strip_internal_render_fields(value.to_dict())
        for key, value in rendered_aspects.items()
    }


def _render_core_sections_v2(
    package: dict[str, Any],
    *,
    client: DeepSeekClient,
    configured_model: str,
    tone_pack: str,
    include_aspects: bool,
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    rendered_sections: dict[str, dict[str, Any]] = {}
    phone_summary: dict[str, Any] = {}

    with ThreadPoolExecutor(max_workers=3) as executor:
        future_map = {
            executor.submit(
                render_phone_summary_from_package,
                package,
                tone_pack=tone_pack,
                client=client,
                model=PHONE_SUMMARY_MODEL,
                thinking_enabled=False,
            ): "phone_summary",
            executor.submit(
                render_stability_from_package,
                package,
                tone_pack=tone_pack,
                client=client,
                model=configured_model,
                thinking_enabled=False,
            ): "stability",
        }
        if include_aspects:
            future_map[
                executor.submit(
                    render_aspects_v2_from_package,
                    package,
                    tone_pack=tone_pack,
                    client=client,
                    model=configured_model,
                    thinking_enabled=False,
                    max_tokens=_get_aspects_max_tokens(),
                )
            ] = "aspects_v2"

        for future in as_completed(future_map):
            target = future_map[future]
            result = future.result()
            if target == "phone_summary":
                phone_summary = result.to_dict()
            elif target == "stability":
                rendered_sections["stability"] = result.to_dict()
            elif target == "aspects_v2":
                rendered_sections.update({key: value.to_dict() for key, value in result.items()})

    return rendered_sections, phone_summary


def _get_aspects_max_tokens() -> int:
    return _get_int_env("EASEWISE_REVIEW_ASPECTS_MAX_TOKENS", 1800, minimum=600, maximum=3200)


def _get_int_env(name: str, default: int, *, minimum: int, maximum: int) -> int:
    raw_value = os.getenv(name, str(default)).strip()
    try:
        return max(minimum, min(maximum, int(raw_value)))
    except ValueError:
        return default


def _resolve_render_client() -> tuple[DeepSeekClient, str]:
    load_env_file()
    if not os.getenv("DEEPSEEK_API_KEY", "").strip():
        raise DeepSeekAPIError(DEEPSEEK_PHONE_SUMMARY_ERROR)

    try:
        client = DeepSeekClient.from_env()
        configured_model = os.getenv("EASEWISE_REVIEW_MODEL", "").strip() or client.config.model
        return client, configured_model
    except Exception as exc:
        raise DeepSeekAPIError(DEEPSEEK_PHONE_SUMMARY_ERROR) from exc


def _strip_internal_render_fields(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in payload.items()
        if key not in {"raw_model_output", "tone_pack", "model_name"}
    }


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
