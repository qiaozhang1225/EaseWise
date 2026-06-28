from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from queue import Queue
from typing import Any, Iterator

from features.phone_qimen.rendering import (
    DEEPSEEK_PHONE_SUMMARY_ERROR,
    render_phone_summary_from_package,
    render_stability_from_package,
    stream_aspect_from_package,
    stream_phone_summary_from_package,
    stream_stability_from_package,
)
from product.backend.llm import DeepSeekAPIError, DeepSeekClient, load_env_file

PHONE_SUMMARY_MODEL = "deepseek-v4-pro"


def build_product_review_render(package: dict[str, Any], *, tone_pack: str = "customer") -> dict[str, Any]:
    return build_product_review_core_render(package, tone_pack=tone_pack)


def build_product_review_core_render(
    package: dict[str, Any],
    *,
    tone_pack: str = "customer",
) -> dict[str, Any]:
    client, configured_model = _resolve_render_client()

    rendered_sections, phone_summary = _render_core_sections_v2(
        package,
        client=client,
        configured_model=configured_model,
        tone_pack=tone_pack,
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
        "llm_sections": ["phone_summary", "stability"],
        "used_llm": True,
    }

    return {
        "meta": meta,
        "phone_summary": public_phone_summary,
        "sections": public_sections,
    }


def stream_product_review_aspect_render(
    package: dict[str, Any],
    *,
    aspect_key: str,
    tone_pack: str = "customer",
    user_id: str | None = None,
    request_id: str | None = None,
):
    client, configured_model = _resolve_render_client()
    return stream_aspect_from_package(
        package,
        aspect_key=aspect_key,
        tone_pack=tone_pack,  # type: ignore[arg-type]
        client=client,
        model=configured_model,
        thinking_enabled=False,
        max_tokens=_get_aspects_max_tokens(),
        user_id=user_id,
        request_id=request_id,
    )


def stream_product_review_core_render(
    package: dict[str, Any],
    *,
    tone_pack: str = "customer",
    user_id: str | None = None,
    request_id: str | None = None,
) -> Iterator[dict[str, Any]]:
    client, configured_model = _resolve_render_client()
    event_queue: Queue[dict[str, Any]] = Queue()
    rendered_sections: dict[str, dict[str, Any]] = {}
    phone_summary: dict[str, Any] = {}

    def run_section(section: str) -> None:
        try:
            if section == "phone_summary":
                event_iter = stream_phone_summary_from_package(
                    package,
                    tone_pack=tone_pack,  # type: ignore[arg-type]
                    client=client,
                    model=PHONE_SUMMARY_MODEL,
                    thinking_enabled=False,
                    user_id=user_id,
                    request_id=f"{request_id}:phone_summary" if request_id else None,
                )
                result_key = "phone_summary"
            else:
                event_iter = stream_stability_from_package(
                    package,
                    tone_pack=tone_pack,  # type: ignore[arg-type]
                    client=client,
                    model=configured_model,
                    thinking_enabled=False,
                    user_id=user_id,
                    request_id=f"{request_id}:stability" if request_id else None,
                )
                result_key = "stability"

            for render_event in event_iter:
                event_name = str(render_event.get("event") or "")
                event_data = render_event.get("data") if isinstance(render_event.get("data"), dict) else {}
                if event_name == "status":
                    event_queue.put({"event": "core_status", "data": {"section": section, **event_data}})
                    continue
                if event_name == "delta":
                    event_queue.put({"event": "core_delta", "data": {"section": section, **event_data}})
                    continue
                if event_name == "result":
                    result_payload = event_data.get(result_key) if isinstance(event_data, dict) else None
                    if not isinstance(result_payload, dict):
                        raise DeepSeekAPIError(f"{section}_stream_missing_result")
                    stripped_payload = _strip_internal_render_fields(result_payload)
                    if section == "phone_summary":
                        phone_summary.update(stripped_payload)
                    else:
                        rendered_sections["stability"] = stripped_payload
                    event_queue.put(
                        {
                            "event": "section_complete",
                            "data": {"section": section, "payload": stripped_payload, "model_name": event_data.get("model_name")},
                        }
                    )
                    return
            raise DeepSeekAPIError(f"{section}_stream_missing_result")
        except Exception as exc:
            event_queue.put({"event": "error", "error": exc, "section": section})
        finally:
            event_queue.put({"event": "_done", "section": section})

    section_count = 2
    with ThreadPoolExecutor(max_workers=section_count) as executor:
        for section_name in ("phone_summary", "stability"):
            executor.submit(run_section, section_name)

        done_count = 0
        first_error: Exception | None = None
        while done_count < section_count:
            queued_event = event_queue.get()
            event_name = str(queued_event.get("event") or "")
            if event_name == "_done":
                done_count += 1
                continue
            if event_name == "error":
                error = queued_event.get("error")
                first_error = error if isinstance(error, Exception) else DeepSeekAPIError("phone_qimen_core_stream_failed")
                continue
            yield queued_event

        if first_error is not None:
            raise first_error

    public_sections = {
        key: _strip_internal_render_fields(section)
        for key, section in rendered_sections.items()
    }
    public_phone_summary = _strip_internal_render_fields(phone_summary)
    product_render = {
        "meta": {
            "render_mode": "llm",
            "render_strategy": "v2_stream",
            "configured_model": configured_model,
            "generated_at": _utc_now(),
            "tone_pack": tone_pack,
            "llm_sections": ["phone_summary", "stability"],
            "used_llm": True,
        },
        "phone_summary": public_phone_summary,
        "sections": public_sections,
    }
    yield {"event": "result", "data": {"product_render": product_render}}


def _render_core_sections_v2(
    package: dict[str, Any],
    *,
    client: DeepSeekClient,
    configured_model: str,
    tone_pack: str,
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
        for future in as_completed(future_map):
            target = future_map[future]
            result = future.result()
            if target == "phone_summary":
                phone_summary = result.to_dict()
            elif target == "stability":
                rendered_sections["stability"] = result.to_dict()

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
