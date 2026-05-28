# H5 字体复刻规范

本规范只约束手机 H5 用户端前端，不约束后台管理系统。

参考来源是 `/Users/qiaoz-macmini/Downloads/phoneqimen-2.zip` 中的 H5 页面代码：

- `Home.vue`
- `Analysis.vue`
- `AIAgent.vue`
- `Profile.vue`
- `Header.vue`
- `BottomNav.vue`
- `App.vue`

## 核心原则

- H5 默认字体是 `Noto Sans`，用于界面、说明、按钮、输入框、导航和普通正文。
- 国风、术数、结果主视觉使用 `Noto Serif`，包括黄历日期、奇门标题、盘面元素、评分数字、核心断语标题。
- `monospace` 只用于结构化数据：客服联系方式、聊天时间、账单增减值、编号、调试信息。普通积分数字、评分数字、手机号文案不使用等宽字体。
- 不再使用 `font-ui`、`font-brand`、`font-data` 或抽象字号 utility；页面直接使用 Tailwind 原生 `font-sans`、`font-serif`、`font-mono` 和 `text-[xxpx]`，便于和参考稿逐项对齐。
- 不设置全局 `font-variant-numeric: tabular-nums`。

## 字号范围

H5 页面字号应优先落在参考稿已有范围内：

| 字号 | 用途 |
| --- | --- |
| `30px` | 个人页积分主数字 |
| `28px` | 评测结果评分数字 |
| `22px` | 黄历日期、盘面方向位 |
| `20px` | 顶部标题、错误页主标题、智能体主标题 |
| `17px` / `17.5px` | 弹窗标题、个人页昵称、主 CTA 标题 |
| `15px` | 输入框、盘面核心字、专项标题 |
| `13px` | 主要正文、按钮、说明、列表标题 |
| `11px` | 辅助说明、标签、导航文字 |
| `10px` | 极小角标、状态标签、工具卡说明 |
| `8px` | 专项评分小徽标，仅限固定高度标签 |

新增字号前，先确认是否可以复用上述范围。

## 页面映射

- `Home.vue`：黄历日期、宜忌、吉神、彭祖百忌、手机号评测 CTA 标题使用 `font-serif`；toast、按钮、工具卡名称和说明使用 `font-sans`。
- `Analysis.vue`：输入页表单、按钮、确认弹窗正文使用 `font-sans`；评测标题、等待态诗句、结果评分、盘面、断语标题使用 `font-serif`。
- `Analysis.vue` 导出长图：`ctx.font` 必须和页面语义一致。盘面天干地干、门星神、评分、标题用 serif；正文、风险说明、英文副标题用 sans-serif。
- `AIAgent.vue`：聊天正文、输入框、快捷问题使用 `font-sans`；页面主标题可以使用 `font-serif`；时间戳和来源信息使用 `font-mono`。
- `Profile.vue`：昵称、列表、按钮使用 `font-sans`；积分主数字和充值弹窗标题使用 `font-serif`；客服联系方式、账单变动值使用 `font-mono`。
- `Header.vue`：产品/页面标题使用 `font-serif`。
- `BottomNav.vue`：导航文字使用 `font-sans`。

## 禁止项

- 不要把所有数字改成 `font-mono`。
- 不要新增宽泛的“语义字体类”再让组件间接引用。
- 不要把后台管理系统的字体规则混入本规范。
- 不要只改页面 DOM 而忘记 `Analysis.vue` 的导出长图 canvas 字体。
