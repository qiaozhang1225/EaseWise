# EaseWise AI Studio Bundle: Generation Results, Agent Layout, And Profile Parity

Cycle: `20260622-011000-h5-generation-results-agent-profile-gap`

Repo: `/Users/qiaoz-macmini/Projects/EaseWise`

Frontend root: `product/frontend`

Local git ref: `a9d6be3`

Latest AI Studio export: `/Users/qiaoz-macmini/Downloads/easewise-vue-sync (3).zip`

Latest AI Studio export SHA256: `163b0b5f462afe2c3fa43ee55d00eafed2fc82f6378b40fd25e9da6f27b3d8e0`

## Objective

Fix the four issues found during manual testing of the latest AI Studio prototype:

1. Phone review waiting animation gets stuck on the 6th step and only shows the result after leaving and returning.
2. Four Pillars result pages still lack rich mock data, so the real UI cannot be judged or redesigned.
3. AI Agent input area has a large incorrect gap above the bottom navigation.
4. Profile page remains far away from the current local project state.

This is a targeted gap iteration. Do not redesign the whole app shell.

## Source Hierarchy

1. Local EaseWise Vue/Vite frontend is authoritative for route names, state handling, component contracts, profile layout, AI Agent layout, auth, points, and error semantics.
2. Local SQLite data can be used as realistic mock-data evidence for Four Pillars and phone review result shape.
3. Latest AI Studio export is only the current prototype output.
4. This Markdown bundle is the handoff contract for the next AI Studio iteration.
5. Keep Vue 3 + Vite. Do not convert to React, TSX, JSX, or a different project structure.

## Latest AI Studio Export Summary

AI Studio export `(3)` changed only:

- `server.ts`
- `src/components/four-pillars/FourPillarsAnalysis.vue`

It did not change:

- `src/components/analysis/Analysis.vue`
- `src/components/ai-agent/AIAgent.vue`
- `src/components/profile/Profile.vue`
- `src/components/auth/AuthModal.vue`
- `src/components/support/ContactServiceModal.vue`

The points work is directionally useful, but the latest manual test found the four issues above.

## Issue 1: Phone Review Waiting Flow Gets Stuck

User-tested symptom:

```text
手机号测评的过场动画会卡在第6项专项内容预热中，需要重新点击首页再点击测评才能看到结果
```

Current code signal:

- `Analysis.vue` did not change in export `(3)`.
- `server.ts` creates phone reviews as immediately completed:

```ts
status: "completed",
progress_stage: "completed",
progress_message: "智能推论完成"
```

- `Analysis.vue` has deferred-completion logic:
  - `pendingCompletedReview`
  - `waitingVisualPhase`
  - `isWaitingFinalPhaseReady`
  - `applyOrDeferCompletedReviewState`

Required fix:

- When polling returns a completed review, the UI must automatically move from `waiting` to `result`.
- It must not require navigating to Home and then back to the review page.
- If a final waiting animation is desired, make it deterministic and short: once `completed` is known, either:
  - immediately call `applyCompletedReviewState`, or
  - set `waitingVisualPhase` to the final index and flush `pendingCompletedReview` on the next tick/timer.
- Clear waiting timers after result display.
- Keep the existing local result UI and voice/autoplay behavior intact.
- Add a guard so the completed review cannot remain in `pendingCompletedReview` forever.

Acceptance for this issue:

- Start a phone review with high-points account.
- The waiting screen may show briefly.
- It must land on the result page automatically without tab navigation.
- No permanent "专项内容预热中" / 6th-step stuck state.

## Issue 2: Four Pillars Needs Real Local-Style Mock Data

User-tested symptom:

```text
四柱八字评测的结果还是没有mock data，建议你从easewise本地服务器中取一些真实数据过来充实这个mock data，否则我没办法看到前端页面就无法进行设计修改
```

Current AI Studio `server.ts` creates a simplified `baziReview`. It is not enough to expose the actual Four Pillars page states.

Use local data shape as evidence. Local SQLite has completed real Four Pillars records:

- Database: `product/backend/api/data/app.db`
- Table: `four_pillars_reviews`
- Example review id: `35d40e61a3544814b991cefb08d9707a`
- Input: male, `1989-05-22`, `08:55`, `Asia/Shanghai`, Beijing
- `score_template_json` length: `366180`
- Top-level keys:
  - `input_profile`
  - `chart`
  - `deterministic_facts`
  - `score_summary`
  - `product_view`
  - `product_render`
  - `product_aspects_render`
- `chart` keys include:
  - `solar_datetime`
  - `lunar_date`
  - `lunar_full_text`
  - `year_ganzhi`
  - `month_ganzhi`
  - `day_ganzhi`
  - `hour_ganzhi`
  - `day_master`
  - `day_master_element`
  - `pillars`
  - `hidden_ten_gods`
  - `ba_zi_wuxing`
  - `ba_zi_na_yin`
- `product_view` keys include:
  - `score`
  - `score_band`
  - `input_profile`
  - `chart`
  - `chart_display`
  - `summary`
  - `deterministic_facts`
  - `aspects`
  - `analysis_branches`
  - `luck_analysis`
- `product_aspects_render` keys include:
  - `wealth`
  - `personality`
  - `career`
  - `love`
  - `health`
  - `family_environment`

Local completed luck-render records also exist:

- Table: `four_pillars_luck_renders`
- Example liunian result keys:
  - `cycle_key`
  - `year`
  - `year_ganzhi`
  - `title`
  - `year_focus`
  - `opportunities`
  - `risks`
  - `relationship_career_wealth_health_notes`
  - `action_guidance`
  - `elements_check`
  - `generated_at`

Required fix:

- Replace the thin `baziReview` mock in `server.ts` with a local-style rich mock result.
- It does not need to copy the full 366KB JSON, but it must include enough realistic nested data for the current frontend cards to render:
  - four pillars natal table
  - lunar/full date text
  - day master and element summary
  - ten-god/hidden-stem details
  - score band and score summary
  - `product_view.summary`
  - `product_view.aspects`
  - `product_render.summary`
  - `product_aspects_render` for six local aspects
  - `luck_analysis.cycles[].year_items[]`
  - completed dayun and liunian render bodies
- Seed at least one rich completed Four Pillars history item for `13800138000`.
- New Four Pillars review creation should also return a rich completed result after the visible waiting flow, not an empty shell.
- Keep the `.some/year_items` guard and `sleep(ms)` helper.

Acceptance for this issue:

- Login as `13800138000`.
- Open 四柱八字 history and/or create a valid new Bazi review.
- The result page must show actual natal table, summary, aspect cards, luck-cycle data, and year/cycle rendered text.
- It must not look empty or generic.

## Issue 3: AI Agent Bottom Gap

User-tested symptom:

```text
智能体页面的输入框和底部的导航栏之间有很大空隙，这是不对的
```

Current AI Studio code:

```vue
<div class="pt-4 pb-32 max-w-md mx-auto px-margin-mobile flex flex-col h-[calc(100vh-80px)] text-left">
```

This creates too much bottom padding and the input area floats too far above the app bottom nav.

Local layout contract:

- Full-height H5 page: `h-[100dvh]`
- Bottom nav reserved space: about `pb-[84px]`
- Input docked directly above bottom interaction area/bottom nav
- No `pb-32` gap
- Login-gated AI Agent, not public direct chat
- Conversation persisted to `localStorage`

Required fix:

- Update `src/components/ai-agent/AIAgent.vue`.
- Align it with the local page model:
  - login gate before active chat
  - `localStorage` conversation persistence
  - input bar docked near the bottom, just above the nav
  - quick query chips horizontally scrollable
  - clear chat action
  - no direct API-only dependency that blocks the demo if backend AI chat is unavailable
- Remove or replace `pb-32`.
- Do not let the input overlap the bottom nav.
- Do not leave a large blank gap between input and bottom nav.

Acceptance for this issue:

- On mobile-width preview, the AI Agent input sits visually close to the bottom nav with normal safe spacing.
- There is no large empty vertical band under the input.
- Chat remains usable after several messages.

## Issue 4: Profile Page Still Far From Local Current State

User-tested symptom:

```text
个人中心和当前项目的状态差距太大了。
```

Current AI Studio status:

- `Profile.vue` did not change in export `(3)`.
- Similarity to local `Profile.vue` remains about `5.23%`.
- AI Studio profile still uses old/fantasy terms such as `灵台余币`, preset-avatar strips, inline history tabs, and broad old layout.

Local profile state to align toward:

- `product/frontend/src/components/profile/Profile.vue`
- local current profile includes:
  - avatar upload button
  - nickname edit modal
  - UID display
  - identity label
  - dark points card with `我的积分结存`
  - `去充值` button using `navigate-to-tab('recharge', { source: 'profile', return_to: 'profile' })`
  - promotion/system intro entry
  - list-style actions:
    - `合伙与推广说明书`
    - `积分记录`
    - `评测记录`
    - `修改密码`
    - `反馈问题`
  - protected modal for points ledger
  - protected modal for report history
  - feedback modal
  - logout confirm modal
  - clean empty states for ledger/history
- Local profile imports extra files:
  - `SystemIntro.vue`
  - `AmbassadorDetail.vue`

Required fix:

- Update `src/components/profile/Profile.vue`.
- If creating new files in AI Studio is reliable, add:
  - `src/components/profile/SystemIntro.vue`
  - `src/components/profile/AmbassadorDetail.vue`
- If creating new files is unreliable, inline enough of the promotion/system intro entry in `Profile.vue` so the visible profile matches the local current shape.
- Remove old profile-only UI that does not exist locally, especially preset-avatar strips and old inline tabbed history layout.
- Preserve local state names and event contracts:
  - `state.points`
  - `state.pointsLedger`
  - `state.reviewHistory`
  - `state.fourPillarsHistory`
  - `requestRegisteredUser`
  - `refreshPointsLedger`
  - `refreshReviewHistory`
  - `refreshFourPillarsHistory`
  - `navigate-to-tab`

Acceptance for this issue:

- Profile first screen feels like current local EaseWise, not a separate prototype.
- Points, recharge, ledger, history, password, feedback, and logout states are represented.
- Empty-history account shows meaningful empty states.
- High-history account shows useful rows.

## Account Matrix Must Be Consistent

AI Studio's written response and actual exported code disagree.

Written response claimed:

- `13800138000`: full regression, 6000 pt
- `13600136000`: low points Bazi, 120 pt
- `13500135000`: low points quick review, 30 pt
- `13900139000`: empty state, 3000 pt

Actual exported `server.ts` has:

- `13800138000`: 20000 pt
- `13600136000`: 80 pt
- `13900139000`: 20 pt low-points account
- `13700137000`: 20000 pt empty-history account
- `13500135000`: missing

Required fix:

Use this stable matrix in both code and explanation:

| Phone | Password | Points | Purpose |
|---|---|---:|---|
| `13800138000` | `Easewise123!` | `6000+` | full regression, rich phone/Bazi/profile history |
| `13600136000` | `Easewise123!` | `120` | can afford base review, then fails aspect/dayun/liunian unlock |
| `13500135000` | `Easewise123!` | `30` | immediate base insufficient-points case |
| `13900139000` | `Easewise123!` | `3000+` | high-points empty-history account |

Optional compatibility aliases are allowed, but the four accounts above must work and be documented consistently.

## Do Not Change

- Do not convert to React, TSX, or JSX.
- Do not rewrite the aligned H5 shell or bottom navigation.
- Do not remove points work from export `(3)`; build on it.
- Do not make all demo accounts high-points.
- Do not hide insufficient-points states.
- Do not replace local state/event contracts with AI Studio-only mock names.
- Do not keep the AI Agent and Profile pages untouched; they are explicit targets this round.

## Acceptance Checklist

- Project remains Vue 3 + Vite.
- Changed files include `server.ts`, `src/components/analysis/Analysis.vue`, `src/components/ai-agent/AIAgent.vue`, and `src/components/profile/Profile.vue`.
- Phone review automatically transitions from waiting to result without route/tab navigation.
- Four Pillars result page has rich local-style mock data, not empty or generic output.
- AI Agent input is docked just above bottom navigation with no large blank gap.
- AI Agent keeps local login/localStorage behavior.
- Profile page visually and behaviorally resembles current local Profile, including points, ledger, history, recharge, promotion entry, feedback, password, and logout states.
- Demo account matrix is consistent between code and written notes.
- Export zip can be diffed in the next cycle.
