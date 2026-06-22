# Merge Constraints

This cycle is for preparing the next AI Studio prompt only. Do not merge AI Studio output into the local product frontend until the next zip export is registered and diffed.

## Import From AI Studio Later

Only consider importing:

- visual treatment for loading, empty, failed, low-points, locked, and success states
- spacing/hierarchy improvements inside phone review, four pillars, profile history, and ledger states
- better state presentation for four pillars waiting and luck generation
- copy treatment if it does not change local business meaning

## Preserve Locally

Preserve local:

- Vue 3 + Vite architecture
- route/query behavior in `App.vue`
- API client paths and response field names
- `useEaseWiseApp` state contract
- auth/session behavior
- point balance and deduction semantics
- payment/recharge behavior
- local validation and error mapping
- local storage keys
- profile avatar upload and account behavior
- actual frontend component ownership

## Hard Reject During Local Merge

Reject AI Studio changes that:

- introduce React, TSX, JSX, Next.js, React hooks, or React Router
- rename local API fields or routes
- replace local real handlers with mock-only logic
- remove local error/loading/empty/permission states
- turn valid four pillars input into a birth-info error
- use `finance` instead of local phone aspect key `wealth`
- remove staged generation/polling behavior
- overwrite local auth/profile/account behavior with invented UI semantics
