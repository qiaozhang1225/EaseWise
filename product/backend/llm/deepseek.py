from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterator, Sequence
from urllib import error, request

DEFAULT_BASE_URL = "https://api.deepseek.com"
BETA_BASE_URL = "https://api.deepseek.com/beta"
DEFAULT_MODEL = "deepseek-v4-pro"

Message = dict[str, Any]
ToolHandler = Callable[[dict[str, Any]], Any]


class DeepSeekAPIError(RuntimeError):
    pass


def load_env_file(path: str | os.PathLike[str] = ".env.local", *, override: bool = False) -> None:
    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if override or key not in os.environ:
            os.environ[key] = value


def build_messages(
    *,
    system_prompt: str | None = None,
    user_prompt: str | None = None,
    messages: Sequence[Message] | None = None,
) -> list[Message]:
    output: list[Message] = [dict(message) for message in (messages or [])]
    if system_prompt:
        output.insert(0, {"role": "system", "content": system_prompt})
    if user_prompt:
        output.append({"role": "user", "content": user_prompt})
    return output


@dataclass
class DeepSeekConfig:
    api_key: str
    base_url: str = DEFAULT_BASE_URL
    model: str = DEFAULT_MODEL
    timeout_seconds: float = 45.0
    temperature: float | None = 0.0
    thinking_enabled: bool = True
    reasoning_effort: str | None = "high"
    use_beta_for_strict_tools: bool = True

    @classmethod
    def from_env(cls, env_file: str | os.PathLike[str] | None = ".env.local") -> "DeepSeekConfig":
        if env_file:
            load_env_file(env_file)

        api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
        if not api_key:
            raise DeepSeekAPIError("Missing `DEEPSEEK_API_KEY`. Set it in the environment or `.env.local`.")

        base_url = os.getenv("DEEPSEEK_BASE_URL", DEFAULT_BASE_URL).strip() or DEFAULT_BASE_URL
        model = os.getenv("DEEPSEEK_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL
        timeout_raw = os.getenv("DEEPSEEK_TIMEOUT_SECONDS", "45").strip() or "45"
        temp_raw = os.getenv("DEEPSEEK_TEMPERATURE", "0").strip()
        thinking_raw = os.getenv("DEEPSEEK_THINKING_ENABLED", "true").strip().lower()
        reasoning_effort = os.getenv("DEEPSEEK_REASONING_EFFORT", "high").strip() or None

        temperature: float | None
        if temp_raw.lower() in {"", "none", "null"}:
            temperature = None
        else:
            temperature = float(temp_raw)

        return cls(
            api_key=api_key,
            base_url=base_url,
            model=model,
            timeout_seconds=float(timeout_raw),
            temperature=temperature,
            thinking_enabled=thinking_raw not in {"0", "false", "no", "off"},
            reasoning_effort=reasoning_effort,
        )


@dataclass
class DeepSeekResponse:
    raw: dict[str, Any]
    model: str
    content: str
    reasoning_content: str | None
    tool_calls: list[dict[str, Any]]
    finish_reason: str | None
    usage: dict[str, Any] | None

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "DeepSeekResponse":
        choices = payload.get("choices") or []
        if not choices:
            raise DeepSeekAPIError(f"DeepSeek response has no choices: {payload}")

        choice = choices[0]
        message = choice.get("message") or {}
        return cls(
            raw=payload,
            model=str(payload.get("model") or ""),
            content=str(message.get("content") or ""),
            reasoning_content=message.get("reasoning_content"),
            tool_calls=list(message.get("tool_calls") or []),
            finish_reason=choice.get("finish_reason"),
            usage=payload.get("usage"),
        )

    def json_object(self) -> dict[str, Any]:
        if not self.content.strip():
            raise DeepSeekAPIError("DeepSeek returned empty content; cannot parse JSON.")
        try:
            parsed = json.loads(self.content)
        except json.JSONDecodeError as exc:
            raise DeepSeekAPIError(f"DeepSeek content is not valid JSON: {self.content}") from exc
        if not isinstance(parsed, dict):
            raise DeepSeekAPIError(f"DeepSeek JSON response is not an object: {parsed}")
        return parsed

    def assistant_message(self) -> Message:
        message: Message = {
            "role": "assistant",
            "content": self.content,
        }
        if self.reasoning_content is not None:
            message["reasoning_content"] = self.reasoning_content
        if self.tool_calls:
            message["tool_calls"] = self.tool_calls
        return message


@dataclass
class DeepSeekStreamChunk:
    raw: dict[str, Any]
    content_delta: str = ""
    reasoning_delta: str = ""
    tool_calls_delta: list[dict[str, Any]] = field(default_factory=list)
    finish_reason: str | None = None


@dataclass
class ToolLoopResult:
    final_response: DeepSeekResponse
    messages: list[Message]
    tool_results: list[dict[str, Any]]


class DeepSeekClient:
    def __init__(self, config: DeepSeekConfig) -> None:
        self.config = config

    @classmethod
    def from_env(cls, env_file: str | os.PathLike[str] | None = ".env.local") -> "DeepSeekClient":
        return cls(DeepSeekConfig.from_env(env_file=env_file))

    def chat(
        self,
        messages: Sequence[Message],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        thinking_enabled: bool | None = None,
        reasoning_effort: str | None = None,
        response_format: dict[str, Any] | None = None,
        tools: Sequence[dict[str, Any]] | None = None,
        tool_choice: str | dict[str, Any] | None = None,
        extra_body: dict[str, Any] | None = None,
    ) -> DeepSeekResponse:
        payload = self._build_payload(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            thinking_enabled=thinking_enabled,
            reasoning_effort=reasoning_effort,
            response_format=response_format,
            tools=tools,
            tool_choice=tool_choice,
            extra_body=extra_body,
            stream=False,
        )
        base_url = self._resolve_base_url(tools=tools)
        raw = self._request_json(base_url, payload)
        return DeepSeekResponse.from_payload(raw)

    def stream_chat(
        self,
        messages: Sequence[Message],
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        thinking_enabled: bool | None = None,
        reasoning_effort: str | None = None,
        response_format: dict[str, Any] | None = None,
        tools: Sequence[dict[str, Any]] | None = None,
        tool_choice: str | dict[str, Any] | None = None,
        extra_body: dict[str, Any] | None = None,
    ) -> Iterator[DeepSeekStreamChunk]:
        payload = self._build_payload(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            thinking_enabled=thinking_enabled,
            reasoning_effort=reasoning_effort,
            response_format=response_format,
            tools=tools,
            tool_choice=tool_choice,
            extra_body=extra_body,
            stream=True,
        )
        base_url = self._resolve_base_url(tools=tools)
        yield from self._stream_request(base_url, payload)

    def chat_text(
        self,
        *,
        system_prompt: str | None = None,
        user_prompt: str,
        messages: Sequence[Message] | None = None,
        **kwargs: Any,
    ) -> DeepSeekResponse:
        final_messages = build_messages(system_prompt=system_prompt, user_prompt=user_prompt, messages=messages)
        return self.chat(final_messages, **kwargs)

    def chat_json(
        self,
        *,
        system_prompt: str | None = None,
        user_prompt: str,
        messages: Sequence[Message] | None = None,
        json_example: dict[str, Any] | None = None,
        max_empty_retries: int = 1,
        **kwargs: Any,
    ) -> DeepSeekResponse:
        json_instruction = "Return valid json only. The final answer must be a single json object."
        if json_example is not None:
            json_instruction += f"\nJSON shape example:\n{json.dumps(json_example, ensure_ascii=False, indent=2)}"
        final_system = json_instruction if not system_prompt else f"{system_prompt.rstrip()}\n\n{json_instruction}"
        final_messages = build_messages(system_prompt=final_system, user_prompt=user_prompt, messages=messages)

        for attempt in range(max_empty_retries + 1):
            response = self.chat(
                final_messages,
                response_format={"type": "json_object"},
                **kwargs,
            )
            if response.content.strip():
                return response
            if attempt == max_empty_retries:
                return response
        raise AssertionError("unreachable")

    def run_tool_loop(
        self,
        messages: Sequence[Message],
        *,
        tools: Sequence[dict[str, Any]],
        tool_handlers: dict[str, ToolHandler],
        max_rounds: int = 8,
        model: str | None = None,
        temperature: float | None = None,
        thinking_enabled: bool | None = None,
        reasoning_effort: str | None = None,
        tool_choice: str | dict[str, Any] | None = "auto",
        extra_body: dict[str, Any] | None = None,
    ) -> ToolLoopResult:
        conversation: list[Message] = [dict(message) for message in messages]
        tool_results: list[dict[str, Any]] = []

        for _ in range(max_rounds):
            response = self.chat(
                conversation,
                model=model,
                temperature=temperature,
                thinking_enabled=thinking_enabled,
                reasoning_effort=reasoning_effort,
                tools=tools,
                tool_choice=tool_choice,
                extra_body=extra_body,
            )
            conversation.append(response.assistant_message())
            if not response.tool_calls:
                return ToolLoopResult(final_response=response, messages=conversation, tool_results=tool_results)

            for tool_call in response.tool_calls:
                function = tool_call.get("function") or {}
                tool_name = str(function.get("name") or "")
                if tool_name not in tool_handlers:
                    raise DeepSeekAPIError(f"No tool handler registered for `{tool_name}`.")

                arguments_text = str(function.get("arguments") or "{}").strip() or "{}"
                try:
                    arguments = json.loads(arguments_text)
                except json.JSONDecodeError as exc:
                    raise DeepSeekAPIError(f"Tool `{tool_name}` arguments are not valid JSON: {arguments_text}") from exc

                result = tool_handlers[tool_name](arguments)
                if isinstance(result, str):
                    tool_content = result
                else:
                    tool_content = json.dumps(result, ensure_ascii=False)

                tool_result = {
                    "id": tool_call.get("id"),
                    "name": tool_name,
                    "arguments": arguments,
                    "content": tool_content,
                }
                tool_results.append(tool_result)
                conversation.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.get("id"),
                        "content": tool_content,
                    }
                )

        raise DeepSeekAPIError(f"Tool loop exceeded max_rounds={max_rounds} without reaching a final answer.")

    def _resolve_base_url(self, *, tools: Sequence[dict[str, Any]] | None = None) -> str:
        base_url = (self.config.base_url or DEFAULT_BASE_URL).rstrip("/")
        if self.config.use_beta_for_strict_tools and self._contains_strict_tools(tools):
            return BETA_BASE_URL
        return base_url

    def _contains_strict_tools(self, tools: Sequence[dict[str, Any]] | None) -> bool:
        if not tools:
            return False
        for tool in tools:
            function = tool.get("function") or {}
            if function.get("strict") is True:
                return True
        return False

    def _build_payload(
        self,
        *,
        messages: Sequence[Message],
        model: str | None,
        temperature: float | None,
        max_tokens: int | None,
        thinking_enabled: bool | None,
        reasoning_effort: str | None,
        response_format: dict[str, Any] | None,
        tools: Sequence[dict[str, Any]] | None,
        tool_choice: str | dict[str, Any] | None,
        extra_body: dict[str, Any] | None,
        stream: bool,
    ) -> dict[str, Any]:
        final_model = model or self.config.model
        final_thinking = self.config.thinking_enabled if thinking_enabled is None else thinking_enabled
        final_temperature = self.config.temperature if temperature is None else temperature
        final_reasoning = self.config.reasoning_effort if reasoning_effort is None else reasoning_effort

        payload: dict[str, Any] = {
            "model": final_model,
            "messages": [dict(message) for message in messages],
            "stream": stream,
        }
        payload["thinking"] = {"type": "enabled" if final_thinking else "disabled"}
        if final_thinking and final_reasoning:
            payload["reasoning_effort"] = final_reasoning
        if not final_thinking and final_temperature is not None:
            payload["temperature"] = final_temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if response_format:
            payload["response_format"] = response_format
        if tools:
            payload["tools"] = [dict(tool) for tool in tools]
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice
        if extra_body:
            payload.update(extra_body)
        return payload

    def _request_json(self, base_url: str, payload: dict[str, Any]) -> dict[str, Any]:
        endpoint = f"{base_url.rstrip('/')}/chat/completions"
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = request.Request(
            endpoint,
            data=body,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=self.config.timeout_seconds) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise DeepSeekAPIError(f"DeepSeek HTTP {exc.code}: {detail}") from exc
        except error.URLError as exc:
            raise DeepSeekAPIError(f"DeepSeek network error: {exc.reason}") from exc

    def _stream_request(self, base_url: str, payload: dict[str, Any]) -> Iterator[DeepSeekStreamChunk]:
        endpoint = f"{base_url.rstrip('/')}/chat/completions"
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = request.Request(
            endpoint,
            data=body,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "Accept": "text/event-stream",
            },
            method="POST",
        )

        try:
            response = request.urlopen(req, timeout=self.config.timeout_seconds)
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise DeepSeekAPIError(f"DeepSeek HTTP {exc.code}: {detail}") from exc
        except error.URLError as exc:
            raise DeepSeekAPIError(f"DeepSeek network error: {exc.reason}") from exc

        def iterator() -> Iterator[DeepSeekStreamChunk]:
            try:
                buffer: list[str] = []
                for raw_line in response:
                    line = raw_line.decode("utf-8", errors="replace").rstrip("\r\n")
                    if not line:
                        if not buffer:
                            continue
                        event_data = "\n".join(part[5:].strip() for part in buffer if part.startswith("data:"))
                        buffer.clear()
                        if not event_data or event_data == "[DONE]":
                            continue
                        payload = json.loads(event_data)
                        choices = payload.get("choices") or []
                        choice = choices[0] if choices else {}
                        delta = choice.get("delta") or {}
                        yield DeepSeekStreamChunk(
                            raw=payload,
                            content_delta=str(delta.get("content") or ""),
                            reasoning_delta=str(delta.get("reasoning_content") or ""),
                            tool_calls_delta=list(delta.get("tool_calls") or []),
                            finish_reason=choice.get("finish_reason"),
                        )
                        continue
                    buffer.append(line)
            finally:
                response.close()

        return iterator()
