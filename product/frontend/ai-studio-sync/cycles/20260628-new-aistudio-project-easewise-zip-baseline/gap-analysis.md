# New AI Studio Project Gap Analysis

## Context

This cycle audits `/Users/qiaoz-macmini/Downloads/easewise.zip` as the new AI Studio account/project baseline. The zip is usable as a shell project, but it is not yet equivalent to the current local EaseWise frontend.

The main conclusion: do not continue iterating from this export as-is. First bootstrap the new AI Studio project with the current local frontend source, especially CSS, routing contracts, Four Pillars, profile, API/types, and Meihua prototype files.

## Critical Gaps

### 1. CSS/theme is missing

`src/index.css` in the new export only contains:

```css
@import "tailwindcss";
```

This drops the local EaseWise visual baseline:

- global body background and typography
- CSS custom properties / theme tokens
- hidden scrollbar utilities used by wheel pickers
- icon/card animations
- app shell sizing and safe-area behavior

This explains why the new project can compile but cannot faithfully reproduce the current UI.

### 2. Four Pillars route is pointed at an outdated component

The new export uses:

- `src/components/bazi/BaziAnalysis.vue`

The current local product uses:

- `src/components/four-pillars/FourPillarsAnalysis.vue`
- `src/components/four-pillars/FourPillarsNatalTable.vue`

The exported `BaziAnalysis.vue` is a simplified prototype with native date/time inputs and older copy. It does not represent the current professional Four Pillars input/result page with bottom-sheet date/location pickers, real API flow, natal chart modal, luck-cycle rendering, and current result table layout.

### 3. App-level route/event contracts drifted

`src/App.vue` in the new project uses older event names and a simpler route contract. The local app now depends on current contracts such as:

- `back-to-home`
- `navigate-to-tab`
- route query props
- recharge/claim context handling
- current Four Pillars restore/navigation behavior

AI Studio should restore the local `App.vue` contract before doing design iterations.

### 4. Current profile/detail components are missing

The new export is missing:

- `src/components/profile/AmbassadorDetail.vue`
- `src/components/profile/SystemIntro.vue`

Current `Profile.vue` and personal-center flows have been iterated repeatedly; the new export is not a reliable profile baseline.

### 5. Current business client/types are older in the export

The following files materially differ and should be restored from local before future design work:

- `src/composables/useEaseWiseApp.ts`
- `src/lib/api.ts`
- `src/types/api.ts`
- `src/config/pricing.ts`
- `src/constants/storage.ts`

These files encode real API/state/persistence/payment/history behavior. AI Studio mock code must not become business authority.

### 6. Meihua prototype should be preserved from local

The new export has a smaller `MeihuaAnalysis.vue`. Since Meihua is the next development focus and the local project already imported/expanded a frontend prototype, AI Studio should use the local file as the new baseline rather than shrinking it to the exported version.

### 7. Admin file is severely truncated

`src/components/admin/AdminWorkspace.vue` is about 1.2 KB in the new export and about 348 KB locally. If AI Studio needs full admin parity, this must be synced separately because it is too large to include casually in the same H5 repair prompt.

### 8. Mock-only files should be classified, not adopted

The new export contains:

- `server.ts`
- `src/components/four-pillars/mockLocations.ts`

These can help AI Studio run a local demo, but they should not override the local product backend/API source of truth. For production-aligned work, use the local API contracts and treat these as AI Studio demo scaffolding only.

## Recommended Sync Strategy

1. Treat this export as a new AI Studio project shell, not as the source of truth.
2. Paste the H5 repair bundle into AI Studio and ask it to restore the current local frontend source.
3. Restore `src/index.css` first, then `App.vue`, then `FourPillarsAnalysis.vue` / `FourPillarsNatalTable.vue`, then shared API/types/state files.
4. Keep `src/components/bazi/BaziAnalysis.vue` only if AI Studio wants an experimental reference; it should not be the active `bazi` route.
5. Sync `AdminWorkspace.vue` only as a separate appendix if the admin surface is needed in the new AI Studio project.
6. After AI Studio applies the repair, export again and compare against local before continuing design iterations.

## Acceptance Checklist

- `src/index.css` is no longer 23 bytes and contains the EaseWise global/theme/scrollbar/animation rules.
- `App.vue` imports and renders `FourPillarsAnalysis` from `src/components/four-pillars/FourPillarsAnalysis.vue`.
- `src/components/four-pillars/FourPillarsNatalTable.vue` exists and is used by the Four Pillars result page.
- `Profile.vue` can import/use `AmbassadorDetail.vue` and `SystemIntro.vue`.
- `MeihuaAnalysis.vue` matches the local prototype baseline.
- AI Studio demo still compiles in Vue 3 + Vite.
- AI Studio does not replace real API/state/types with mock-only server assumptions.
