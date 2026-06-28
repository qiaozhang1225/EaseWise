# Health Output Contract

必须输出 JSON object：
- `aspect_key`: 必须为 `health`。
- `title`: 一句话标题。
- `content`: 体质倾向、压力来源和保养建议。
- `risk`: 需要留意的健康风险，但不得诊断。
- `elements_check`: 必须包含 `日主`、`五行`、`十神`、`合冲刑害`、`喜忌` 五个键。
