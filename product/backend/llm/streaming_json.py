from __future__ import annotations

import json
from typing import Any

from .deepseek import DeepSeekAPIError


def build_json_stream_instruction(json_example: dict[str, Any] | None) -> str:
    instruction = "Return valid json only. The final answer must be a single json object."
    if json_example:
        instruction += f"\nJSON shape example:\n{json.dumps(json_example, ensure_ascii=False, indent=2)}"
    return instruction


def loads_streamed_json_object(raw_content: str) -> dict[str, Any]:
    text = raw_content.strip()
    if not text:
        raise DeepSeekAPIError("DeepSeek returned empty content; cannot parse JSON.")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise DeepSeekAPIError(f"DeepSeek content is not valid JSON: {text}") from exc
    if not isinstance(parsed, dict):
        raise DeepSeekAPIError(f"DeepSeek JSON response is not an object: {parsed}")
    return parsed


def extract_partial_json_string_field(raw_content: str, field: str) -> str | None:
    key = json.dumps(field, ensure_ascii=False)
    key_index = raw_content.find(key)
    if key_index < 0:
        return None
    colon_index = raw_content.find(":", key_index + len(key))
    if colon_index < 0:
        return None
    value_index = colon_index + 1
    while value_index < len(raw_content) and raw_content[value_index].isspace():
        value_index += 1
    if value_index >= len(raw_content) or raw_content[value_index] != '"':
        return None

    chars: list[str] = []
    index = value_index + 1
    while index < len(raw_content):
        char = raw_content[index]
        if char == '"':
            return "".join(chars)
        if char != "\\":
            chars.append(char)
            index += 1
            continue

        if index + 1 >= len(raw_content):
            break
        escaped = raw_content[index + 1]
        if escaped == "u":
            hex_text = raw_content[index + 2:index + 6]
            if len(hex_text) < 4:
                break
            try:
                chars.append(chr(int(hex_text, 16)))
            except ValueError:
                chars.append("\\u" + hex_text)
            index += 6
            continue
        chars.append(
            {
                '"': '"',
                "\\": "\\",
                "/": "/",
                "b": "\b",
                "f": "\f",
                "n": "\n",
                "r": "\r",
                "t": "\t",
            }.get(escaped, escaped)
        )
        index += 2
    return "".join(chars)
