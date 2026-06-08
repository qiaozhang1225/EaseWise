from __future__ import annotations

import os
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Literal

PriorityClass = Literal["foreground_core", "foreground_interactive", "background_prefetch"]

PRIORITY_RANK: dict[str, int] = {
    "foreground_core": 0,
    "foreground_interactive": 1,
    "background_prefetch": 2,
}

DEFAULT_PROVIDER = "deepseek"
DEFAULT_MAX_CONCURRENCY = 450
DEFAULT_COOLDOWN_SECONDS = 60


class LLMGovernorError(RuntimeError):
    pass


@dataclass(frozen=True)
class LLMKeyConfig:
    key_id: str
    provider: str
    model: str
    display_name: str
    api_key: str
    priority: int
    max_concurrency: int
    cooldown_seconds: int
    enabled: bool = True
    masked_key: str | None = None
    secret_configured: bool = True


@dataclass
class _KeyRuntime:
    inflight: int = 0
    cooldown_until: float = 0.0
    last_rate_limited_at: str | None = None
    last_error_message: str | None = None
    last_used_at: str | None = None


@dataclass
class LLMLease:
    governor: "DeepSeekGovernor"
    key: LLMKeyConfig
    priority_class: str
    llm_scene: str | None
    user_id: str | None
    request_id: str | None
    wait_ms: int
    acquired_at: float
    released: bool = False

    @property
    def api_key(self) -> str:
        return self.key.api_key

    @property
    def key_id(self) -> str:
        return self.key.key_id

    @property
    def model(self) -> str:
        return self.key.model

    def mark_rate_limited(self, detail: str | None = None) -> None:
        self.governor.mark_rate_limited(self, detail=detail)

    def release(self, *, error_type: str | None = None, error_message: str | None = None) -> None:
        if self.released:
            return
        self.released = True
        self.governor.release(self, error_type=error_type, error_message=error_message)

    def to_meta(self, *, duration_ms: int | None = None, error_type: str | None = None) -> dict[str, Any]:
        return {
            "llm_key_id": self.key.key_id,
            "llm_key_name": self.key.display_name,
            "model": self.key.model,
            "priority_class": self.priority_class,
            "llm_scene": self.llm_scene,
            "wait_ms": self.wait_ms,
            "duration_ms": duration_ms,
            "retry_count": 0,
            "error_type": error_type,
        }


class _MemoryConcurrencyBackend:
    def __init__(self) -> None:
        self._condition = threading.Condition()
        self._runtime_by_key: dict[str, _KeyRuntime] = {}
        self._waiters_by_priority: dict[str, int] = {key: 0 for key in PRIORITY_RANK}
        self._inflight_by_priority: dict[str, int] = {key: 0 for key in PRIORITY_RANK}
        self._metrics = {
            "requests_total": 0,
            "completed_total": 0,
            "failed_total": 0,
            "rate_limited_total": 0,
            "timeout_total": 0,
            "wait_ms_total": 0,
            "duration_ms_total": 0,
            "duration_count": 0,
            "recent_429_count": 0,
            "recent_timeout_count": 0,
        }
        self._recent_events: list[tuple[float, str]] = []

    def acquire(
        self,
        *,
        keys: list[LLMKeyConfig],
        priority_class: str,
        llm_scene: str | None,
        user_id: str | None,
        request_id: str | None,
        background_prefetch_enabled: bool,
        background_max_concurrency_ratio: float,
    ) -> LLMLease:
        if not keys:
            raise LLMGovernorError("deepseek_api_key_not_configured")
        normalized_priority = normalize_priority_class(priority_class)
        if normalized_priority == "background_prefetch" and not background_prefetch_enabled:
            raise LLMGovernorError("background_prefetch_disabled")

        start = time.monotonic()
        with self._condition:
            self._waiters_by_priority[normalized_priority] = self._waiters_by_priority.get(normalized_priority, 0) + 1
            waiter_removed = False
            try:
                while True:
                    self._prune_recent_events_locked()
                    selected = self._select_available_key_locked(
                        keys,
                        priority_class=normalized_priority,
                        background_max_concurrency_ratio=background_max_concurrency_ratio,
                    )
                    if selected is not None:
                        runtime = self._runtime_by_key.setdefault(selected.key_id, _KeyRuntime())
                        runtime.inflight += 1
                        runtime.last_used_at = _utc_now()
                        self._waiters_by_priority[normalized_priority] -= 1
                        waiter_removed = True
                        self._inflight_by_priority[normalized_priority] = self._inflight_by_priority.get(normalized_priority, 0) + 1
                        wait_ms = int((time.monotonic() - start) * 1000)
                        self._metrics["requests_total"] += 1
                        self._metrics["wait_ms_total"] += wait_ms
                        return LLMLease(
                            governor=None,  # type: ignore[arg-type]
                            key=selected,
                            priority_class=normalized_priority,
                            llm_scene=llm_scene,
                            user_id=user_id,
                            request_id=request_id,
                            wait_ms=wait_ms,
                            acquired_at=time.monotonic(),
                        )

                    wait_seconds = self._next_wait_seconds_locked(keys)
                    self._condition.wait(timeout=wait_seconds)
            finally:
                if not waiter_removed and self._waiters_by_priority.get(normalized_priority, 0) > 0:
                    self._waiters_by_priority[normalized_priority] -= 1

    def bind_lease(self, lease: LLMLease, governor: "DeepSeekGovernor") -> LLMLease:
        lease.governor = governor
        return lease

    def release(self, lease: LLMLease, *, error_type: str | None, error_message: str | None) -> None:
        duration_ms = int((time.monotonic() - lease.acquired_at) * 1000)
        with self._condition:
            runtime = self._runtime_by_key.setdefault(lease.key_id, _KeyRuntime())
            runtime.inflight = max(0, runtime.inflight - 1)
            self._inflight_by_priority[lease.priority_class] = max(0, self._inflight_by_priority.get(lease.priority_class, 0) - 1)
            runtime.last_used_at = _utc_now()
            if error_message:
                runtime.last_error_message = error_message[:500]
            if error_type:
                self._metrics["failed_total"] += 1
                if error_type == "timeout":
                    self._metrics["timeout_total"] += 1
                    self._recent_events.append((time.time(), "timeout"))
            else:
                self._metrics["completed_total"] += 1
            self._metrics["duration_ms_total"] += duration_ms
            self._metrics["duration_count"] += 1
            self._prune_recent_events_locked()
            self._condition.notify_all()

    def mark_rate_limited(self, lease: LLMLease, *, detail: str | None = None) -> None:
        now_text = _utc_now()
        cooldown_until = time.time() + max(1, lease.key.cooldown_seconds)
        with self._condition:
            runtime = self._runtime_by_key.setdefault(lease.key_id, _KeyRuntime())
            runtime.cooldown_until = max(runtime.cooldown_until, cooldown_until)
            runtime.last_rate_limited_at = now_text
            runtime.last_error_message = (detail or "DeepSeek 429 rate limited")[:500]
            self._metrics["rate_limited_total"] += 1
            self._recent_events.append((time.time(), "429"))
            self._prune_recent_events_locked()
            self._condition.notify_all()

    def snapshot(self, keys: list[LLMKeyConfig]) -> dict[str, Any]:
        now = time.time()
        with self._condition:
            self._prune_recent_events_locked()
            key_items: list[dict[str, Any]] = []
            for key in keys:
                runtime = self._runtime_by_key.setdefault(key.key_id, _KeyRuntime())
                cooldown_until_text = _timestamp_to_iso(runtime.cooldown_until) if runtime.cooldown_until > now else None
                available_slots = 0 if cooldown_until_text else max(0, key.max_concurrency - runtime.inflight)
                key_items.append(
                    {
                        "key_id": key.key_id,
                        "display_name": key.display_name,
                        "provider": key.provider,
                        "model": key.model,
                        "enabled": key.enabled,
                        "priority": key.priority,
                        "max_concurrency": key.max_concurrency,
                        "cooldown_seconds": key.cooldown_seconds,
                        "current_inflight": runtime.inflight,
                        "available_slots": available_slots,
                        "cooldown_until": cooldown_until_text,
                        "last_rate_limited_at": runtime.last_rate_limited_at,
                        "last_error_message": runtime.last_error_message,
                        "last_used_at": runtime.last_used_at,
                    }
                )
            global_inflight = sum(item["current_inflight"] for item in key_items)
            total_capacity = sum(item["max_concurrency"] for item in key_items if item["enabled"])
            avg_wait_ms = int(self._metrics["wait_ms_total"] / self._metrics["requests_total"]) if self._metrics["requests_total"] else 0
            avg_duration_ms = int(self._metrics["duration_ms_total"] / self._metrics["duration_count"]) if self._metrics["duration_count"] else 0
            return {
                "global_inflight": global_inflight,
                "foreground_waiting": self._waiters_by_priority.get("foreground_core", 0) + self._waiters_by_priority.get("foreground_interactive", 0),
                "background_waiting": self._waiters_by_priority.get("background_prefetch", 0),
                "foreground_inflight": self._inflight_by_priority.get("foreground_core", 0) + self._inflight_by_priority.get("foreground_interactive", 0),
                "background_inflight": self._inflight_by_priority.get("background_prefetch", 0),
                "enabled_key_count": len([key for key in keys if key.enabled]),
                "total_capacity": total_capacity,
                "recent_429_count": len([event for _, event in self._recent_events if event == "429"]),
                "recent_timeout_count": len([event for _, event in self._recent_events if event == "timeout"]),
                "avg_wait_ms": avg_wait_ms,
                "avg_duration_ms": avg_duration_ms,
                "keys": key_items,
            }

    def _select_available_key_locked(
        self,
        keys: list[LLMKeyConfig],
        *,
        priority_class: str,
        background_max_concurrency_ratio: float,
    ) -> LLMKeyConfig | None:
        now = time.time()
        if priority_class == "background_prefetch":
            foreground_waiters = self._waiters_by_priority.get("foreground_core", 0) + self._waiters_by_priority.get("foreground_interactive", 0)
            if foreground_waiters > 0:
                return None
            total_capacity = sum(max(0, key.max_concurrency) for key in keys)
            if total_capacity > 0:
                background_cap = max(1, int(total_capacity * max(0.0, min(0.8, background_max_concurrency_ratio))))
                if self._inflight_by_priority.get("background_prefetch", 0) >= background_cap:
                    return None

        sorted_keys = sorted(keys, key=lambda item: (item.priority, item.key_id))
        for key in sorted_keys:
            runtime = self._runtime_by_key.setdefault(key.key_id, _KeyRuntime())
            if runtime.cooldown_until > now:
                continue
            if runtime.inflight < key.max_concurrency:
                return key
        return None

    def _next_wait_seconds_locked(self, keys: list[LLMKeyConfig]) -> float:
        now = time.time()
        cooldowns = [
            self._runtime_by_key.setdefault(key.key_id, _KeyRuntime()).cooldown_until - now
            for key in keys
            if self._runtime_by_key.setdefault(key.key_id, _KeyRuntime()).cooldown_until > now
        ]
        if not cooldowns:
            return 0.5
        return max(0.05, min(0.5, min(cooldowns)))

    def _prune_recent_events_locked(self) -> None:
        cutoff = time.time() - 3600
        self._recent_events = [(ts, kind) for ts, kind in self._recent_events if ts >= cutoff]


class _RedisConcurrencyBackend:
    def __init__(self, redis_url: str) -> None:
        if not redis_url:
            raise LLMGovernorError("redis_url_not_configured")
        try:
            import redis  # type: ignore
        except Exception as exc:  # pragma: no cover - depends on optional deployment package
            raise LLMGovernorError("redis_package_not_installed") from exc
        self._redis = redis.Redis.from_url(redis_url, decode_responses=True)
        try:
            self._redis.ping()
        except Exception as exc:  # pragma: no cover - depends on optional deployment service
            raise LLMGovernorError("redis_backend_unavailable") from exc
        self._memory_waiters = _MemoryConcurrencyBackend()

    def acquire(
        self,
        *,
        keys: list[LLMKeyConfig],
        priority_class: str,
        llm_scene: str | None,
        user_id: str | None,
        request_id: str | None,
        background_prefetch_enabled: bool,
        background_max_concurrency_ratio: float,
    ) -> LLMLease:
        # Redis stores the distributed key counters; local waiters still keep
        # foreground/background wake-up behavior inside this process.
        lease = self._memory_waiters.acquire(
            keys=keys,
            priority_class=priority_class,
            llm_scene=llm_scene,
            user_id=user_id,
            request_id=request_id,
            background_prefetch_enabled=background_prefetch_enabled,
            background_max_concurrency_ratio=background_max_concurrency_ratio,
        )
        self._redis.hincrby(f"easewise:llm:deepseek:key:{lease.key_id}", "inflight", 1)
        return lease

    def bind_lease(self, lease: LLMLease, governor: "DeepSeekGovernor") -> LLMLease:
        return self._memory_waiters.bind_lease(lease, governor)

    def release(self, lease: LLMLease, *, error_type: str | None, error_message: str | None) -> None:
        key = f"easewise:llm:deepseek:key:{lease.key_id}"
        try:
            value = int(self._redis.hincrby(key, "inflight", -1))
            if value < 0:
                self._redis.hset(key, "inflight", 0)
        finally:
            self._memory_waiters.release(lease, error_type=error_type, error_message=error_message)

    def mark_rate_limited(self, lease: LLMLease, *, detail: str | None = None) -> None:
        key = f"easewise:llm:deepseek:key:{lease.key_id}"
        cooldown_until = time.time() + max(1, lease.key.cooldown_seconds)
        self._redis.hset(
            key,
            mapping={
                "cooldown_until": str(cooldown_until),
                "last_rate_limited_at": _utc_now(),
                "last_error_message": (detail or "DeepSeek 429 rate limited")[:500],
            },
        )
        self._memory_waiters.mark_rate_limited(lease, detail=detail)

    def snapshot(self, keys: list[LLMKeyConfig]) -> dict[str, Any]:
        snapshot = self._memory_waiters.snapshot(keys)
        now = time.time()
        for item in snapshot["keys"]:
            redis_key = f"easewise:llm:deepseek:key:{item['key_id']}"
            values = self._redis.hgetall(redis_key)
            inflight = int(values.get("inflight") or item["current_inflight"] or 0)
            cooldown_until_raw = values.get("cooldown_until")
            cooldown_until = float(cooldown_until_raw) if cooldown_until_raw else 0.0
            item["current_inflight"] = max(0, inflight)
            item["cooldown_until"] = _timestamp_to_iso(cooldown_until) if cooldown_until > now else item.get("cooldown_until")
            item["last_rate_limited_at"] = values.get("last_rate_limited_at") or item.get("last_rate_limited_at")
            item["last_error_message"] = values.get("last_error_message") or item.get("last_error_message")
            item["available_slots"] = 0 if item["cooldown_until"] else max(0, int(item["max_concurrency"]) - item["current_inflight"])
        snapshot["global_inflight"] = sum(item["current_inflight"] for item in snapshot["keys"])
        return snapshot


class DeepSeekGovernor:
    def __init__(self, *, backend_name: str, redis_url: str | None = None) -> None:
        self.backend_name = backend_name
        if backend_name == "redis":
            self._backend: Any = _RedisConcurrencyBackend(redis_url or "")
        elif backend_name == "memory":
            self._backend = _MemoryConcurrencyBackend()
        else:
            raise LLMGovernorError("invalid_llm_concurrency_backend")

    def acquire(
        self,
        *,
        model: str | None = None,
        priority_class: str | None = None,
        llm_scene: str | None = None,
        user_id: str | None = None,
        request_id: str | None = None,
    ) -> LLMLease:
        runtime_config = load_governance_config()
        keys = load_deepseek_keys(model=model, runtime_config=runtime_config)
        lease = self._backend.acquire(
            keys=keys,
            priority_class=priority_class or "foreground_interactive",
            llm_scene=llm_scene,
            user_id=user_id,
            request_id=request_id,
            background_prefetch_enabled=bool(runtime_config["background_prefetch_enabled"]),
            background_max_concurrency_ratio=float(runtime_config["background_max_concurrency_ratio"]),
        )
        return self._backend.bind_lease(lease, self)

    def release(self, lease: LLMLease, *, error_type: str | None = None, error_message: str | None = None) -> None:
        self._backend.release(lease, error_type=error_type, error_message=error_message)
        _record_key_runtime_event(
            key_id=lease.key_id,
            last_used_at=_utc_now(),
            last_error_message=error_message,
        )

    def mark_rate_limited(self, lease: LLMLease, *, detail: str | None = None) -> None:
        self._backend.mark_rate_limited(lease, detail=detail)
        now_text = _utc_now()
        _record_key_runtime_event(
            key_id=lease.key_id,
            last_used_at=now_text,
            last_rate_limited_at=now_text,
            last_error_message=detail or "DeepSeek 429 rate limited",
        )

    def status(self) -> dict[str, Any]:
        runtime_config = load_governance_config()
        keys = load_deepseek_keys(model=None, runtime_config=runtime_config, allow_missing=True)
        backend_available = True
        backend_error = None
        try:
            snapshot = self._backend.snapshot(keys)
        except Exception as exc:
            backend_available = False
            backend_error = str(exc)
            snapshot = {
                "global_inflight": 0,
                "foreground_waiting": 0,
                "background_waiting": 0,
                "foreground_inflight": 0,
                "background_inflight": 0,
                "enabled_key_count": len(keys),
                "total_capacity": sum(key.max_concurrency for key in keys),
                "recent_429_count": 0,
                "recent_timeout_count": 0,
                "avg_wait_ms": 0,
                "avg_duration_ms": 0,
                "keys": [],
            }
        return {
            "backend": self.backend_name,
            "backend_available": backend_available,
            "backend_error": backend_error,
            "redis_configured": bool(runtime_config["redis_url"]),
            "config": {
                "default_key_max_concurrency": int(runtime_config["default_key_max_concurrency"]),
                "default_cooldown_seconds": int(runtime_config["default_cooldown_seconds"]),
                "foreground_priority_enabled": bool(runtime_config["foreground_priority_enabled"]),
                "background_prefetch_enabled": bool(runtime_config["background_prefetch_enabled"]),
                "background_max_concurrency_ratio": float(runtime_config["background_max_concurrency_ratio"]),
            },
            **snapshot,
        }


_governor_lock = threading.Lock()
_governor: DeepSeekGovernor | None = None


def get_deepseek_governor() -> DeepSeekGovernor:
    global _governor
    runtime_config = load_governance_config()
    backend_name = str(runtime_config["backend"])
    with _governor_lock:
        if _governor is None or _governor.backend_name != backend_name:
            _governor = DeepSeekGovernor(backend_name=backend_name, redis_url=str(runtime_config["redis_url"] or ""))
        return _governor


def get_deepseek_governor_status() -> dict[str, Any]:
    try:
        return get_deepseek_governor().status()
    except Exception as exc:
        runtime_config = load_governance_config()
        return {
            "backend": str(runtime_config["backend"]),
            "backend_available": False,
            "backend_error": str(exc),
            "redis_configured": bool(runtime_config["redis_url"]),
            "global_inflight": 0,
            "foreground_waiting": 0,
            "background_waiting": 0,
            "foreground_inflight": 0,
            "background_inflight": 0,
            "enabled_key_count": 0,
            "total_capacity": 0,
            "recent_429_count": 0,
            "recent_timeout_count": 0,
            "avg_wait_ms": 0,
            "avg_duration_ms": 0,
            "keys": [],
            "config": {
                "default_key_max_concurrency": int(runtime_config["default_key_max_concurrency"]),
                "default_cooldown_seconds": int(runtime_config["default_cooldown_seconds"]),
                "foreground_priority_enabled": bool(runtime_config["foreground_priority_enabled"]),
                "background_prefetch_enabled": bool(runtime_config["background_prefetch_enabled"]),
                "background_max_concurrency_ratio": float(runtime_config["background_max_concurrency_ratio"]),
            },
        }


def normalize_priority_class(value: str | None) -> str:
    normalized = (value or "foreground_interactive").strip()
    return normalized if normalized in PRIORITY_RANK else "foreground_interactive"


def load_governance_config() -> dict[str, Any]:
    bundle = _load_runtime_config_bundle()
    backend = _coerce_choice(
        bundle.get("llm.concurrency.backend"),
        os.getenv("EASEWISE_LLM_CONCURRENCY_BACKEND", "memory"),
        allowed={"memory", "redis"},
    )
    default_max = _coerce_int(
        bundle.get("llm.deepseek.default_key_max_concurrency"),
        os.getenv("EASEWISE_DEEPSEEK_KEY_MAX_CONCURRENCY_DEFAULT", str(DEFAULT_MAX_CONCURRENCY)),
        minimum=1,
        maximum=5000,
    )
    default_cooldown = _coerce_int(
        bundle.get("llm.deepseek.default_cooldown_seconds"),
        os.getenv("EASEWISE_DEEPSEEK_COOLDOWN_SECONDS_DEFAULT", str(DEFAULT_COOLDOWN_SECONDS)),
        minimum=1,
        maximum=3600,
    )
    background_ratio = _coerce_float(
        bundle.get("llm.deepseek.background_max_concurrency_ratio"),
        os.getenv("EASEWISE_DEEPSEEK_BACKGROUND_MAX_CONCURRENCY_RATIO", "0.3"),
        minimum=0.0,
        maximum=0.8,
    )
    return {
        "backend": backend,
        "redis_url": os.getenv("EASEWISE_REDIS_URL", "").strip(),
        "default_key_max_concurrency": default_max,
        "default_cooldown_seconds": default_cooldown,
        "foreground_priority_enabled": _coerce_bool(bundle.get("llm.deepseek.foreground_priority_enabled"), True),
        "background_prefetch_enabled": _coerce_bool(bundle.get("llm.deepseek.background_prefetch_enabled"), True),
        "background_max_concurrency_ratio": background_ratio,
    }


def load_deepseek_keys(
    *,
    model: str | None,
    runtime_config: dict[str, Any] | None = None,
    allow_missing: bool = False,
) -> list[LLMKeyConfig]:
    config = runtime_config or load_governance_config()
    keys: list[LLMKeyConfig] = []
    try:
        from product.backend.api.database import list_enabled_llm_api_keys

        rows = list_enabled_llm_api_keys(provider=DEFAULT_PROVIDER)
    except Exception:
        rows = []

    requested_model = (model or "").strip()
    exact_rows = [row for row in rows if not requested_model or str(row.get("model") or "").strip() == requested_model]
    fallback_rows = [row for row in rows if row not in exact_rows]
    for row in [*exact_rows, *fallback_rows]:
        secret_value = str(row.get("secret_value") or "").strip()
        if not secret_value:
            continue
        keys.append(
            LLMKeyConfig(
                key_id=str(row.get("key_id") or row.get("id") or ""),
                provider=str(row.get("provider") or DEFAULT_PROVIDER),
                model=str(row.get("model") or requested_model or "deepseek-v4-pro"),
                display_name=str(row.get("display_name") or "DeepSeek Key"),
                api_key=secret_value,
                priority=int(row.get("priority") or 100),
                max_concurrency=max(1, int(row.get("max_concurrency") or config["default_key_max_concurrency"])),
                cooldown_seconds=max(1, int(row.get("cooldown_seconds") or config["default_cooldown_seconds"])),
                enabled=bool(row.get("enabled", True)),
                masked_key=str(row.get("masked_key") or ""),
                secret_configured=bool(row.get("secret_configured", True)),
            )
        )

    env_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if env_key:
        env_model = os.getenv("DEEPSEEK_MODEL", requested_model or "deepseek-v4-pro").strip() or requested_model or "deepseek-v4-pro"
        if not requested_model or env_model == requested_model or not keys:
            keys.append(
                LLMKeyConfig(
                    key_id="env:deepseek",
                    provider=DEFAULT_PROVIDER,
                    model=env_model,
                    display_name="DeepSeek 环境变量 Key",
                    api_key=env_key,
                    priority=10_000,
                    max_concurrency=max(1, int(config["default_key_max_concurrency"])),
                    cooldown_seconds=max(1, int(config["default_cooldown_seconds"])),
                    masked_key=_mask_secret(env_key),
                    secret_configured=True,
                )
            )

    unique: dict[str, LLMKeyConfig] = {}
    for key in keys:
        if key.key_id and key.key_id not in unique:
            unique[key.key_id] = key
    sorted_keys = sorted(unique.values(), key=lambda item: (item.priority, item.key_id))
    if not sorted_keys and not allow_missing:
        raise LLMGovernorError("deepseek_api_key_not_configured")
    return sorted_keys


def _record_key_runtime_event(
    *,
    key_id: str,
    last_used_at: str | None = None,
    last_rate_limited_at: str | None = None,
    last_error_message: str | None = None,
) -> None:
    if key_id.startswith("env:"):
        return
    try:
        from product.backend.api.database import update_llm_api_key_runtime_state

        update_llm_api_key_runtime_state(
            key_id=key_id,
            last_used_at=last_used_at,
            last_rate_limited_at=last_rate_limited_at,
            last_error_message=last_error_message,
        )
    except Exception:
        return


def _load_runtime_config_bundle() -> dict[str, Any]:
    try:
        from product.backend.api.runtime_config import resolve_runtime_config_bundle

        return resolve_runtime_config_bundle()
    except Exception:
        return {}


def _coerce_int(value: Any, fallback: Any, *, minimum: int, maximum: int) -> int:
    candidate = value if value is not None else fallback
    try:
        return max(minimum, min(maximum, int(candidate)))
    except (TypeError, ValueError):
        try:
            return max(minimum, min(maximum, int(fallback)))
        except (TypeError, ValueError):
            return minimum


def _coerce_float(value: Any, fallback: Any, *, minimum: float, maximum: float) -> float:
    candidate = value if value is not None else fallback
    try:
        return max(minimum, min(maximum, float(candidate)))
    except (TypeError, ValueError):
        try:
            return max(minimum, min(maximum, float(fallback)))
        except (TypeError, ValueError):
            return minimum


def _coerce_bool(value: Any, fallback: bool) -> bool:
    if value is None:
        return fallback
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    return fallback


def _coerce_choice(value: Any, fallback: Any, *, allowed: set[str]) -> str:
    normalized = str(value if value is not None else fallback).strip().lower()
    return normalized if normalized in allowed else str(fallback).strip().lower()


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _timestamp_to_iso(value: float) -> str | None:
    if value <= 0:
        return None
    return datetime.fromtimestamp(value, tz=timezone.utc).replace(microsecond=0).isoformat()


def _mask_secret(secret_value: str) -> str:
    value = secret_value.strip()
    if len(value) <= 8:
        return f"****{value[-4:]}"
    prefix = value[:3] if value.startswith("sk-") else value[:4]
    return f"{prefix}****{value[-4:]}"
