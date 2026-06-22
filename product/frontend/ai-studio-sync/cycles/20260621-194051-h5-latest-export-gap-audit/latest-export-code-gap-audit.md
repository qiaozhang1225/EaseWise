# Latest AI Studio Export Code Gap Audit

Cycle: `20260621-194051-h5-latest-export-gap-audit`

Source zip: `/Users/qiaoz-macmini/Downloads/easewise-vue-sync (1).zip`

SHA256: `a5ef6ef0d6801dc35b589d8beab713097f103e583c7f7a1557fdc2c7a352854d`

## Summary

This export moved in the right direction, but it is still not enough to judge the final H5 frontend design. The main issue is no longer global styling. The remaining gap is that AI Studio's mock data and state coverage are too thin, and several stateful Vue components are still rewritten rather than aligned to the local product implementation.

The user-observed findings are confirmed from code:

- Phone review and four pillars mock data are too shallow to exercise the UI.
- Four pillars waiting animation exists in component code, but mock server returns `completed` immediately, so the waiting state can disappear too quickly to be visible.
- AI Studio's four pillars component has a real code bug: it calls `sleep(...)` but no `sleep` function is defined.

## Files Changed By This Export

The latest AI Studio export changed only these files from the previous export:

- `server.ts`
- `src/components/analysis/Analysis.vue`
- `src/components/auth/AuthModal.vue`
- `src/components/four-pillars/FourPillarsAnalysis.vue`
- `src/components/profile/Profile.vue`
- `src/components/support/ContactServiceModal.vue`

This matches the requested slice, but the implementation is still incomplete.

## Similarity To Local Frontend

| file | similarity | local lines | AI Studio lines | interpretation |
|---|---:|---:|---:|---|
| `src/App.vue` | 100.00% | 239 | 239 | aligned |
| `src/components/home/Home.vue` | 99.93% | 286 | 286 | aligned |
| `src/index.css` | 100.00% | 76 | 76 | aligned |
| `src/composables/useEaseWiseApp.ts` | 100.00% | 814 | 814 | aligned state contract |
| `src/lib/api.ts` | 99.59% | 816 | 823 | close |
| `src/types/api.ts` | 95.31% | 1228 | 1241 | close |
| `src/components/analysis/Analysis.vue` | 51.54% | 2691 | 1515 | still heavily simplified |
| `src/components/four-pillars/FourPillarsAnalysis.vue` | 86.80% | 1733 | 1736 | close-ish but contains behavioral changes and a missing helper |
| `src/components/profile/Profile.vue` | 5.23% | 1089 | 584 | still rewritten, not aligned |
| `src/components/auth/AuthModal.vue` | 12.85% | 605 | 438 | still rewritten, not aligned |
| `src/components/support/ContactServiceModal.vue` | 13.61% | 173 | 135 | still rewritten |
| `src/components/recharge/RechargePage.vue` | 4.19% | 817 | 299 | still not covered |
| `src/components/points-claim/PointsClaimPage.vue` | 4.39% | 527 | 213 | still not covered |

## What Improved

### Seeded Demo Account Exists

`server.ts` now seeds:

- phone: `13800138000`
- password: `Easewise123!`
- user id: `u_13800138000`
- UID: `EW-DEMO-001`
- nickname: `易友_演示`
- identity: `promoter`
- points: `120`

### Basic Histories Exist

`server.ts` now seeds:

- 1 phone qimen completed review
- 1 four pillars completed review
- 3 points ledger entries

This is a useful first step, but not enough for design QA.

### Auth Modal Has More States

AI Studio restored the mode names:

- `options`
- `phone`
- `login`
- `register`
- `forgot_password`
- `wechat_loading`

However, it directly mutates `state.contactServiceModalVisible`, `state.contactServiceScene`, and `state.contactServiceContext` instead of using `openCustomerServiceModal`. The copy and interaction behavior still differ from local.

### Profile Is No Longer Fully Auth-Gated

AI Studio now shows a guest profile page before login and a logged-in profile after login. This fixes the most visible auth-gate problem, but the file is still a rewritten version, missing many local details and local modal semantics.

## Major Remaining Gaps

### 1. Mock Data Is Too Thin

The latest mock server only includes completed states:

- `status` values in `server.ts`: `completed`, `success`
- `progress_stage` values in `server.ts`: `completed`

Missing mock states:

- phone review `processing`
- phone review `failed`
- phone review `queued`
- phone review `scoring`
- phone review `rendering`
- phone review `finalizing`
- four pillars `processing`
- four pillars `failed`
- four pillars luck cycle `not_generated`
- four pillars luck cycle `processing`
- four pillars luck cycle `failed`
- four pillars luck year `not_generated`
- four pillars luck year `processing`
- four pillars luck year `failed`
- insufficient points user
- guest user
- empty history user
- high-balance user
- low-balance user
- locked aspect state
- unlock-in-progress state

Current seeded phone review has only 3 aspects: `career`, `finance`, `love`.

Local phone UI expects up to 12 aspect keys:

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

Current seeded four pillars review has only 3 aspects:

- `day_master`
- `career_trend`
- `wealth_analysis` in the seed
- newly created reviews use `day_master`, `career_trend`, `wealth_capacity`

Local four pillars UI expects richer aspect and luck data, including:

- `personality`
- `career`
- `wealth`
- `love`
- `health`
- `family_environment`
- luck cycles with render statuses
- luck year items with render statuses
- rendered and unrendered cycle/year result bodies

### 2. Four Pillars Animation Is Present But Not Exercised

AI Studio `FourPillarsAnalysis.vue` still has a waiting section with spinning/pulsing UI:

- `viewState === 'waiting'`
- animated circular SVG
- `Sparkles` pulse
- progress message

But `server.ts` returns a completed review immediately:

- `status: "completed"`
- no `progress_stage`
- no simulated delayed transition

So after submit, the frontend sets `viewState = 'waiting'`, immediately receives a completed response, and switches to `result`. In manual testing this looks like the animation is gone.

Fix needed:

- Add mock server delayed/progressive review behavior, or
- Add AI Studio preview-only minimum waiting duration in `FourPillarsAnalysis.vue`.

The better sync behavior is server-side:

- create review as `processing` with `progress_stage: "queued"`
- first detail poll returns `queued`
- next returns `scoring`
- next returns `rendering`
- next returns `finalizing`
- final returns `completed`

### 3. Four Pillars Has A Code Bug: Missing `sleep`

AI Studio `src/components/four-pillars/FourPillarsAnalysis.vue` calls:

- `await sleep(ASPECT_UNLOCK_RETRY_DELAY_MS)`
- `await sleep(REVIEW_READY_RETRY_DELAY_MS)`
- `await sleep(LUCK_RENDER_RETRY_DELAY_MS)`

But this file has no `function sleep(...)` definition. Local has:

```ts
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}
```

This must be restored before the next export is usable.

### 4. Profile Is Still Not Local-Equivalent

AI Studio `Profile.vue` improved from auth-gated to guest/logged-in, but it is still only 5.23% similar to local and misses/changes several important local semantics:

- does not import or render `SystemIntro.vue`
- does not use `resolveApiAssetUrl`
- does not preserve local avatar upload flow via file input, validation, and `uploadAvatar(imageDataUrl)`
- uses remote Unsplash preset avatars as mock UI, which is not local behavior
- changes local labels into invented "灵台/同修/修证" phrasing
- does not preserve `profileIdentityClass` variants for normal/VIP/SVIP/promoter users
- does not preserve local `activeModal` structure for ledger/history/feedback/logout
- does not preserve local ledger formatting helpers
- does not preserve `connectionError` fallback and reconnect behavior
- does not preserve the local promotion/system intro entry

### 5. Auth Modal Is Still Not Local-Equivalent

AI Studio `AuthModal.vue` restored the broad mode names but still differs from local:

- no `watch(visible)` reset behavior
- no `nextTick` focus management
- removed `phoneHint`
- removed local `actionError` flow
- directly mutates customer-service state instead of calling `openCustomerServiceModal('account_security')`
- uses invented copy and labels
- WeChat placeholder shows "启动微信极速通道中" and times out after 1.8 seconds, rather than matching local reserved placeholder copy
- does not preserve local service agreement disclaimer layout exactly

This is less urgent than mock data, but still a design fidelity gap.

### 6. Phone Analysis Is Still Heavily Simplified

`Analysis.vue` is still only 51.54% similar to local and is much shorter than local.

Specific differences:

- waiting timing was shortened from 4000ms to 500ms, which helps mock speed but changes real local behavior
- fallback text is more invented and less local-authoritative
- local voice playback details and error handling are reduced
- local aspect grid/detail treatment is not fully preserved
- mock data has too few aspects to exercise the full 12-aspect grid

### 7. Four Pillars Error Handling Regressed

AI Studio simplified `handleReviewSyncError`:

```ts
setError('review_failed', humanizeError(error));
```

Local distinguishes:

- `insufficient_points`
- `registered_user_required`
- `module_disabled`
- `birth_datetime`
- `review_timeout`
- `review_failed`
- `request_failed`

This matters for judging error-state design.

### 8. Recharge And Points Claim Are Still Not Covered

Even after this export:

- `RechargePage.vue` similarity is only 4.19%
- `PointsClaimPage.vue` similarity is only 4.39%

They are not the focus of the current complaint, but they remain major H5 parity gaps.

## Code-Level Gap Count

High-priority blockers:

1. Missing `sleep` helper in `FourPillarsAnalysis.vue`.
2. Mock server has no processing/failed/progress-stage states.
3. Four pillars mock completes immediately, so waiting animation is not visible.
4. Phone mock only covers one completed report and 3 aspects, not enough for full UI.
5. Four pillars mock only covers one completed report and 3 aspects, not enough for full UI.

Medium-priority fidelity gaps:

6. `Profile.vue` still rewritten and missing local system intro/avatar/identity/connection/ledger formatting semantics.
7. `AuthModal.vue` still rewritten and missing local focus/reset/hint/customer-service semantics.
8. `Analysis.vue` still heavily simplified and needs more mock data to judge layout.
9. Four pillars error-state mapping regressed.

Lower-priority but still open:

10. `ContactServiceModal.vue` still rewritten.
11. `RechargePage.vue` and `PointsClaimPage.vue` still not aligned.

## Recommended Next Iteration

Do not ask AI Studio for another broad visual pass.

Next prompt should say:

1. First fix build/runtime correctness:
   - restore `sleep(ms)` in `FourPillarsAnalysis.vue`
   - do not remove local error mapping

2. Expand `server.ts` mock data substantially:
   - at least 3 demo users:
     - normal logged-in user with enough points
     - low-points user
     - empty-history user
   - phone reviews:
     - completed full report with all 12 aspects
     - processing report at `queued`
     - processing report at `scoring`
     - processing report at `rendering`
     - failed report
   - four pillars reviews:
     - completed full report with 5-6 aspects
     - processing report with staged progress
     - failed report
     - one report with luck cycle/year rendered
     - one report with luck cycle/year `not_generated`
   - points ledger:
     - recharge add
     - phone review deduct
     - four pillars deduct
     - aspect unlock deduct
     - luck cycle/year deduct

3. Make mock endpoints progress over time:
   - POST creates `processing`
   - detail polling advances `queued -> scoring -> rendering -> finalizing -> completed`
   - keep each stage visible long enough for AI Studio preview

4. Restore local state fidelity:
   - use local `Profile.vue` as source for behavior and modal structure
   - use local `AuthModal.vue` as source for mode transitions, focus, hints, and support modal call
   - preserve local error state mapping in four pillars

## Verification Notes

- `server.ts` bundles successfully with esbuild.
- Full Vite build could not run from the extracted folder because the extracted zip does not include local `node_modules` and Vite cannot resolve `@tailwindcss/vite` from that folder directly.
- Static source inspection confirms the missing `sleep` helper in AI Studio `FourPillarsAnalysis.vue`.
