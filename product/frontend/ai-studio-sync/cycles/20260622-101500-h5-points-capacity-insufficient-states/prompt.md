# AI Studio Sync Request

Marker: `AISTUDIO-GIT-SYNC-20260622-H5-POINTS-CAPACITY-INSUFFICIENT-STATES`

## Objective

请在当前 EaseWise Vue/Vite H5 原型上做一轮窄修：补齐积分余额、积分流水、充值入口、积分不足错误态和 mock server 行为，让演示既能用高积分账号做全面测试，也能用低积分账号专门测试“积分不足 / 解锁积分不足”。

上一轮 AI Studio 只修了四柱 `.some/year_items` 崩溃，没有执行 mock/state coverage 主任务。这轮必须修改 `server.ts`，不要只改一个 Vue 文件。

## Source Hierarchy

- 本地 EaseWise 仓库是业务真相：路由、API 字段、鉴权、积分、充值、客服场景、错误类型、状态管理都以本地 Vue 代码为准。
- 最新 AI Studio export 只是当前原型状态，不是业务真相。
- 本轮 `bundle.md` 是详细交互合约，请按其中的积分与错误态要求执行。
- 当前项目必须保持 Vue 3 + Vite，不要转换为 React/TSX/JSX。

## Local Frontend Changes

本轮不要求同步新的本地业务改动，只要求让 AI Studio 原型贴近当前本地积分体系和错误态语义。

本地默认积分成本：

- 基础评测：`100`
- 单个专项解锁：`50`

真实值来自 runtime config，AI Studio 可以 mock，但不能改语义。

## Current AI Studio Export

当前全局 H5 壳层已经比较接近，请保留：

- `src/App.vue`
- `src/components/home/Home.vue`
- `src/index.css`
- `src/composables/useEaseWiseApp.ts`
- 底部导航和整体移动端布局

当前仍未完成：

- `server.ts` 没有改
- demo 积分太少，无法做全面测试
- 低积分和空历史账号缺失
- `sleep(ms)` helper 仍缺失
- 手机号 aspect 不完整，且错误使用 `finance` 而不是 `wealth`
- 四柱 mock 数据、等待动画、大运/流年数据不足
- 积分不足提示与当前项目差距很大

## Gap To Close

这轮只关闭积分和状态测试缺口：

1. 增加足够高积分账号，保证全面测试不会被积分不足误挡住。
2. 增加低积分账号，专门触发基础评测积分不足。
3. 增加“可做基础评测但不能解锁”的账号，专门触发专项解锁积分不足。
4. 增加高积分空历史账号，专门看 empty state。
5. 让 `server.ts` 的 mock 行为真实检查余额、扣减积分、追加积分流水。
6. 让积分不足 UI 符合本地项目当前语义。

## Design Task

请按 `bundle.md` 修改当前 AI Studio 项目：

- 首先保留上一轮 `.some/year_items` 防崩溃修复。
- 然后补回 `FourPillarsAnalysis.vue` 缺失的 `sleep(ms)` helper。
- 重点修改 `server.ts`：
  - mock 登录
  - mock points account
  - mock points ledger
  - mock recharge packages
  - phone review create/detail/unlock
  - four pillars create/detail/aspect unlock/luck cycle/luck year
  - 余额不足时返回本地兼容的 `insufficient_points`
- 修正前端不足积分状态，不要做成泛泛的英文 credits 提示。

## Mock Data And States

必须至少有 4 个账号：

| Phone | Password | Balance | Purpose |
|---|---|---:|---|
| `13800138000` | `Easewise123!` | `20000` | 高积分完整测试账号，带完整历史和积分流水 |
| `13900139000` | `Easewise123!` | `20` | 低积分账号，触发基础评测积分不足 |
| `13600136000` | `Easewise123!` | `80` | 解锁不足账号，可做基础评测但不能反复解锁 |
| `13700137000` | `Easewise123!` | `20000` | 空历史账号，展示 empty state |

积分成本 mock：

- `phone_review.base_points_cost = 100`
- `phone_review.aspect_unlock_points_cost = 50`
- `four_pillars.base_points_cost = 100`
- `four_pillars.aspect_unlock_points_cost = 50`
- `four_pillars.luck_cycle_points_cost = 80`
- `four_pillars.luck_year_points_cost = 30`

手机号评测必须覆盖：

- `queued -> scoring -> rendering -> finalizing -> completed`
- completed full report
- failed report
- locked/unlocked aspects
- unlock success
- unlock insufficient points
- 12 个本地 aspect key：`career`、`wealth`、`love`、`health`、`acad`、`fortune`、`investment`、`travel`、`social`、`family`、`personality`、`fengshui`
- 不要使用 `finance`

四柱八字必须覆盖：

- 等待动画约 2-4 秒
- valid demo input 成功完成
- 刻意缺失出生信息时才显示 `birth_datetime`
- 基础评测积分不足
- 专项/大运/流年解锁积分不足
- completed rich report
- failed report
- luck cycle/year: `not_generated`、`processing`、`completed`、`failed/retryable`
- completed luck cycle/year result bodies

## Insufficient Points Copy And Actions

请贴近本地项目，不要使用泛泛的 mock 提示。

手机号基础评测不足：

- error type: `insufficient_points`
- title: `评测积分不足`
- body pattern: `当前手机号评测需要消耗 {requiredPoints} 积分。您当前可用积分为 {userPoints} 分。`
- actions: `返回重新输入`、`前往充值`、`联系客服`
- customer service scene: `points_insufficient`

手机号专项解锁不足：

- error type: `unlock_points_insufficient`
- title: `解锁积分不足`
- body pattern: `解锁单个专项需要消耗 {requiredPoints} 积分。您当前可用积分为 {userPoints} 分。`
- actions: `返回评测结果`、`前往充值`、`联系客服`
- customer service scene: `points_insufficient`

四柱基础评测不足：

- error type: `insufficient_points`
- title: `积分不足`
- body: `当前积分不足，可充值后继续生成四柱评测。`
- actions: `重新填写`、`去充值`

四柱专项/大运/流年解锁不足：

- error type: `unlock_points_insufficient`
- title: `专项解锁积分不足`
- body: `当前积分不足，可充值后继续解锁专项内容。`
- actions: `重新填写`、`去充值`

## Do Not Change

- 不要转换为 React/TSX/JSX。
- 不要改名或移动 Vue 文件结构。
- 不要重写已经对齐的 H5 全局视觉壳层。
- 不要改本地 API path、字段名、状态名、鉴权、积分和支付语义。
- 不要把所有账号都设成无限积分，低积分是测试场景，高积分才是全面回归场景。
- 不要隐藏积分不足错误，必须能稳定触发并展示。
- 不要把 AI Studio mock 行为当成正式产品逻辑。

## Acceptance Checklist

- 项目仍然是 Vue 3 + Vite。
- 下一次导出中 `server.ts` 有实质改动。
- 没有 `sleep is not defined`。
- `13800138000` 可以完整测试手机号、四柱、解锁、个人主页、充值入口，不会被积分不足误挡。
- `13900139000` 能稳定触发基础评测积分不足。
- `13600136000` 能稳定触发专项/大运/流年解锁积分不足。
- `13700137000` 能展示空历史/empty state，且不是因为积分不足。
- 手机号评测展示 12 个本地 aspect key，且使用 `wealth` 不使用 `finance`。
- 四柱等待动画可见，结果数据足够丰富。
- 积分不足文案和按钮符合本地项目语义。
- 个人主页/钱包能看到足够的积分流水。
- 导出 zip 后可以继续用 Git diff 审计。
