# AI Studio Sync Request

Marker: `AISTUDIO-GIT-SYNC-20260622-H5-GENERATION-RESULTS-AGENT-PROFILE-GAP`

## Objective

请基于当前 EaseWise Vue 3 + Vite 原型继续做一轮窄修，解决我在最新演示中实际测出来的 4 个问题：

1. 手机号测评过场动画会卡在第 6 项“专项内容预热中”，必须点首页再回来才看到结果。
2. 四柱八字评测结果仍然缺少真实 mock data，前端结果页无法充分展示，无法继续做设计修改。
3. 智能体页面输入框和底部导航栏之间有很大空隙。
4. 个人中心和当前本地项目状态差距太大。

上一轮 points/server.ts 工作可以保留，但这轮必须改 `Analysis.vue`、`AIAgent.vue`、`Profile.vue`，不能只继续改 `server.ts`。

## Source Hierarchy

- 本地 EaseWise 仓库是业务真相：路由、API 字段、鉴权、积分、个人中心、智能体布局、状态管理、错误态都以本地 Vue 代码为准。
- 本地 SQLite 数据可以作为四柱八字真实 mock 结构参考。
- 最新 AI Studio export 只是当前原型状态，不是业务真相。
- 本轮 `bundle.md` 是详细交互合约，请按其中的四个问题逐项执行。
- 当前项目必须保持 Vue 3 + Vite，不要转换为 React/TSX/JSX。

## Local Frontend Changes

本轮不是同步新的本地业务开发，而是修复 AI Studio 原型与本地当前状态的差距。

关键本地参照：

- `product/frontend/src/components/analysis/Analysis.vue`
- `product/frontend/src/components/four-pillars/FourPillarsAnalysis.vue`
- `product/frontend/src/components/ai-agent/AIAgent.vue`
- `product/frontend/src/components/profile/Profile.vue`
- `product/backend/api/data/app.db`

## Current AI Studio Export

最新 export `(3)` 只改了：

- `server.ts`
- `src/components/four-pillars/FourPillarsAnalysis.vue`

没有改：

- `src/components/analysis/Analysis.vue`
- `src/components/ai-agent/AIAgent.vue`
- `src/components/profile/Profile.vue`

所以用户测到的问题仍然存在。

## Gap To Close

### 1. Phone review waiting-to-result bug

当前手机号评测完成后不能停留在第 6 项等待动画。

请修复 `Analysis.vue`：

- 当 polling 或 mock response 返回 `status: "completed"` 时，必须自动进入 result 页面。
- 不允许依赖用户切到首页再切回来触发刷新。
- 如果保留等待动画，completed 后要短暂收尾并自动 flush `pendingCompletedReview`。
- 清理 waiting timers。
- 添加兜底：`pendingCompletedReview` 不可永久停留。

### 2. Four Pillars real mock data

当前 `server.ts` 的四柱结果太薄，页面看不到真实结果结构。

请从本地真实数据结构补 mock。参考本地 SQLite：

- DB: `product/backend/api/data/app.db`
- table: `four_pillars_reviews`
- example review id: `35d40e61a3544814b991cefb08d9707a`
- example input: male, `1989-05-22`, `08:55`, Beijing
- real `score_template_json` top-level keys:
  - `input_profile`
  - `chart`
  - `deterministic_facts`
  - `score_summary`
  - `product_view`
  - `product_render`
  - `product_aspects_render`
- `product_aspects_render` must include:
  - `wealth`
  - `personality`
  - `career`
  - `love`
  - `health`
  - `family_environment`

请在 `server.ts` 里构造一个足够丰富的 local-style Bazi result，不需要复制完整 366KB，但必须让前端结果页展示出：

- 四柱 natal table
- 农历/公历/四柱干支/日主
- 五行比例和十神/藏干
- 总评摘要
- 六个专项结果
- 大运 cycles 和流年 year_items
- completed dayun/liunian render bodies
- 历史记录里的 completed Bazi result

### 3. AI Agent bottom layout gap

当前 AI Studio `AIAgent.vue` 有类似：

```vue
class="pt-4 pb-32 max-w-md mx-auto px-margin-mobile flex flex-col h-[calc(100vh-80px)]"
```

这会造成输入框和底部导航之间空隙过大。

请修复 `AIAgent.vue`：

- 不要使用 `pb-32` 这种过大底部间距。
- 输入框要贴近底部导航上方，只保留正常 safe spacing。
- 参考本地：`h-[100dvh] pb-[84px]` 的页面模型。
- 保留/恢复本地行为：登录门槛、localStorage 对话、清空对话、横向快捷问题。
- 不要让智能体依赖真实 AI API 才能演示，mock 回复即可。

### 4. Profile page parity

当前 AI Studio `Profile.vue` 和本地差距太大。

请重构/对齐 `Profile.vue`，向本地当前状态靠拢：

- 头像上传/昵称编辑
- UID 和身份标签
- 黑色积分卡：`我的积分结存`
- `去充值` 按钮，导航 payload 包含 `{ source: 'profile', return_to: 'profile' }`
- `合伙与推广说明书`
- `积分记录`
- `评测记录`
- `修改密码`
- `反馈问题`
- 登出确认
- 积分记录 modal
- 评测记录 modal
- empty state

如果 AI Studio 能稳定新建文件，请补：

- `src/components/profile/SystemIntro.vue`
- `src/components/profile/AmbassadorDetail.vue`

如果不能稳定新建文件，请先在 `Profile.vue` 内联足够的推广说明入口/弹层，保证可见状态接近本地。

## Mock Data And States

请修正 demo 账号矩阵。当前 AI Studio 文字说明和实际代码不一致。

必须保证这 4 个账号在代码和说明中一致：

| Phone | Password | Points | Purpose |
|---|---|---:|---|
| `13800138000` | `Easewise123!` | `6000+` | 高积分全量回归账号，带手机号、四柱、积分流水、个人中心历史 |
| `13600136000` | `Easewise123!` | `120` | 可做基础评测，但会触发专项/大运/流年解锁积分不足 |
| `13500135000` | `Easewise123!` | `30` | 立即触发手机号/四柱基础评测积分不足 |
| `13900139000` | `Easewise123!` | `3000+` | 高积分空历史账号，用于测试 empty state 和首次生成 |

四柱 mock 至少提供：

- 一个 `13800138000` 的 rich completed history
- 一个新建四柱评测后的 rich completed result
- 一个 dayun completed render
- 一个 liunian completed render
- `not_generated`、`processing`、`completed`、`failed/retryable` 的 luck states

手机号 mock 必须保证：

- completed 后自动进结果页
- 不会卡在第 6 项等待动画
- 12 个 aspect key 仍然完整，使用 `wealth`，不要使用 `finance`

## Do Not Change

- 不要转换为 React/TSX/JSX。
- 不要重写已经对齐的 H5 壳层和底部导航。
- 不要删除上一轮 points/server.ts 的有效成果。
- 不要让所有账号都变成高积分。
- 不要隐藏积分不足状态。
- 不要保留当前 AI Agent 的大底部空隙。
- 不要保留当前旧版 Profile 页面不动。
- 不要用空壳四柱 mock data 糊弄结果页。

## Acceptance Checklist

- 项目仍然是 Vue 3 + Vite。
- 下一次导出至少改动 `server.ts`、`Analysis.vue`、`AIAgent.vue`、`Profile.vue`。
- 手机号测评会自动从等待页进入结果页，不需要切首页再回来。
- 四柱八字结果页有足够丰富的 local-style mock data，可用于设计判断。
- 智能体输入框和底部导航之间没有异常大空隙。
- 智能体保持登录门槛、localStorage 对话和 mock 可演示回复。
- 个人中心接近当前本地项目状态，而不是旧版幻想风格页面。
- 4 个 demo 账号在代码和说明中完全一致。
- 导出 zip 后可以继续用 Git diff 审计。
