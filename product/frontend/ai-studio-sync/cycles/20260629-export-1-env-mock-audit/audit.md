# AI Studio Export 1 Env And Mock Audit

## Source

- Source zip: `/Users/qiaoz-macmini/Downloads/easewise (1).zip`
- SHA256: `64f5ca7c5559490e636694fc9f8e1804c5a104512d9e782892a6105b17caaf9d`
- Clean extraction: `/tmp/easewise-export-1-clean`
- File count: `38`

## Environment Variables

The export asks for two Vite variables:

- `VITE_API_BASE_URL`
- `VITE_APP_BASE_PATH`

Current `.env.example` already defines the intended defaults:

```text
VITE_API_BASE_URL=
VITE_APP_BASE_PATH=/
```

Meaning:

- `VITE_API_BASE_URL` controls where the frontend sends API requests. Empty means the frontend uses the current site origin and Vite proxy handles `/api` locally. For a standalone AI Studio demo, `/api` or the current origin is acceptable if the included mock server/proxy is available.
- `VITE_APP_BASE_PATH` controls the Vite public base path. For normal AI Studio/local root deployment this should be `/`.

Recommended AI Studio values:

```text
VITE_API_BASE_URL=
VITE_APP_BASE_PATH=/
```

If AI Studio refuses an empty value, use:

```text
VITE_API_BASE_URL=/api
VITE_APP_BASE_PATH=/
```

## What Improved

- `src/index.css` is restored and no longer just imports Tailwind.
- `src/components/four-pillars/FourPillarsAnalysis.vue` and `FourPillarsNatalTable.vue` now exist.
- Profile detail files exist:
  - `src/components/profile/AmbassadorDetail.vue`
  - `src/components/profile/SystemIntro.vue`
- The package is still Vue 3 + Vite.
- `npm run build` succeeds in the exported project.

## Remaining Problems

### 1. TypeScript check fails

`npm run lint` fails because `src/types/api.ts` contains duplicate interface declarations that conflict:

```text
InternalFourPillarsReviewDetailResponse.review
InternalFourPillarsReviewListResponse.items
InternalPhoneQimenReviewDetailResponse.review
InternalPhoneQimenReviewListResponse.items
RuntimeConfigEntryResponse.value
RuntimeConfigEntryUpsertRequest.value
UsageRecordListResponse.items
```

This looks like AI Studio appended extra admin/internal type definitions instead of replacing the file cleanly.

### 2. Four Pillars input page regressed

Exported `FourPillarsAnalysis.vue` is only about 19 KB, while the current local page is about 148 KB. The exported page uses native `type="date"` / `type="time"` inputs and a simple city text field.

It does not preserve the current local professional input page:

- compact title/form card
- manual numeric fields plus wheel picker
- calendar mode handling
- birth location picker
- true-solar-time/location preview
- richer waiting state and error state flow
- route-query restoration behavior

### 3. Potential undefined symbols in Four Pillars

`FourPillarsAnalysis.vue` references:

- `Loader2`
- `resetToInput`
- `reviewScore`

These should be checked/fixed by AI Studio. Vite build currently passes, but this is still code-quality drift and can break once stricter checks or template diagnostics apply.

### 4. Mock data is too thin

The mock server has test accounts, but the seeded data is not rich enough for design review:

- only `13800138000` and `13600136000` have obvious seeded phone/four-pillars histories
- `13500135000`, `13700137000`, `13900139000` are mostly empty
- profile, recharge, points ledger, claim, and history states are thin
- Meihua has no meaningful backend/mock lifecycle
- Four Pillars birthday/location picker design cannot be fully tested because mock location data is very small

### 5. Fantasy copy returned

The export reintroduced wording that should not appear in the current product tone:

- `同修`
- `灵台`
- `灵币`
- `灵能`
- `修行点数`
- `功德包`

These appear in `server.ts`, `AIAgent.vue`, `Analysis.vue`, `PointsClaimPage.vue`, `Profile.vue`, `RechargePage.vue`, and `ContactServiceModal.vue`.

### 6. Bazi prototype file remains

`src/components/bazi/BaziAnalysis.vue` still exists and contains older fantasy-style copy. It should not be the active Four Pillars route. If retained, it must remain unused experimental reference only.

## Recommended Next AI Studio Interaction

Send AI Studio a narrow follow-up prompt, not another full source bundle:

1. Fill env vars with `VITE_API_BASE_URL=/api` if empty values are not allowed, and `VITE_APP_BASE_PATH=/`.
2. Fix `src/types/api.ts` duplicate interfaces by replacing it with the clean local bundled type file or removing the appended duplicate section.
3. Restore Four Pillars input page fidelity from the previous bundle, especially the picker/manual input/location drawer design.
4. Expand mock data for all demo accounts and key states.
5. Remove fantasy wording and use plain EaseWise product copy.
6. Keep admin out of scope.

## Verification

- `npm run build`: passed.
- `npm run lint`: failed with duplicate interface declarations in `src/types/api.ts`.
