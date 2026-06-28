# Personality Output Contract

必须输出 JSON object：
- `aspect_key`: 必须为 `personality`。
- `title`: 一句话标题。
- `content`: 性格主轴、优势和可调整点。
- `risk`: 性格过度时的风险提醒。
- `elements_check`: 必须包含 `日主`、`五行`、`十神`、`合冲刑害`、`喜忌` 五个键。
