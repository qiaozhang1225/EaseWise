# 四柱八字 DeepSeek Prompt 知识底座专项审查报告

日期：2026-06-29

## 结论摘要

本次审查覆盖四柱八字所有当前可见的 DeepSeek 交互链路：综合评述、综合评述流式输出、12 个专项解锁/流式解锁、大运、流年。

核心结论：

- 综合评述已经明显好于旧版本：现在有独立的 `chart_summary` 知识包、结构化 `summary_highlights` facts，并且普通生成失败会抛错，不会静默返回固定文案。
- 12 个专项仍存在明显知识底座不足：每个专项真正的 `judgement-knowledge.md` 只有约 296-488 个字符，更多内容是表达约束、术语解释、输出合同和 JSON 示例。
- 专项 prompt 还有一个更大的工程风险：`build_aspect_prompts` 直接把整个 package 作为 `locked facts` 传给 DeepSeek，单个样例约 68 万字符，其中大运流年 facts 约 26 万字符以上，专项知识会被巨大事实包淹没。
- 大运和流年同样偏弱：`dayun` 判断知识约 309 字，`liunian` 判断知识约 329 字，事实包相对紧凑，但知识不足，容易让 DeepSeek 使用模型内置命理知识自由发挥。
- explicit knowledge 本身并不空：主文件和盲派补充中有婚恋、财富、健康、刑冲灾煞、墓库、空亡、禄神、五鬼、家庭六亲等内容；问题主要是这些内容没有系统性抽取并注入到 12 专项、大运和流年 prompt。

## DeepSeek 交互清单

| 链路 | `llm_scene` | 入口 | Prompt builder | Knowledge 来源 | Facts 输入 | JSON example | 失败行为 | 审查等级 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 综合评述 | `four_pillars.summary` | `render_summary_from_package` | `build_summary_prompts` | `chart_summary` 专用知识包 | `_summary_prompt_locked_facts` 精简 facts | `chat_json` 不传 example | 抛 `DeepSeekAPIError` | GREEN |
| 综合评述流式 | `four_pillars.summary` | `stream_summary_from_package` | `build_summary_prompts` | 同综合评述 | 同综合评述 | 仅作为流式 JSON 指令 | 抛 `DeepSeekAPIError` | GREEN |
| 专项预生成 | `four_pillars.aspect.{aspect_key}` | `render_aspect_from_package` | `build_aspect_prompts` | shared foundation + 专项小知识包 | 整个 package | 传入泛化 example | 吞异常并返回 `fallback_aspect` | RED |
| 专项流式解锁 | `four_pillars.aspect_unlock.{aspect_key}` | `stream_aspect_from_package` | `build_aspect_prompts` | 同专项预生成 | 整个 package | 手动拼进 system | 抛错，API 失败退款 | RED |
| 大运 | `four_pillars.luck.dayun` | `render_dayun_from_package` | `build_dayun_prompts` | shared foundation + 大运小知识包 | `build_dayun_facts` | 传入泛化 example | 抛错，后台任务失败退款 | YELLOW/RED |
| 流年 | `four_pillars.luck.liunian` | `render_liunian_from_package` | `build_liunian_prompts` | shared foundation + 流年小知识包 | `build_liunian_facts` | 传入泛化 example | 抛错，后台任务失败退款 | YELLOW/RED |

关键代码位置：

- [features/four_pillars/rendering/service.py](/Users/qiaoz-macmini/Projects/EaseWise/features/four_pillars/rendering/service.py:76)
- [features/four_pillars/knowledge/loader.py](/Users/qiaoz-macmini/Projects/EaseWise/features/four_pillars/knowledge/loader.py:30)
- [product/backend/api/handlers.py](/Users/qiaoz-macmini/Projects/EaseWise/product/backend/api/handlers.py:2262)

## Prompt 体量与知识占比

基于样例命盘 `1989-05-22 08:55 男命` 静态导出，不调用 DeepSeek。

| Prompt | system 字符 | user 字符 | knowledge 字符 | 真正 judgement 字符 | facts 字符 | example 字符 | 判断 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 综合评述 | 5,629 | 22,091 | 5,248 | 3,349 | 21,679 | 839 | 知识足够支撑当前综评 |
| 单个专项 | 3,632-3,899 | 685,198 | 3,179-3,446 | 296-488 | 685,059 | 369-374 | 知识薄，facts 过大 |
| 大运 | 3,601 | 1,968 | 3,308 | 309 | 1,898 | 391 | 知识薄，facts 可控 |
| 流年 | 3,726 | 4,247 | 3,430 | 329 | 4,175 | 546 | 知识薄，facts 可控 |

专项 facts 过大的原因是 `build_aspect_prompts` 在 user prompt 中直接 `_dump_json(package)`，其中包含完整 `luck_cycles`、`year_items`、`score_template` 等信息。三个样例盘的 package 大小约 67-68 万字符，`luck_cycles` 单项约 26-27 万字符。

## 12 专项知识完整度

| 维度 | judgement 大小 | 当前状态 | 风险 |
| --- | ---: | --- | --- |
| 性格 `personality` | 325 字 | 有十神性格方向，但缺少从 explicit knowledge 抽出的完整格局/性情规则 | RED |
| 财运 `wealth` | 488 字 | 有正偏财、食伤生财、比劫夺财、财库规则，仍偏摘要 | YELLOW |
| 婚姻 `marriage` | 371 字 | 有夫妻宫、配偶星、食伤/比劫压力，但比 explicit knowledge 婚恋规则少很多 | RED |
| 事业 `career` | 430 字 | 有官杀、印、食伤、比劫与职位规则，仍缺强弱/岁运触发细则 | YELLOW |
| 健康 `health` | 354 字 | 有五行偏枯、七杀、偏印、宫位身体，但缺身体映射和风险触发细则 | RED |
| 运势 `fortune` | 296 字 | 只定义阶段趋势边界，缺大运流年触发知识 | RED |
| 投资 `investment` | 325 字 | 有偏财、印星风控、比劫分财，但缺财富时机和风险触发规则 | RED |
| 人际 `social` | 313 字 | 有五类十神的人际解释，缺合冲刑害和宫位互动规则 | RED |
| 行业 `industry` | 368 字 | 有五行行业表和十神场域，缺喜忌、格局、岗位画像细化 | RED |
| 风水 `fengshui` | 360 字 | 有环境调节和喜忌方向，缺地支环境象意、宅体方位细则 | RED |
| 家庭 `family` | 334 字 | 有年/月/印/财/比劫，缺盲派六亲、兄弟姐妹、父母线索抽取 | RED |
| 格局 `pattern` | 403 字 | 有十神格局现实翻译，但缺 explicit knowledge 中格局层次、制化组合 | YELLOW |

总体判断：12 专项不是“完全没有知识”，但目前只能算小型提示卡，不足以承担 DeepSeek 专项深度评测。它们会引导模型往正确方向走，但深度主要依赖模型内置知识和巨大 facts 自行推理。

## 大运与流年审查

大运和流年的 deterministic facts 是相对可控的：大运 facts 约 1,898 字，流年 facts 约 4,175 字。问题不在 facts 体量，而在知识规则太薄。

当前大运知识只覆盖：

- 原局、大运、现实推进三层合断。
- 天干看外显主题，地支看根气环境。
- 生扶/消耗日主。
- 合冲喜忌。
- 神煞只作辅助标签。

当前流年知识只覆盖：

- 原局、大运、流年三层。
- 流年天干/地支分工。
- 合出喜忌。
- 冲刑害破触发日支、时支。
- 岁运补足三合、三会、三刑。
- 神煞辅助。

缺口：

- 没有系统注入 `explicit-knowledge.md` 中的岁运并临、五鬼运财、禄神、墓库打开、空亡、三刑补齐、风险神煞现实转译等规则。
- JSON example 仍是“这一年适合推进关键事项”“关系备注”等泛化占位，容易诱导输出套话。
- 大运/流年输出契约没有明确要求引用“触发依据 -> 现实影响 -> 行动边界”的结构。

## 运行链路风险

1. 综合评述主生成链路会真实调用 DeepSeek。

   生成失败会抛错并让基础评测失败退款；这条链路不是静默 fallback。

2. 报告详情页可能触发综合评述刷新。

   `_resolve_four_pillars_public_view` 发现旧 summary 需要刷新时，会同步调用 `build_four_pillars_core_render`。这能修复旧 summary，但也意味着用户打开旧报告时可能遇到 DeepSeek 调用失败。

3. 专项缓存缺失不会自动批量调用 DeepSeek。

   `build_four_pillars_product_view` 在没有 `product_aspects_render` 时会用 `fallback_aspect_from_facts` 生成 12 个占位专项。普通非流式解锁要求 `_four_pillars_aspect_detail_ready` 为 true，否则返回 `aspect_not_ready`。

4. 专项流式解锁会真实调用 DeepSeek。

   如果缓存不存在，流式解锁会创建 processing 记录、调用 `stream_four_pillars_aspect_render`，成功后持久化，失败后退款。

5. 如果历史缓存里已经有 fallback 文案，普通解锁会直接把它当成可解锁内容。

   `fallback_aspect_from_facts` 的标题固定为“{维度}：先看自身状态，再看五行流通”，内容固定为“不是单点判断，要结合五行流通、十神主题和现实节奏来看”。这类内容如果曾经被写入 `product_aspects_render`，用户会以为是 DeepSeek 专项结果。

## 整改优先级清单

### P0：先阻断固定文案被当成付费结果

- 识别 `fallback_aspect_from_facts` 形态的历史缓存，普通解锁时不把它当成已生成专项，应返回 `aspect_not_ready` 或引导走流式生成。
- `render_aspect_from_package` 不应吞掉所有异常并静默返回 fallback；至少要给调用方明确的失败状态，避免未来重新启用预生成时污染缓存。
- 专项 prompt 不再传整个 package，改成维度专用 locked facts：chart、day_master、element_counts、ten_god_counts、interactions、empty_branches、tombs、shen_sha summary、aspect_signals、必要的 summary_highlights。只有运势专项可以带精简后的 current/near-term luck facts。

### P1：补齐 12 专项 explicit rule pack

- 从 `explicit-knowledge.md` 和 `blind_explicit_knowledge.md` 为 12 个专项抽取专用 rule pack，每个维度至少覆盖：判断顺序、关键术语、触发条件、现实表现、风险边界、不能写的断语。
- 优先补：婚姻、健康、运势、投资、人际、行业、风水、家庭。这几项当前最容易让 DeepSeek 自由发挥。
- 财运、事业、格局已有方向，但仍要补财富时机、财库/官杀库、制化组合、强弱喜忌和岁运触发。

### P2：补大运和流年知识底座

- 为大运新增 explicit rule pack：原局主轴、大运干支、十神主题、喜忌增强、合冲刑害、墓库开合、空亡、禄神、五鬼、风险神煞、十年行动策略。
- 为流年新增 explicit rule pack：所在大运背景、流年干支触发、岁运并临、三刑/三合/三会补齐、日支/时支触发、关系/事业/财富/健康四类现实落点。
- JSON example 改成空字段或非污染的 schema example，不再写“这一年适合推进关键事项”“一段机会判断”这类套话。

### P3：清理重复约束和 example 污染

- shared foundation 保留为短协议，不再承担“知识底座”的名义。
- 每个 prompt 只保留一次“专业词必须解释”的规则，避免重复占用上下文。
- 删除用户可见文案中的泛化占位例句，保留字段 shape 即可。
- prompt QA 中增加静态阈值：专项 `judgement-knowledge` 不低于 1,500-2,000 字，luck rule pack 不低于 2,000 字，专项 user prompt 不超过合理上限。

## 本次验证

已执行：

- 静态导出最终 prompt：综合评述、12 专项、大运、流年。
- 统计 system/user/example/facts/knowledge 字符量。
- 使用 3 个样例命盘检查 facts 体量差异。
- 运行四柱 prompt readability 单元测试：`python -m unittest features.four_pillars.rendering.tests.test_prompt_readability`，结果 5 tests OK。
- 运行轻量 mock contract 检查：summary 1 个、12 专项、大运、流年均通过现有 validate/public 输出函数。

未执行：

- `pytest` 测试未执行，因为当前 `.venv` 没有安装 `pytest`。
- 未进行真实 DeepSeek smoke。本次审查已经确认知识底座结构性不足，真实 smoke 应放在整改后用于验收。

## 最终判断

之前综合评述的问题已经被局部修正；目前真正需要专项整改的是 12 专项、大运和流年。它们不是完全没有知识，但知识体量和结构明显不足，且专项链路存在“整包 facts 过大 + 示例泛化 + fallback 缓存污染”的组合风险。

下一步应先做 P0，避免固定文案继续被当成付费专项；随后按 P1/P2 把 explicit knowledge 真正抽取进 12 专项、大运和流年的 prompt。
