# Chart Summary Output Contract

必须输出 JSON object，字段如下：

- `title`: 一句判断式标题，直接点出命盘主轴。
- `comprehensive_text`: 用户主文案，一整段综合评述，320-520 个中文字符，不换行。自然串联命格主轴、婚恋、财富、健康、家庭/环境、风险窗口、喜忌策略。
- `overview`: 80-140 字短摘要，用于旧 UI 或分享摘要。
- `risk`: 80-140 字，重点写阶段压力和现实管理。
- `usage_guidance`: 80-140 字，说明如何借力、避坑和发挥优势。
- `key_judgements`: 6-8 个结构化依据；每项含 `key`、`label`、`title`、`content`、`basis`、`level`。每项 `content` 不超过 80 字，`basis` 不超过 60 字。
- `life_risk_windows`: 优先 3 个风险窗口，最多 5 个；每项含 `age_range`、`year_range`、`risk_type`、`trigger`、`guidance`、`level`。`trigger` 和 `guidance` 各不超过 70 字。
- `time_highlights`: 最多 3 个年份/年龄重点；每项含 `year`、`age`、`title`、`content`、`trigger`。`content` 不超过 70 字。
- `favorable_strategy`: 含 `favorable_elements`、`unfavorable_elements`、`supportive_environments`、`avoid_patterns`、`action_guidance`。
- `elements_check`: 必须含 `日主`、`五行`、`十神`、`合冲刑害`、`喜忌`。每项不超过 80 字。

旧报告只有 `title/risk/usage_guidance/elements_check` 时仍兼容；新报告必须尽量完整输出以上字段。

输出控量优先级高于展开细节：知识包用于判断，不要把知识包逐条复述进 JSON。
