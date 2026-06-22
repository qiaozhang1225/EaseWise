# EaseWise AI Studio Bundle: Points Capacity And Insufficient Points States

Cycle: `20260622-101500-h5-points-capacity-insufficient-states`

Repo: `/Users/qiaoz-macmini/Projects/EaseWise`

Frontend root: `product/frontend`

Local git ref: `a9d6be3`

Latest AI Studio export SHA256: `a24f18342acd99153da003fe490beeffda1084734d9c85d046030f299eb49da4`

## Objective

This round must make the AI Studio H5 prototype testable for points-heavy flows and insufficient-points flows.

The previous AI Studio export only patched a Four Pillars `.some` runtime crash. It did not change `server.ts`, did not add enough points, did not add low-points and empty-history accounts, and did not align the insufficient-points UI with the local EaseWise product.

## Source Hierarchy

1. Local EaseWise Vue/Vite frontend is authoritative for route names, component contracts, API fields, auth, validation, points, payment, customer-service scenes, and error-state semantics.
2. Latest AI Studio export is only the current prototype output.
3. This Markdown bundle is the handoff contract for the next AI Studio iteration.
4. Keep Vue 3 + Vite. Do not convert anything to React, TSX, or JSX.

## Current AI Studio State

Keep the already aligned shell:

- `src/App.vue`
- `src/components/home/Home.vue`
- `src/index.css`
- `src/composables/useEaseWiseApp.ts`
- overall H5 layout and bottom navigation

Do not spend this round on a broad visual redesign.

Known latest export gaps:

- `server.ts` did not change in the last round.
- Only one file changed: `src/components/four-pillars/FourPillarsAnalysis.vue`.
- `sleep(ms)` is still missing while `FourPillarsAnalysis.vue` still calls `sleep(...)`.
- Mock review creation still returns `completed` immediately.
- Only `13800138000` exists as a demo account.
- Low-points and empty-history accounts are missing.
- Phone mock aspects are incomplete and still use `finance` instead of local key `wealth`.
- Four Pillars mock aspects and luck-cycle/year result bodies are too thin.
- Insufficient-points UI is not local-equivalent.

## Local Points Semantics To Preserve

Runtime config, not hardcoded design text, is the business source of truth. AI Studio can mock the values, but must keep the same shape and semantics.

Local fallback values:

```ts
// product/frontend/src/config/pricing.ts
export const DEFAULT_BASE_REVIEW_POINTS = 100;
export const DEFAULT_ASPECT_UNLOCK_POINTS = 50;
```

Local runtime config keys include:

- `points.initial_grant`
- `phone_review.base_points_cost`
- `phone_review.aspect_unlock_points_cost`
- `four_pillars.base_points_cost`
- `four_pillars.aspect_unlock_points_cost`
- `four_pillars.luck_cycle_points_cost`
- `four_pillars.luck_year_points_cost`
- `recharge.packages`
- `customer_service.copy.points_insufficient`

Local generic API error copy:

```ts
insufficient_points: '当前积分不足，请充值后继续。'
```

Local customer-service copy default:

```py
"points_insufficient": "当前积分不足时，可添加客服协助确认充值或套餐配置。"
```

## Local Insufficient-Points UI Semantics

Do not show a generic disconnected "not enough credits" state. EaseWise has different insufficient-points situations.

### Phone review base review insufficient

Local error type:

```ts
insufficient_points
```

Local title:

```text
评测积分不足
```

Local body pattern:

```text
当前手机号评测需要消耗 {effectiveBaseReviewPoints} 积分。您当前可用积分为 {userPoints} 分。
```

Local actions:

- primary: `返回重新输入`
- secondary: `前往充值`, navigates to `recharge` with source `insufficient_points`, return_to `phone`, required_points base cost
- support block: uses `customerServiceCopyForScene('points_insufficient')`
- support action: `联系客服`, opens the customer-service modal for scene `points_insufficient`

### Phone aspect unlock insufficient

Local error type:

```ts
unlock_points_insufficient
```

Local title:

```text
解锁积分不足
```

Local body pattern:

```text
解锁单个专项需要消耗 {effectiveAspectUnlockPoints} 积分。您当前可用积分为 {userPoints} 分。
```

Local actions:

- primary: `返回评测结果`
- secondary: `前往充值`, navigates to `recharge` with source `unlock_points_insufficient`, return_to `phone`, required_points aspect cost
- support block/action same as above

### Four Pillars base review insufficient

Local error type:

```ts
insufficient_points
```

Local title:

```text
积分不足
```

Local body:

```text
当前积分不足，可充值后继续生成四柱评测。
```

Local actions:

- `重新填写`
- `去充值`

### Four Pillars aspect/luck unlock insufficient

Local error type:

```ts
unlock_points_insufficient
```

Local title:

```text
专项解锁积分不足
```

Local body:

```text
当前积分不足，可充值后继续解锁专项内容。
```

Local actions:

- `重新填写`
- `去充值`

## Required Demo Accounts

Add or update demo users in `server.ts`. The high-points account must have enough points for a full manual test pass without hitting an accidental insufficient-points wall.

| Phone | Password | Balance | Purpose |
|---|---|---:|---|
| `13800138000` | `Easewise123!` | `20000` | Full regression account with rich history and enough points for every H5 flow |
| `13900139000` | `Easewise123!` | `20` | Low-points account for base review insufficient-points flows |
| `13600136000` | `Easewise123!` | `80` | Unlock-insufficient account: can afford one base review but cannot afford repeated aspect/luck unlocks |
| `13700137000` | `Easewise123!` | `20000` | Empty-history account: plenty of points, no history, used for empty-state UI |

Do not make all users low balance. Low balance is a test case, not the default demo condition.

## Required Points Ledger Mock Data

For `13800138000`, provide enough points ledger rows to judge the profile and wallet UI:

- initial grant
- recharge package purchase
- points claim grant
- phone base review deduction
- phone aspect unlock deduction
- Four Pillars base review deduction
- Four Pillars aspect unlock deduction
- Four Pillars luck-cycle deduction
- Four Pillars luck-year deduction
- at least one failed/voided or pending payment-like record if the prototype supports it

For `13900139000`, provide a tiny balance and a short ledger explaining why:

- initial grant or recharge
- one or more deductions
- final balance below base review cost

For `13600136000`, provide a balance that can pass base review but fails unlock:

- balance after base review should be below aspect/luck unlock cost
- this account must exercise `unlock_points_insufficient`, not only base `insufficient_points`

For `13700137000`, keep ledger/history empty or nearly empty while keeping enough balance for testing an empty state without a points blocker.

## Required Server Behavior

Modify `server.ts`. The previous AI Studio export stopped before touching it. Do not stop after editing `FourPillarsAnalysis.vue`.

Required behavior:

- login works for all four demo accounts above
- points account endpoint returns the current mock balance and frozen balance
- points ledger endpoint returns meaningful rows per account
- phone review create checks balance against `phone_review.base_points_cost`
- phone aspect unlock checks balance against `phone_review.aspect_unlock_points_cost`
- Four Pillars create checks balance against `four_pillars.base_points_cost`
- Four Pillars aspect unlock checks balance against `four_pillars.aspect_unlock_points_cost`
- luck cycle checks balance against `four_pillars.luck_cycle_points_cost`
- luck year checks balance against `four_pillars.luck_year_points_cost`
- insufficient balance responses must use local-compatible detail values, especially `insufficient_points`
- unlock insufficiency must surface in the frontend as `unlock_points_insufficient`
- successful mock operations should deduct points in the mock state and append ledger rows when practical

Use these mock costs unless the existing AI Studio runtime-config mock already exposes equivalent values:

```ts
phone_review.base_points_cost = 100
phone_review.aspect_unlock_points_cost = 50
four_pillars.base_points_cost = 100
four_pillars.aspect_unlock_points_cost = 50
four_pillars.luck_cycle_points_cost = 80
four_pillars.luck_year_points_cost = 30
```

## Required Phone Review Coverage

The full regression account must be able to complete and inspect:

- staged generation: `queued -> scoring -> rendering -> finalizing -> completed`
- completed full report
- failed report
- locked aspects
- unlocked aspects
- unlock success
- unlock insufficient points
- all 12 local aspect keys:
  - `career`
  - `wealth`
  - `love`
  - `health`
  - `acad`
  - `fortune`
  - `investment`
  - `travel`
  - `social`
  - `family`
  - `personality`
  - `fengshui`

Do not use `finance`. The local key is `wealth`.

## Required Four Pillars Coverage

First keep the `.some/year_items` guard from the previous export, then add the missing `sleep(ms)` helper:

```ts
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}
```

The Four Pillars flow must cover:

- visible waiting animation for about 2 to 4 seconds
- valid demo input completes successfully
- intentionally missing birth datetime shows `birth_datetime`
- low-points account triggers base `insufficient_points`
- unlock-insufficient account triggers `unlock_points_insufficient`
- completed rich report
- failed report
- aspect locked/unlocked states
- luck cycle/year states: `not_generated`, `processing`, `completed`, `failed/retryable`
- completed luck cycle/year result bodies with non-empty copy
- aspects at least:
  - `personality`
  - `career`
  - `wealth`
  - `love`
  - `health`
  - `family_environment`

Do not simplify local error mapping. Preserve these distinctions:

- `birth_datetime`
- `insufficient_points`
- `unlock_points_insufficient`
- `module_disabled`
- `request_failed`
- `review_timeout`
- `review_failed`

## Recharge And Customer Service

The insufficient-points state must make sense in the current product:

- The user should see the required points and current available balance when the local component supports it.
- There must be a clear path to `recharge`.
- Customer-service copy must use the `points_insufficient` scene, not generic review support text.
- Recharge packages should look realistic enough for testing, with enough total points to restore the full regression account if a tester chooses a package.
- Do not invent payment success as business truth. If payment is mocked, mark it as prototype-only.

## Do Not Change

- Do not convert to React, TSX, or JSX.
- Do not rename or move Vue files.
- Do not rewrite the aligned H5 shell.
- Do not replace local API paths or payload field names.
- Do not remove existing loading, empty, error, disabled, auth, payment, and success states.
- Do not treat AI Studio mock logic as production backend logic.
- Do not hide insufficient-points errors by giving every account unlimited points.

## Acceptance Checklist

- Project remains Vue 3 + Vite.
- `server.ts` changes are present in the next export.
- No `sleep is not defined` runtime path remains.
- `13800138000` can run broad H5 regression without accidental points blockage.
- `13900139000` triggers base review insufficient-points flows.
- `13600136000` triggers unlock insufficient-points flows.
- `13700137000` shows empty-history UI without being blocked by points.
- Phone review shows staged generation and all 12 local aspect keys.
- Four Pillars shows visible waiting animation and rich result data.
- Four Pillars valid demo input does not incorrectly show missing birth info.
- Insufficient-points UI copy and actions match local semantics.
- Profile/wallet has enough ledger data to judge design.
- Export zip can be diffed against the previous export for verification.
