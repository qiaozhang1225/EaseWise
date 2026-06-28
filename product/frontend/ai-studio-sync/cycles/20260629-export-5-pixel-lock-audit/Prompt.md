# AI Studio Pixel-Lock Replication Request

The current AI Studio H5 preview has working runtime/mock improvements, but four major pages are still not close to the real local EaseWise project:

- 手机号评测
- 四柱八字
- 个人中心
- 智能体

This is not a styling-only issue. The exported AI Studio components are much smaller and structurally different from the local source-of-truth components.

Please stop creatively redesigning these pages. This pass is a strict pixel-lock replication pass.

## Source Hierarchy

The `bundle.md` I will paste after this prompt is the source of truth for this pass.

For every file included in `bundle.md`:

1. Recreate the file at the exact same path.
2. Replace the current AI Studio file content with the bundled local file content.
3. Do not summarize the file.
4. Do not “improve” the layout.
5. Do not simplify the component.
6. Do not keep the current AI Studio version if the bundle includes a replacement.

## Required Replacement Files

Replace these files from `bundle.md` exactly:

```text
src/components/analysis/Analysis.vue
src/components/four-pillars/FourPillarsAnalysis.vue
src/components/four-pillars/FourPillarsNatalTable.vue
src/components/profile/Profile.vue
src/components/profile/AmbassadorDetail.vue
src/components/profile/SystemIntro.vue
src/components/ai-agent/AIAgent.vue
src/components/support/ContactServiceModal.vue
src/composables/useEaseWiseApp.ts
src/lib/api.ts
src/types/api.ts
src/config/pricing.ts
src/constants/storage.ts
src/index.css
```

## Why Replacement Is Required

The current export is structurally far from the local source:

```text
Analysis.vue
  AI Studio: ~573 lines
  Local:     ~2884 lines

FourPillarsAnalysis.vue
  AI Studio: ~658 lines
  Local:     ~3741 lines

Profile.vue
  AI Studio: ~230 lines
  Local:     ~1148 lines
```

This gap cannot be fixed with high-level design instructions. You must restore the local component structures.

## Preserve Existing Runtime Fixes Where Compatible

Keep these runtime fixes if they do not conflict with the bundled files:

- `npm run dev` should continue to run the custom mock server via `tsx server.ts`.
- `VITE_API_BASE_URL=/api` must not cause `/api/api/v1/...` requests.
- API requests should not spin forever on misrouting/timeouts.
- `GET /api/v1/mock/summary` can remain as a mock-only test helper.
- Demo accounts can remain in `server.ts`.

But do not let these mock/test helpers override the bundled page components.

## Allowed Compatibility Edits

After replacing the bundled files, you may make minimal edits only if required for compile/runtime compatibility:

- add missing imports
- add missing exported API helpers referenced by the bundled files
- align TypeScript types with the bundled code
- preserve or re-add the mock summary API helper in `src/lib/api.ts` if needed
- keep the custom server start script

Do not make aesthetic redesign edits in this pass.

## Mock Data Requirement

After restoring the local frontend files, ensure the mock server still provides enough data for testing:

- `13800138000 / Easewise123!`: full regression, high points, phone history, Four Pillars history, points ledger
- `13600136000 / Easewise123!`: low points, insufficient for deep unlocks
- `13500135000 / Easewise123!`: very low points, insufficient for base review
- `13900139000 / Easewise123!`: high points, empty history
- `13700137000 / Easewise123!`: mixed partial history

The important part: make the mock responses satisfy the restored bundled frontend files, not the simplified AI Studio pages.

## Do Not Change

- Do not add backend admin pages.
- Do not convert Vue/Vite architecture.
- Do not replace bundled components with shorter simplified versions.
- Do not remove local route/event contracts.
- Do not change real API path names unless adding mock compatibility aliases.
- Do not reintroduce fantasy/game-style wording.
- Do not redesign page hierarchy, cards, buttons, pickers, modals, or result tables.

## Acceptance Checklist

After applying `bundle.md`:

- `npm run lint` passes.
- `npm run build` passes.
- `npm run dev` starts the custom mock server.
- `Analysis.vue` is close to the bundled local size/structure, not the old ~573-line simplified version.
- `FourPillarsAnalysis.vue` is close to the bundled local size/structure, not the old ~658-line simplified version.
- `Profile.vue` is close to the bundled local size/structure, not the old ~230-line simplified version.
- AI Agent layout matches the bundled local source.
- Phone review page opens and matches the current local product layout.
- Four Pillars page opens and matches the current local product layout.
- Profile page opens and matches the current local product layout.
- Demo login still works.
- Almanac/mock data still loads.

## Response Format

Reply with:

1. Files replaced exactly from `bundle.md`.
2. Minimal compatibility edits made after replacement.
3. Runtime/mock server changes preserved.
4. Verification results for `npm run lint`, `npm run build`, and `npm run dev`.
5. Any files you could not replace and why.
