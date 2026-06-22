# Phone Summary Output Contract

## Required fields

When rendered as structured output, keep these fields:

- `title`
- `risk`
- `usage_guidance`
- `elements_check`

## Contract rule

这 4 个字段分别对应：

- `title`
  - 一句话概括这个手机号
- `risk`
  - 一段话，讲清楚号码暴露出的核心问题
- `usage_guidance`
  - 一段话，把命中的盘面结果综合成最终使用状态
- `elements_check`
  - 一个结构化对象，分别写出对 `宫`、`门`、`神`、`星`、`天干/地干`、`特殊组合`、`四害` 的判断

## Hard rules

- `risk` 和 `usage_guidance` 都必须是完整段落，不要拆成项目符号
- `risk` 和 `usage_guidance` 必须优先写用户能核实的现实表现、具体场景和使用建议，不要连续堆叠专业术语
- 如果使用 `空亡 / 门迫 / 入墓 / 击刑 / 特殊组合 / 四害` 等术语，必须同时写出它在现实里怎么表现
- `elements_check` 是结构化判断层，可以直写每一层的判断，但不要写来源痕迹
- `elements_check` 每项都要写成“专业层 + 现实含义”，不要只写标签
- 不要在最终输出里出现来源痕迹
- 不要在最终输出里出现内部检查层字段名
- 不要把过程感写成结果感

## Minimum quality bar

用户读完以后，至少应该知道：

- 这组号码整体是什么调性
- 最大问题是什么
- 现实里更像什么状态
- 应该怎么使用才更贴近这组号码的结构
