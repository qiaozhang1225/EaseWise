# AI Studio Export 5 Profile Audit

- Date: 2026-06-22
- Repo: `/Users/qiaoz-macmini/Projects/EaseWise`
- Local frontend root: `product/frontend`
- AI Studio export zip: `/Users/qiaoz-macmini/Downloads/easewise-vue-sync (5).zip`
- AI Studio zip sha256: `475b1745f0459379df28815be2043dc2bdbadf6045eb05e4d2e5be3ab94aac91`
- Local git ref: `a9d6be3`

## User-Tested Status

The personal-center iteration is now directionally closer than the previous export. The main profile page uses more local product language, removes the remote avatar preset strip, has an action-list model, and no longer relies on inline tabs as the primary profile body.

However, it is still not a pixel-level reproduction of the current local EaseWise personal center. The next round should provide actual local source code to AI Studio and ask it to replicate the profile area from code rather than continue approximating from prose.

## Export 5 Changes

The latest export changed exactly the profile slice requested:

- `src/components/profile/Profile.vue`
- `src/components/profile/SystemIntro.vue`
- `src/components/profile/AmbassadorDetail.vue`

No new files were added, and no unrelated Four Pillars/phone/agent files changed in this export.

## Similarity Snapshot

Even after the improved direction, the profile files are still structurally far from local:

| File | Similarity to local | Local lines | AI Studio lines | Status |
| --- | ---: | ---: | ---: | --- |
| `Profile.vue` | 8.06% | 1089 | 731 | Better language, still not source-structure parity |
| `SystemIntro.vue` | 4.13% | 736 | 280 | Correct topic, still much thinner than local |
| `AmbassadorDetail.vue` | 4.76% | 209 | 125 | Correctly conservative, still visually/structurally simplified |

## Remaining Gaps To Close

### 1. Profile needs source-level replication

The next iteration should not ask AI Studio to infer the UI from descriptions. It should use the bundled local source code as the replication baseline.

Key local `Profile.vue` patterns that must be preserved:

- Same top-level spacing and max-width column.
- Same avatar header composition and edit affordance.
- Same dark points-card treatment.
- Same promoter/system intro card.
- Same compact action-list card.
- Same account button/footer composition.
- Same modal overlay structure for ledger, history, feedback, profile edit, password edit, and logout confirmation.
- Same local function/state structure unless the AI Studio mock app requires a narrow compatibility shim.

### 2. SystemIntro is still too short

AI Studio moved `SystemIntro.vue` in the right direction, but the local file is a full H5 manual with richer sections, calculator state, share/copy actions, tables, and long-form pricing/partnership explanation. The next prompt should tell AI Studio to copy the local `SystemIntro.vue` structure directly from the Source Code Appendix.

### 3. AmbassadorDetail is directionally correct but simplified

AI Studio removed fake invitation codes and poster generation, which is good. It still needs to match the local visual hierarchy, benefit-card layout, thresholds, rules, and closing CTA more closely.

### 4. Do not regress the previous improvements

The next iteration must keep:

- Plain local product copy.
- No `同修`, `灵台`, `灵币`, or `玄想` in the profile surface.
- No remote avatar presets.
- No fake invitation code/link/poster/live commission.
- Protected ledger and review-history overlays.
- `我的积分结存` points label.
- Recharge navigation payload `{ source: 'profile', return_to: 'profile' }`.

## Local Source Files Added To Bundle

The next bundle includes real source-code appendices for the selected profile slice and dependencies:

- `product/frontend/src/components/profile/Profile.vue`
- `product/frontend/src/components/profile/SystemIntro.vue`
- `product/frontend/src/components/profile/AmbassadorDetail.vue`
- `product/frontend/src/index.css`
- `product/frontend/src/composables/useEaseWiseApp.ts`
- `product/frontend/src/lib/api.ts`
- `product/frontend/src/types/api.ts`

AI Studio should use those files as the primary replication target.

## Next Slice

Profile pixel/source replication:

- Replace the current AI Studio profile implementation with a close Vue-source adaptation of the bundled local files.
- Keep AI Studio mock-server compatibility only where needed.
- Preserve all currently working non-profile flows.

## Acceptance Criteria

- Changed files include `Profile.vue`, `SystemIntro.vue`, and `AmbassadorDetail.vue`.
- The profile page visually matches the local source at the component/section level.
- The dark points card, promoter card, action list, account button, footer, and modal overlays are arranged like local.
- `SystemIntro.vue` is close to the bundled local full-screen manual, not a shortened summary page.
- `AmbassadorDetail.vue` is close to the bundled local rules page, not a simplified booklet.
- No fake business behavior is introduced.
- No Four Pillars, phone review, or AI Agent regression.
