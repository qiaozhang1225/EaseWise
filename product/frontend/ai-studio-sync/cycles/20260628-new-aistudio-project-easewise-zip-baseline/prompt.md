# AI Studio Sync Request

## Objective

Please rebuild this new AI Studio project from the attached Markdown source bundle so it matches the current EaseWise H5 frontend prototype. This AI Studio project is only for the mobile/H5 user-facing prototype and design iteration. It does **not** need the backend admin management system.

## Source Hierarchy

- The Markdown `bundle.md` I will paste is the source of truth for the H5 frontend files.
- Preserve Vue 3 + Vite architecture.
- Preserve the local frontend business contracts: route names, API fields, auth/session behavior, points/pricing handling, persistence, history, error states, and component event contracts.
- Treat any current AI Studio `server.ts`, mock data, or demo-only files as scaffolding only.
- Do not use the old simplified `src/components/bazi/BaziAnalysis.vue` as the active Four Pillars page.

## Current AI Studio Export

The current new-project export is incomplete:

- `src/index.css` only contains `@import "tailwindcss";`, so the EaseWise theme/style baseline is missing.
- The active Four Pillars route points to an older simplified `BaziAnalysis.vue`.
- The current local Four Pillars implementation files are missing.
- Several current H5 pages and shared business files differ from local.
- The admin workspace is not in scope for this AI Studio project.

## What To Rebuild

Recreate every file from `bundle.md` at the exact path shown in each file heading.

The most important files to restore are:

- `src/index.css`
- `src/App.vue`
- `src/components/home/Home.vue`
- `src/components/analysis/Analysis.vue`
- `src/components/four-pillars/FourPillarsAnalysis.vue`
- `src/components/four-pillars/FourPillarsNatalTable.vue`
- `src/components/meihua/MeihuaAnalysis.vue`
- `src/components/profile/Profile.vue`
- `src/components/recharge/RechargePage.vue`
- `src/components/points-claim/PointsClaimPage.vue`
- `src/components/ai-agent/AIAgent.vue`
- `src/composables/useEaseWiseApp.ts`
- `src/lib/api.ts`
- `src/types/api.ts`
- `src/config/pricing.ts`
- `src/constants/storage.ts`
- `package.json`
- `vite.config.ts`
- `tsconfig.json`

## Four Pillars Requirement

The active Four Pillars page must use:

- `src/components/four-pillars/FourPillarsAnalysis.vue`
- `src/components/four-pillars/FourPillarsNatalTable.vue`

Do not replace this with the older `src/components/bazi/BaziAnalysis.vue`.

Keep the current Four Pillars input/result design from the bundle, including:

- compact entry card
- manual numeric birthday input plus wheel picker
- calendar mode support
- birth location picker
- true-solar-time display/contract
- natal chart result table
- more chart information modal
- luck cycle display behavior

## H5 Scope

This project should include the H5/mobile user-facing prototype only:

- home
- phone/qimen number analysis
- Four Pillars analysis
- Meihua prototype entry/page
- AI Agent
- profile
- recharge
- points claim
- auth/support overlays
- bottom navigation/header layout

Do **not** add or restore the large admin management system in this AI Studio project. If you see an old `AdminWorkspace.vue`, `AdminSelect.vue`, or backend-admin route in the export, leave it out of this reconstruction. The `bundle.md` file is already adapted for H5-only compilation.

## Do Not Change

- Do not convert the project to React, TSX, or another framework.
- Do not redesign the H5 experience yet; first restore the current local baseline.
- Do not simplify Four Pillars back to native date/time inputs.
- Do not remove current API/state/type/persistence contracts.
- Do not invent new backend behavior from mock files.
- Do not introduce fantasy-style wording such as `灵币`, `同修`, or `灵能`.
- Do not import the admin appendix or backend admin system.

## Acceptance Checklist

- The project compiles as Vue 3 + Vite.
- `src/index.css` is restored from `bundle.md`, not left as a one-line Tailwind import.
- `src/App.vue` renders `FourPillarsAnalysis` from `src/components/four-pillars/FourPillarsAnalysis.vue`.
- `FourPillarsNatalTable.vue` exists and is used by the Four Pillars result page.
- The home page includes the current H5 service entries, including the Meihua prototype.
- Phone analysis, Four Pillars, Meihua, AI Agent, profile, recharge, points claim, auth, and support overlays all keep the bundled local contracts.
- No large admin management system is included.

## Response Format

After applying the bundle, reply with:

1. Files recreated or replaced.
2. Files intentionally omitted because they are admin-only or AI Studio mock-only.
3. Any compile/runtime errors.
4. Confirmation that the active Four Pillars route uses `src/components/four-pillars/FourPillarsAnalysis.vue`.
