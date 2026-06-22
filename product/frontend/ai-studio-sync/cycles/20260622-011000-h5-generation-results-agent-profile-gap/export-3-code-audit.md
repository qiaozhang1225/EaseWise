# AI Studio Export 3 Code Audit

Cycle: `20260622-011000-h5-generation-results-agent-profile-gap`

Source zip: `/Users/qiaoz-macmini/Downloads/easewise-vue-sync (3).zip`

SHA256: `163b0b5f462afe2c3fa43ee55d00eafed2fc82f6378b40fd25e9da6f27b3d8e0`

## Summary

The latest AI Studio export made real progress on points mock data by changing `server.ts`, but it did not address the user's latest design-test blockers.

Only two text files changed from the previous export:

- `server.ts`
- `src/components/four-pillars/FourPillarsAnalysis.vue`

No changes were made to:

- `src/components/analysis/Analysis.vue`
- `src/components/ai-agent/AIAgent.vue`
- `src/components/profile/Profile.vue`
- `src/components/auth/AuthModal.vue`
- `src/components/support/ContactServiceModal.vue`

## What Improved

- `server.ts` now defines multiple demo users, points accounts, points ledgers, recharge packages, and 402 responses for insufficient points.
- Phone mock data now includes 12 local aspect keys and uses `wealth`.
- Four Pillars luck-cycle and luck-year endpoints now return richer objects for dayun/liunian summary routes.
- Vue 3 + Vite architecture remains intact.

## User-Tested Problems Still Open

### 1. Phone Review Waiting Flow Sticks

User symptom:

> 手机号测评的过场动画会卡在第6项专项内容预热中，需要重新点击首页再点击测评才能看到结果

Code signal:

- `src/components/analysis/Analysis.vue` did not change in this export.
- The component has deferred-completion logic around `pendingCompletedReview`, `waitingVisualPhase`, and `applyOrDeferCompletedReviewState`.
- The current mock server creates a phone review with `status: "completed"` and `progress_stage: "completed"` immediately.

Likely cause:

The review result is ready, but the waiting UI does not reliably auto-flush the pending completed review into `appState = "result"` in the AI Studio prototype. Navigation away and back forces the component to re-read state, so the result appears.

Next requirement:

When polling returns `completed`, the UI must automatically finish the waiting sequence and switch to result without requiring route/tab navigation. The mock server can still show a short staged preview, but the frontend must not park forever on the last waiting step.

### 2. Four Pillars Results Still Lack Real Mock Data

User symptom:

> 四柱八字评测的结果还是没有mock data，建议你从easewise本地服务器中取一些真实数据过来充实这个mock data，否则我没办法看到前端页面就无法进行设计修改

Code signal:

- `server.ts` returns a handcrafted `baziReview` with simplified `natal_table`, `luck_analysis`, `aspects`, and one short `score_markdown`.
- The local EaseWise SQLite database has real completed Four Pillars records.
- Latest local real record example:
  - database: `product/backend/api/data/app.db`
  - table: `four_pillars_reviews`
  - review id: `35d40e61a3544814b991cefb08d9707a`
  - input: `1989-05-22 08:55`, male, Beijing
  - `score_template_json` length: `366180`
  - top-level keys: `input_profile`, `chart`, `deterministic_facts`, `score_summary`, `product_view`, `product_render`, `product_aspects_render`
  - `product_view` keys include `score`, `score_band`, `input_profile`, `chart`, `chart_display`, `summary`, `deterministic_facts`, `aspects`, `analysis_branches`, `luck_analysis`
  - `product_aspects_render` keys include `wealth`, `personality`, `career`, `love`, `health`, `family_environment`
- Local completed luck-render examples exist in `four_pillars_luck_renders`.
  - Example liunian result keys: `cycle_key`, `year`, `year_ganzhi`, `title`, `year_focus`, `opportunities`, `risks`, `relationship_career_wealth_health_notes`, `action_guidance`, `elements_check`, `generated_at`

Next requirement:

Populate AI Studio `server.ts` Four Pillars mock data from a real local-style payload shape. It does not need the full 366KB JSON, but it must expose enough realistic `product_view`, natal chart, aspects, luck analysis, and rendered copy for the actual front-end cards to appear.

### 3. AI Agent Bottom Gap Is Wrong

User symptom:

> 智能体页面的输入框和底部的导航栏之间有很大空隙，这是不对的

Code signal:

- `src/components/ai-agent/AIAgent.vue` did not change.
- AI Studio version uses `class="pt-4 pb-32 max-w-md mx-auto px-margin-mobile flex flex-col h-[calc(100vh-80px)]"`.
- Local version uses a full-height layout with `h-[100dvh] pb-[84px]`, login gate, localStorage conversation, bottom interaction area, and no oversized gap between input and bottom nav.
- Similarity to local remains `8.19%`.

Next requirement:

Align AI Studio `AIAgent.vue` with the local layout contract: login-gated, localStorage-backed, input docked just above the app bottom navigation, no `pb-32` gap, no direct API-only chat dependency for demo.

### 4. Profile Page Still Drifts From Current Project

User symptom:

> 个人中心和当前项目的状态差距太大了。

Code signal:

- `src/components/profile/Profile.vue` did not change.
- Similarity to local remains `5.23%`.
- AI Studio profile uses "灵台余币", fake preset avatars, inline history tabs, and older fantasy copy.
- Local profile has:
  - avatar upload and nickname edit
  - UID and identity label
  - dark points balance card with `我的积分结存`
  - recharge action with source/return_to payload
  - promotion/system intro entry
  - protected modals for `积分记录` and `评测记录`
  - password editor, feedback, logout confirmation
  - local ledger title mapping and clean empty states
  - references to missing local components `SystemIntro.vue` and `AmbassadorDetail.vue`

Next requirement:

Rebuild the AI Studio profile page toward local current state. If creating new files is unreliable, inline the missing `SystemIntro`/promotion entry enough for visual parity, but do not keep the old profile as-is.

## Account Contract Mismatch

AI Studio's written response and exported code disagree.

Written response claimed:

- `13800138000`: 6000 pt
- `13600136000`: 120 pt
- `13500135000`: 30 pt
- `13900139000`: empty state / 3000 pt

Actual exported `server.ts` has:

- `13800138000`: 20000 pt
- `13600136000`: 80 pt
- `13900139000`: 20 pt low-points account
- `13700137000`: 20000 pt empty-history account
- `13500135000`: not present

Next requirement:

Make the demo account matrix explicit and consistent in code and notes. Recommended next stable set:

- `13800138000 / Easewise123! / 6000+`: full regression with rich history
- `13600136000 / Easewise123! / 120`: can afford base review, then fails unlock/dayun/liunian
- `13500135000 / Easewise123! / 30`: base review insufficient
- `13900139000 / Easewise123! / 3000+`: empty-state high-points account

Aliases for older accounts are optional, but the four accounts above should be the documented test matrix.

## Similarity Snapshot

| file | similarity | status |
|---|---:|---|
| `src/components/analysis/Analysis.vue` | 51.54% | user reports waiting/result transition bug |
| `src/components/four-pillars/FourPillarsAnalysis.vue` | 86.63% | visually close, but mock data from server is too thin |
| `src/components/ai-agent/AIAgent.vue` | 8.19% | still drifted; bottom gap visible |
| `src/components/profile/Profile.vue` | 5.23% | still heavily drifted |

## Recommended Next Step

Generate a narrower prompt that asks AI Studio to:

1. Fix the phone review waiting-to-result transition in `Analysis.vue`.
2. Replace thin Four Pillars mock results with real local-style payloads in `server.ts`.
3. Align `AIAgent.vue` with the local docked layout and login/localStorage behavior.
4. Align `Profile.vue` with the current local profile structure and states.
5. Keep the points work, but fix account documentation/code mismatch.
