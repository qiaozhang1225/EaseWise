# Merge Constraints: AI Studio Export 6

## Import

- Agent chat input bottom alignment.
- Four Pillars staged waiting animation and visual polish.
- Profile combined review-history presentation.

## Preserve

- Local Vue 3 + Vite architecture.
- Local API clients, auth state, route navigation, points, validation, persistence, and backend field contracts.
- Existing admin, recharge, points claim, support, and profile edit/password flows.

## Ignore Or Translate

- Ignore AI Studio `server.ts` mock data changes for local product source.
- Translate AI Studio mock history data into existing `state.reviewHistory` and `state.fourPillarsHistory`.
- Translate AI Studio chat-layout markup into local `AIAgent.vue` without replacing the local login/persistence behavior.

## Required Verification

- Build and TypeScript checks must pass.
- Agent input must visually touch BottomNav on mobile.
- Four Pillars input page must no longer show a local history card.
- Profile history modal must include both phone and four-pillars records and route to the correct tab.

