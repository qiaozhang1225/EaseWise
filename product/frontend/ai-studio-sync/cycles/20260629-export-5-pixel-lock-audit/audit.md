# AI Studio Export 5 Pixel-Lock Audit

## Source

- Source zip: `/Users/qiaoz-macmini/Downloads/easewise (5).zip`
- SHA256: `cb25cbd9953cc41e7813314ba34190c6e120878b624efce87afc02bd1e2e9400`
- Clean extraction: `/tmp/easewise-export-5-clean`
- File count: `39`

## User-Observed Gap

The home page looks acceptable, and login/runtime issues are improving, but these pages still differ heavily from the current local project:

- 手机号评测
- 四柱八字
- 个人中心
- 智能体

The user wants AI Studio to pixel-replicate the current local state instead of creatively redesigning these pages.

## Evidence

The gap is structural, not just visual.

```text
src/components/analysis/Analysis.vue
  AI Studio: 573 lines / 24,995 bytes
  Local:     2,884 lines / 114,609 bytes

src/components/four-pillars/FourPillarsAnalysis.vue
  AI Studio: 658 lines / 35,700 bytes
  Local:     3,741 lines / 156,305 bytes

src/components/profile/Profile.vue
  AI Studio: 230 lines / 9,501 bytes
  Local:     1,148 lines / 48,272 bytes

src/components/ai-agent/AIAgent.vue
  AI Studio: 418 lines / 17,085 bytes
  Local:     303 lines / 13,492 bytes
```

This means AI Studio has not preserved the real local component structures. It is generating simplified analogues.

## Why Natural-Language Prompting Is Failing

Prompts like “make it closer” or “restore the current design” leave too much room for AI Studio to infer. The exported files show that it:

- keeps simplified phone/four-pillars/profile components
- invents mock-only UI helpers
- preserves runtime fixes but does not restore the real local page composition
- uses its own interpretation of the page instead of the local source

For pixel-level parity, AI Studio must receive the exact local files and be instructed to replace the corresponding AI Studio files.

## Required Strategy

Use a pixel-lock source bundle:

- `bundle.md`: local source-of-truth files for the drifting pages and required dependencies
- `Prompt.md`: strict replacement instructions

The bundle includes:

- `src/components/analysis/Analysis.vue`
- `src/components/four-pillars/FourPillarsAnalysis.vue`
- `src/components/four-pillars/FourPillarsNatalTable.vue`
- `src/components/profile/Profile.vue`
- `src/components/profile/AmbassadorDetail.vue`
- `src/components/profile/SystemIntro.vue`
- `src/components/ai-agent/AIAgent.vue`
- `src/components/support/ContactServiceModal.vue`
- `src/composables/useEaseWiseApp.ts`
- `src/lib/api.ts`
- `src/types/api.ts`
- `src/config/pricing.ts`
- `src/constants/storage.ts`
- `src/index.css`

## Important Constraint

Do not ask AI Studio to “apply design ideas” in this pass. Ask it to replace the specified files exactly, then make only minimal compatibility edits if the project fails to compile.

## Follow-Up After AI Studio Exports Again

After the next export:

1. Compare line/byte sizes again for the four key components.
2. Confirm the key local component structures exist.
3. Run lint/build.
4. Only then resume design-level polish.
