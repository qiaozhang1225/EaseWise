# AI Studio Follow-Up Request

The latest export is much closer to the EaseWise H5 baseline, but it still has several important gaps. Please make a narrow repair pass only. Do not redesign unrelated pages.

## Environment Variables

If AI Studio asks for environment variables, use:

```text
VITE_API_BASE_URL=/api
VITE_APP_BASE_PATH=/
```

If an empty value is accepted, `VITE_API_BASE_URL` may also be empty, matching `.env.example`.

## Scope

This project remains H5/mobile frontend only. Do not add the backend admin management system.

Keep:

- Vue 3 + Vite
- current H5 routes and component contracts
- API/state/type/persistence behavior
- points/pricing behavior
- auth/session behavior
- user-facing pages only

## Fix 1: TypeScript Duplicate Interfaces

`npm run lint` currently fails because `src/types/api.ts` has duplicate conflicting interface declarations near the end of the file.

Please fix `src/types/api.ts` so `npm run lint` passes.

Known conflicts include:

- `InternalFourPillarsReviewDetailResponse`
- `InternalFourPillarsReviewListResponse`
- `InternalPhoneQimenReviewDetailResponse`
- `InternalPhoneQimenReviewListResponse`
- `RuntimeConfigEntryResponse`
- `RuntimeConfigEntryUpsertRequest`
- `UsageRecordListResponse`

Do not append another compatibility section. Remove the duplicate appended declarations or replace the file with one clean coherent type definition.

## Fix 2: Restore Four Pillars Input Fidelity

The current export has regressed the Four Pillars input page to native `type="date"` / `type="time"` inputs and a simple city text field.

Please restore the current professional H5 input design:

- compact title/form card
- manual numeric year/month/day/hour/minute fields
- wheel picker working together with manual fields
- calendar mode handling
- birth location bottom sheet/drawer
- location preview with timezone/longitude/latitude/true-solar-time context
- bottom-navigation-safe sheets
- no native date/time input UI
- no simple free-text city-only input as the main location selector

Keep the active Four Pillars route using:

- `src/components/four-pillars/FourPillarsAnalysis.vue`
- `src/components/four-pillars/FourPillarsNatalTable.vue`

Do not switch back to `src/components/bazi/BaziAnalysis.vue`.

## Fix 3: Check Undefined Four Pillars Symbols

Please check and fix these references in `FourPillarsAnalysis.vue`:

- `Loader2`
- `resetToInput`
- `reviewScore`

They should either be properly imported/defined or removed/replaced.

## Fix 4: Expand Mock Data

The current mock data is still too thin for design testing. Please expand `server.ts` mock data while keeping it clearly demo-only.

Required demo accounts:

- `13800138000`: high-points full regression account with rich phone history, rich Four Pillars history, unlocked aspect examples, points ledger, recharge/order examples.
- `13600136000`: low-points account that can create a base review but should trigger insufficient points on aspect unlocks and luck-cycle/year generation.
- `13500135000`: very low-points account that triggers insufficient points before base phone/Four Pillars generation.
- `13900139000`: high-points clean empty-history account for first-time flows.
- `13700137000`: high-points account with partially completed histories, mixed locked/unlocked aspects, and several points ledger records.

Mock data must cover:

- phone review list/detail
- Four Pillars review list/detail
- Four Pillars luck cycles and years
- points ledger
- recharge packages/orders
- profile state
- empty state
- insufficient-points state
- completed/unlocked/locked aspect states
- Meihua prototype entry state if available

Make mock records rich enough for visual review, not just one-line placeholders.

## Fix 5: Remove Fantasy Copy

Do not use fantasy-style product wording. Remove these words from user-facing UI and mock-visible content:

- `同修`
- `灵台`
- `灵币`
- `灵能`
- `修行点数`
- `功德包`

Use plain EaseWise terminology instead:

- 用户
- 积分
- 注册礼包
- 充值
- 客服
- 评测记录
- 积分记录

Please check at least:

- `server.ts`
- `src/components/ai-agent/AIAgent.vue`
- `src/components/analysis/Analysis.vue`
- `src/components/points-claim/PointsClaimPage.vue`
- `src/components/profile/Profile.vue`
- `src/components/recharge/RechargePage.vue`
- `src/components/support/ContactServiceModal.vue`
- `src/components/bazi/BaziAnalysis.vue` if it remains in the project

## Do Not Change

- Do not add admin management pages.
- Do not convert the project to another framework.
- Do not change real API route names or frontend state contracts.
- Do not remove H5 pages that already exist.
- Do not replace business logic with mock-only assumptions.

## Acceptance Checklist

- `npm run build` passes.
- `npm run lint` passes.
- AI Studio no longer blocks on missing env vars when `VITE_API_BASE_URL=/api` and `VITE_APP_BASE_PATH=/` are set.
- Four Pillars input page no longer uses native browser date/time inputs.
- Birth date and birth location pickers are usable and visually close to the H5 design baseline.
- The mock demo accounts cover rich history, empty state, high points, low points, insufficient points, locked/unlocked aspects, and points ledger scenarios.
- User-facing copy no longer contains `同修 / 灵台 / 灵币 / 灵能 / 修行点数 / 功德包`.
