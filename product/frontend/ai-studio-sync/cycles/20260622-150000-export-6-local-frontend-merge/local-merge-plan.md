# Local Merge Plan: AI Studio Export 6

- Date: 2026-06-22
- Repo: `/Users/qiaoz-macmini/Projects/EaseWise`
- Frontend root: `product/frontend`
- AI Studio zip: `/Users/qiaoz-macmini/Downloads/easewise-vue-sync (6).zip`
- AI Studio zip SHA256: `a139bf3755267ed339979736a84cae863f379796bd1dbb4e26aab94b10410c73`

## Imported Design Changes

- `AIAgent.vue`: imported the bottom-aligned chat layout idea only. The local login gate, persisted conversation state, quick queries, and simulated local response flow remain unchanged.
- `FourPillarsAnalysis.vue`: imported the four-stage waiting animation direction and the phone-review-style waiting surface: circular aura, poem line, progress bar, and staged list.
- `Profile.vue`: imported the combined phone + four-pillars review-history modal pattern with distinct visual labels and subject fields.

## Preserved Local Behavior

- No AI Studio mock server behavior was merged into local product source.
- Phone review, recharge, auth, points, password/profile edit, customer service, and existing route contracts remain owned by local code.
- Four Pillars API calls still use `submitFourPillarsReview`, `startReviewPolling`, `refreshCurrentFourPillarsReview`, aspect unlocks, and luck-generation helpers.
- Existing `BottomNav.vue` was not changed; the agent page adapts its own viewport height to the navigation height.

## Implementation Notes

- The agent page removes the previous root `pb-[84px]` spacer and uses `h-[calc(100dvh-82px)]` so the bottom input area touches the nav top boundary.
- Four Pillars generation now runs polling and the staged animation concurrently; the result page appears only after both the backend review is ready and the minimum animation duration has elapsed.
- Four Pillars historical records were removed from the input form. History is now centralized in the profile modal.
- Profile history opens phone reviews via `refreshCurrentReview(id)` and four-pillars reviews via `refreshCurrentFourPillarsReview(id)`, then navigates to the matching tab.

## Checks

- `npm run build` passed.
- `npm run lint` passed.

