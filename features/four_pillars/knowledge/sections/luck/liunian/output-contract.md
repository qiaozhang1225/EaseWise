# Liunian Output Contract

必须输出 JSON object：
- `cycle_key`: 必须等于 locked facts 中的 `selected_cycle.cycle_key`。
- `year`: 必须等于 locked facts 中的 `selected_year.year`。
- `year_ganzhi`: 必须等于 locked facts 中的 `selected_year.ganzhi`。
- `title`
- `year_focus`
- `opportunities`
- `risks`
- `relationship_career_wealth_health_notes`
- `action_guidance`
- `elements_check`: 必须包含 `原局`、`大运`、`流年`、`十神`、`五行`、`合冲刑害`、`喜忌`。

主文案字段写法：
- `year_focus` 只写这一年的核心触发主题。
- `opportunities` 只写当年可推进的机会、助力、资源和顺势点。
- `risks` 只写当年容易放大的风险、消耗、冲突和需要避开的现实问题。
- `action_guidance` 只写当年具体行动建议。
- 上述字段都写成自然段，不要使用 `1、2、3`、`①②③`、项目符号或小标题列表。
- 每个字段 1 段，最多 2 句；不要在绿色机会段和红色风险段里重复同一套编号结构。
