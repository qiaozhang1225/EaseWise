# AI Studio Export 6 Pixel-Lock Not Applied Audit

## Source

- Source zip: `/Users/qiaoz-macmini/Downloads/easewise (6).zip`
- SHA256: `246a61224736ad1daca3e072cbfbfe9ff2cc04c6505889eb099a82674ac41450`
- Clean extraction: `/tmp/easewise-export-6-clean`
- File count: `39`

## AI Studio Claim

AI Studio reported that it repaired the AI Agent chat session engine:

- client-side chat session management
- simulated streaming typing effect
- local storage persistence
- 1-point deduction after generation

## What Actually Changed

The export changed shared state/API/type files, but did not apply the requested pixel-lock replication to the main assessment pages.

## Key Evidence

```text
src/components/analysis/Analysis.vue
  Export 6: 573 lines / 24,995 bytes
  Local:    2,884 lines / 114,609 bytes
  Changed from export 5: no

src/components/four-pillars/FourPillarsAnalysis.vue
  Export 6: 658 lines / 35,700 bytes
  Local:    3,765 lines / 158,790 bytes
  Changed from export 5: no

src/components/profile/Profile.vue
  Export 6: 230 lines / 9,501 bytes
  Local:    1,148 lines / 48,272 bytes
  Changed from export 5: no

src/components/ai-agent/AIAgent.vue
  Export 6: 418 lines / 17,085 bytes
  Local:    303 lines / 13,492 bytes
  Changed from export 5: no
```

So the previous pixel-lock request was not followed. AI Studio worked on the agent engine instead of replacing the drifting page components.

## Current User-Tested Problem

Even though the frontend may look broadly acceptable, the core assessment routes are still not usable for local-product testing:

- 手机号评测 is still a simplified AI Studio version, not the local product page.
- 四柱八字 is still a simplified AI Studio version, not the local product page.
- 个人中心 and 智能体 still differ significantly from the local product.

## Next Strategy

Do not ask AI Studio to repair all four areas at once.

The next pass should be **Phase A only**:

1. Replace 手机号评测.
2. Replace 四柱八字.
3. Replace only the shared files required for those flows to compile and run.

Do not touch Profile or AI Agent in this pass. This prevents AI Studio from picking a different target again.

## Phase A Bundle

`bundle.md` contains the local source-of-truth files for:

- `src/App.vue`
- `src/components/analysis/Analysis.vue`
- `src/components/four-pillars/FourPillarsAnalysis.vue`
- `src/components/four-pillars/FourPillarsNatalTable.vue`
- `src/components/support/ContactServiceModal.vue`
- `src/composables/useEaseWiseApp.ts`
- `src/lib/api.ts`
- `src/types/api.ts`
- `src/config/pricing.ts`
- `src/constants/storage.ts`
- `src/index.css`

## Pass/Fail Rule For Next Export

The next export should be treated as failed if:

- `Analysis.vue` remains around 573 lines.
- `FourPillarsAnalysis.vue` remains around 658 lines.
- AI Studio reports unrelated AI Agent/profile work instead of replacing these two assessment flows.

The next export should be treated as successful only if:

- `Analysis.vue` is structurally close to the bundled local file.
- `FourPillarsAnalysis.vue` is structurally close to the bundled local file.
- lint/build pass.
- Phone review and Four Pillars routes open and can be tested with demo accounts.
