# AI Studio Sync Request

Marker: `AISTUDIO-GIT-SYNC-20260621-H5-MOCK-STATE-COVERAGE-FOUR-PILLARS-ANIMATION`

## Objective

请在当前 AI Studio Vue/Vite 原型上做一轮很窄的修复：补齐 mock data 和状态覆盖，让 H5 前端可以真实展示手机号评测、四柱八字、奇门问事/智能体的关键状态。不要做新的大范围视觉重设计。

## Source Hierarchy

- 本地 EaseWise 仓库是业务真相：路由、API 字段、鉴权、积分、校验、状态管理、持久化、支付和真实行为都以本地 Vue 代码为准。
- 最新 AI Studio zip 只是当前原型状态，不是业务真相。
- 本轮 `bundle.md` 是详细交互合约，请按其中的代码证据和 mock 覆盖要求执行。
- 当前项目必须保持 Vue 3 + Vite，AI Studio 默认 React 架构不适用于本项目。

## Current AI Studio Export

当前导出的全局视觉已经比较接近，本轮不要重做 `App.vue`、`Home.vue`、`index.css`、布局导航和全局壳层。

主要问题是：mock 数据和生成状态不够，导致用户无法判断真实前端设计。

已确认的问题：

- 手机号测评 mock 只有少量 completed 数据，不够撑起完整 UI。
- 四柱八字 mock 立即 completed，导致测算动画看起来消失。
- 四柱八字有时提示出生信息不完整，valid demo path 不能落入这个错误状态。
- `FourPillarsAnalysis.vue` 调用了 `sleep(...)`，但最新 AI Studio 文件里缺少 `sleep` 函数。
- 奇门问事/智能体页面有漂移：本地是登录门槛 + localStorage 对话，AI Studio 版本变成直接 API chat。

## Design Task

只做这轮窄修：

1. 修复 `src/components/four-pillars/FourPillarsAnalysis.vue` 缺失的 `sleep(ms)` helper。
2. 不要简化四柱错误映射，恢复本地的 `birth_datetime`、`insufficient_points`、`unlock_points_insufficient`、`module_disabled`、`request_failed`、`review_timeout`、`review_failed` 区分。
3. 大幅扩充 `server.ts` mock data，让预览能覆盖真实 UI 状态。
4. 手机号评测和四柱八字不要 POST 后马上 completed，要通过 detail polling 展示 `queued -> scoring -> rendering -> finalizing -> completed`。
5. 四柱八字等待动画必须可见，正常成功流程至少显示约 2-4 秒。
6. valid demo 四柱输入必须成功完成，不要错误提示出生信息不完整；缺失出生信息只在刻意留空时出现。
7. 如果触碰奇门问事/智能体页面，恢复本地登录门槛和本地持久化对话，不要让它卡在真实 API 生成。

## Mock Data And States

请至少提供三个登录账号：

| Phone | Password | Purpose |
|---|---|---|
| `13800138000` | `Easewise123!` | 正常/高积分账号，带完整历史 |
| `13900139000` | `Easewise123!` | 低积分账号，触发积分不足 |
| `13700137000` | `Easewise123!` | 空历史账号，展示 empty state |

手机号评测必须覆盖：

- completed full report
- processing queued/scoring/rendering/finalizing
- failed
- locked aspects
- unlocked aspects
- aspect unlock success
- unlock insufficient points
- 全部 12 个本地 aspect key：`career`、`wealth`、`love`、`health`、`acad`、`fortune`、`investment`、`travel`、`social`、`family`、`personality`、`fengshui`
- 不要使用 `finance`，本地键名是 `wealth`

四柱八字必须覆盖：

- completed rich report
- processing staged report
- failed report
- low-points create error
- missing birth datetime error
- aspect locked/unlocked
- luck cycle/year: `not_generated`、`processing`、`completed`、`failed/retryable`
- completed luck cycle/year result bodies
- aspects 至少包含：`personality`、`career`、`wealth`、`love`、`health`、`family_environment`

积分流水必须足够判断个人主页与历史记录：

- 充值增加
- 积分领取增加
- 手机号评测扣减
- 手机号维度解锁扣减
- 四柱评测扣减
- 四柱专项解锁扣减
- 大运综评扣减
- 流年单年扣减

## Do Not Change

- 不要转换为 React/TSX/JSX。
- 不要改名或移动本地 Vue 文件结构。
- 不要重写已经对齐的全局视觉壳层。
- 不要改本地 API path、字段名、状态名、鉴权、积分和支付语义。
- 不要把 AI Studio mock 行为当成正式产品逻辑。
- 不要移除本地错误状态、加载状态、空状态和低积分状态。

## Acceptance Checklist

- 项目仍然是 Vue 3 + Vite。
- 没有 `sleep is not defined` 或同类运行错误。
- 三个 demo 账号均可登录。
- 手机号评测能看到生成中状态，并最终展示 12 维度结果。
- 四柱八字能看到等待动画约 2-4 秒，并最终展示完整结果。
- 四柱有效输入不会误报出生信息不完整。
- 低积分账号能触发积分不足 UI。
- 空历史账号能触发个人主页/历史记录 empty UI。
- 个人主页历史和积分流水数据足够判断设计细节。
- 奇门问事/智能体不再卡在生成过程；如修改该页，保持本地登录门槛和 localStorage 会话行为。
- 导出 zip 后可以继续用 Git diff 进行下一轮同步。
