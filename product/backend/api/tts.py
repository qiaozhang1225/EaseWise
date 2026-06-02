from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Iterable

import httpx

from .config import (
    get_aliyun_nls_access_key_id,
    get_aliyun_nls_access_key_secret,
    get_aliyun_tts_app_key,
    get_aliyun_tts_endpoint,
    get_aliyun_tts_token,
    get_bailian_tts_api_key,
    get_bailian_tts_endpoint,
    get_bailian_tts_model,
    get_tts_timeout_seconds,
    get_voice_cache_dir,
)
from .aliyun_nls_token import AliyunNlsTokenError, resolve_aliyun_nls_token

VOICE_AUDIO_FORMAT = "mp3"
VOICE_STATIC_URL_PREFIX = "/api/v1/static/voice"
ALIYUN_TTS_MAX_CHARS_PER_SEGMENT = 280
ALIYUN_TTS_VOLUME = "70"
ALIYUN_TTS_SPEECH_RATE = "50"
ALIYUN_TTS_PITCH_RATE = "0"
BAILIAN_TTS_MAX_CHARS_PER_SEGMENT = 1800
BAILIAN_DEFAULT_VOICE = "longanyang"
BAILIAN_VOICE_ALIASES = {
    "xiaoyun": BAILIAN_DEFAULT_VOICE,
    "xiaogang": BAILIAN_DEFAULT_VOICE,
}


class VoiceSynthesisError(RuntimeError):
    pass


class VoiceProviderUnavailableError(VoiceSynthesisError):
    pass


@dataclass(frozen=True)
class VoiceAudioResult:
    text_hash: str
    audio_path: Path
    audio_url: str
    provider: str
    voice_key: str
    format: str
    char_count: int
    cached: bool


def synthesize_voice_audio(
    *,
    text: str,
    scene: str,
    provider: str,
    voice_key: str,
    cache_enabled: bool,
) -> VoiceAudioResult:
    normalized_provider = provider.strip().lower() or "aliyun"
    if normalized_provider == "aliyun" and not is_aliyun_nls_tts_configured() and is_bailian_tts_configured():
        normalized_provider = "bailian"
    normalized_voice_key = voice_key.strip() or "xiaoyun"
    normalized_text = normalize_voice_text(text)
    if not normalized_text:
        raise VoiceSynthesisError("voice_text_empty")

    text_hash = build_voice_text_hash(
        text=normalized_text,
        scene=scene,
        provider=normalized_provider,
        voice_key=normalized_voice_key,
        audio_format=VOICE_AUDIO_FORMAT,
        synthesis_params=resolve_voice_hash_params(normalized_provider),
    )
    cache_dir = get_voice_cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)
    audio_path = cache_dir / f"{text_hash}.{VOICE_AUDIO_FORMAT}"
    audio_url = f"{VOICE_STATIC_URL_PREFIX}/{audio_path.name}"

    if cache_enabled and audio_path.exists() and audio_path.stat().st_size > 0:
        return VoiceAudioResult(
            text_hash=text_hash,
            audio_path=audio_path,
            audio_url=audio_url,
            provider=normalized_provider,
            voice_key=normalized_voice_key,
            format=VOICE_AUDIO_FORMAT,
            char_count=len(normalized_text),
            cached=True,
        )

    audio_bytes = synthesize_with_provider(
        text=normalized_text,
        provider=normalized_provider,
        voice_key=normalized_voice_key,
    )
    if not audio_bytes:
        raise VoiceSynthesisError("voice_audio_empty")

    _write_audio_file(audio_path, audio_bytes)
    return VoiceAudioResult(
        text_hash=text_hash,
        audio_path=audio_path,
        audio_url=audio_url,
        provider=normalized_provider,
        voice_key=normalized_voice_key,
        format=VOICE_AUDIO_FORMAT,
        char_count=len(normalized_text),
        cached=False,
    )


def synthesize_with_provider(*, text: str, provider: str, voice_key: str) -> bytes:
    if provider == "bailian":
        return synthesize_with_bailian(text=text, voice_key=voice_key)
    if provider == "aliyun":
        return synthesize_with_aliyun(text=text, voice_key=voice_key)
    if provider in {"tencent", "openai"}:
        raise VoiceProviderUnavailableError(f"{provider}_provider_not_configured")
    raise VoiceProviderUnavailableError("voice_provider_not_supported")


def is_bailian_tts_configured() -> bool:
    return bool(get_bailian_tts_api_key())


def is_aliyun_nls_tts_configured() -> bool:
    has_app_key = bool(get_aliyun_tts_app_key())
    has_static_token = bool(get_aliyun_tts_token())
    has_access_keys = bool(get_aliyun_nls_access_key_id() and get_aliyun_nls_access_key_secret())
    return has_app_key and (has_static_token or has_access_keys)


def synthesize_with_bailian(*, text: str, voice_key: str) -> bytes:
    api_key = get_bailian_tts_api_key()
    endpoint = get_bailian_tts_endpoint()
    model = get_bailian_tts_model()
    if not api_key or not endpoint or not model:
        raise VoiceProviderUnavailableError("bailian_tts_not_configured")

    chunks = list(split_voice_text(text, BAILIAN_TTS_MAX_CHARS_PER_SEGMENT))
    if not chunks:
        raise VoiceSynthesisError("voice_text_empty")

    audio_parts: list[bytes] = []
    timeout = httpx.Timeout(get_tts_timeout_seconds())
    with httpx.Client(timeout=timeout) as client:
        for chunk in chunks:
            response = client.post(
                endpoint,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "input": {
                        "text": chunk,
                        "voice": normalize_bailian_voice_key(voice_key),
                        "format": VOICE_AUDIO_FORMAT,
                        "sample_rate": 24000,
                    },
                },
            )
            if response.status_code != 200:
                raise VoiceSynthesisError(f"bailian_tts_http_{response.status_code}")
            try:
                payload = response.json()
            except ValueError as exc:
                raise VoiceSynthesisError("bailian_tts_invalid_response") from exc
            audio_url = extract_bailian_audio_url(payload)
            if not audio_url:
                raise VoiceSynthesisError(_extract_bailian_error(payload))
            audio_response = client.get(audio_url)
            if audio_response.status_code != 200:
                raise VoiceSynthesisError(f"bailian_tts_audio_http_{audio_response.status_code}")
            audio_parts.append(audio_response.content)

    return b"".join(audio_parts)


def synthesize_with_aliyun(*, text: str, voice_key: str) -> bytes:
    app_key = get_aliyun_tts_app_key()
    try:
        token = resolve_aliyun_nls_token()
    except AliyunNlsTokenError as exc:
        raise VoiceProviderUnavailableError(str(exc) or "aliyun_nls_token_unavailable") from exc
    endpoint = get_aliyun_tts_endpoint()
    if not app_key or not token or not endpoint:
        raise VoiceProviderUnavailableError("aliyun_tts_not_configured")

    chunks = list(split_voice_text(text, ALIYUN_TTS_MAX_CHARS_PER_SEGMENT))
    if not chunks:
        raise VoiceSynthesisError("voice_text_empty")

    audio_parts: list[bytes] = []
    timeout = httpx.Timeout(get_tts_timeout_seconds())
    with httpx.Client(timeout=timeout) as client:
        for chunk in chunks:
            response = client.get(
                endpoint,
                params={
                    "appkey": app_key,
                    "token": token,
                    "text": chunk,
                    "format": VOICE_AUDIO_FORMAT,
                    "sample_rate": "16000",
                    "voice": voice_key,
                    "volume": ALIYUN_TTS_VOLUME,
                    "speech_rate": ALIYUN_TTS_SPEECH_RATE,
                    "pitch_rate": ALIYUN_TTS_PITCH_RATE,
                },
            )
            if response.status_code != 200:
                raise VoiceSynthesisError(f"aliyun_tts_http_{response.status_code}")
            content_type = response.headers.get("content-type", "").lower()
            if "json" in content_type or response.content[:1] in {b"{", b"["}:
                raise VoiceSynthesisError(_extract_aliyun_error(response.content))
            audio_parts.append(response.content)

    return b"".join(audio_parts)


def normalize_bailian_voice_key(voice_key: str) -> str:
    normalized_voice_key = voice_key.strip() or BAILIAN_DEFAULT_VOICE
    return BAILIAN_VOICE_ALIASES.get(normalized_voice_key, normalized_voice_key)


def extract_bailian_audio_url(payload: dict[str, object]) -> str | None:
    output = payload.get("output")
    if not isinstance(output, dict):
        return None
    audio = output.get("audio")
    if isinstance(audio, dict):
        audio_url = audio.get("url")
        return str(audio_url).strip() if audio_url else None
    audio_url = output.get("audio_url") or output.get("url")
    return str(audio_url).strip() if audio_url else None


def normalize_voice_text(text: str) -> str:
    normalized = re.sub(r"\s+", " ", str(text or "")).strip()
    normalized = re.sub(r"[#*_`~>\[\]{}]+", "", normalized)
    normalized = normalized.replace("：", "。").replace(":", "。")
    normalized = re.sub(r"。{2,}", "。", normalized)
    return normalized.strip(" 。")


def build_voice_text_hash(*, text: str, scene: str, provider: str, voice_key: str, audio_format: str, synthesis_params: dict[str, object] | None = None) -> str:
    payload = {
        "format": audio_format,
        "provider": provider,
        "scene": scene,
        "synthesis_params": synthesis_params or {},
        "text": text,
        "voice_key": voice_key,
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def resolve_voice_hash_params(provider: str) -> dict[str, object]:
    if provider == "aliyun":
        return {
            "sample_rate": "16000",
            "volume": ALIYUN_TTS_VOLUME,
            "speech_rate": ALIYUN_TTS_SPEECH_RATE,
            "pitch_rate": ALIYUN_TTS_PITCH_RATE,
        }
    if provider == "bailian":
        return {
            "sample_rate": 24000,
        }
    return {}


def split_voice_text(text: str, max_chars: int) -> Iterable[str]:
    clean_text = normalize_voice_text(text)
    if len(clean_text) <= max_chars:
        yield clean_text
        return

    sentences = [item for item in re.split(r"(?<=[。！？!?；;])", clean_text) if item.strip()]
    buffer = ""
    for sentence in sentences:
        candidate = f"{buffer}{sentence}".strip()
        if len(candidate) <= max_chars:
            buffer = candidate
            continue
        if buffer:
            yield buffer
            buffer = ""
        while len(sentence) > max_chars:
            yield sentence[:max_chars]
            sentence = sentence[max_chars:]
        buffer = sentence.strip()
    if buffer:
        yield buffer


def _write_audio_file(audio_path: Path, audio_bytes: bytes) -> None:
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("wb", delete=False, dir=audio_path.parent, prefix=f".{audio_path.stem}.", suffix=".tmp") as tmp_file:
        tmp_file.write(audio_bytes)
        tmp_path = Path(tmp_file.name)
    tmp_path.replace(audio_path)


def _extract_aliyun_error(raw_content: bytes) -> str:
    try:
        payload = json.loads(raw_content.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return "aliyun_tts_failed"
    if isinstance(payload, dict):
        message = payload.get("message") or payload.get("Message") or payload.get("error")
        code = payload.get("code") or payload.get("Code")
        if message and code:
            return f"aliyun_tts_failed:{code}:{message}"
        if message:
            return f"aliyun_tts_failed:{message}"
    return "aliyun_tts_failed"


def _extract_bailian_error(payload: dict[str, object]) -> str:
    code = str(payload.get("code") or "").strip()
    message = str(payload.get("message") or payload.get("error") or "").strip()
    if code and message:
        return f"bailian_tts_failed:{code}:{message}"
    if code:
        return f"bailian_tts_failed:{code}"
    if message:
        return f"bailian_tts_failed:{message}"
    return "bailian_tts_failed"
