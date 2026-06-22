# AI Studio Sync Request

## Objective

Perform a profile pixel/source replication pass for the EaseWise Vue 3 + Vite H5 prototype.

The previous profile iteration is directionally closer, but it is still not close enough to the current local product. This round should stop approximating from prose and instead use the Source Code Appendix in the bundle as the replication baseline.

## Source Hierarchy

- Local repo behavior is authoritative for real routes, APIs, auth, validation, state, persistence, payments, and business behavior.
- Latest AI Studio zip is authoritative only for AI Studio's current prototype state.
- The bundled local source files are the primary target for this round.
- If this prompt and the source code disagree, follow the source code for `Profile.vue`, `SystemIntro.vue`, `AmbassadorDetail.vue`, `index.css`, `useEaseWiseApp.ts`, `api.ts`, and `types/api.ts`.

## Current AI Studio Export

The latest export changed the correct files:

- `src/components/profile/Profile.vue`
- `src/components/profile/SystemIntro.vue`
- `src/components/profile/AmbassadorDetail.vue`

It also made the right directional improvements:

- Plain profile copy is closer to local.
- Remote avatar presets were removed.
- The action-list model exists.
- The partnership/pricing manual exists.
- Fake invitation links/posters/live commission were mostly removed.

But the code and layout are still not close enough:

- `Profile.vue` is still only about 8% similar to the local source.
- `SystemIntro.vue` is still only about 4% similar to the local source.
- `AmbassadorDetail.vue` is still only about 5% similar to the local source.

This is now a source-replication task, not a broad design-writing task.

## Source Files To Use

Open the `Source Code Appendix` section in the Markdown bundle and use these local files as the concrete target:

- `product/frontend/src/components/profile/Profile.vue`
- `product/frontend/src/components/profile/SystemIntro.vue`
- `product/frontend/src/components/profile/AmbassadorDetail.vue`
- `product/frontend/src/index.css`
- `product/frontend/src/composables/useEaseWiseApp.ts`
- `product/frontend/src/lib/api.ts`
- `product/frontend/src/types/api.ts`

You may adapt imports and API calls only where required for the AI Studio mock server, but the visible profile layout, section order, interaction model, class rhythm, and modal structure should follow the local source very closely.

## Design Task

### 1. Replace Profile.vue with a close local-source adaptation

Make the AI Studio `Profile.vue` match the bundled local `Profile.vue` structure and visual hierarchy.

Required visible structure:

- Top-level mobile column with the same spacing rhythm.
- Header card with avatar, avatar edit button, nickname, identity badge, phone/account hint, and profile edit button.
- Dark points card labeled `我的积分结存`.
- Recharge button that emits:

```ts
emit('navigate-to-tab', 'recharge', { source: 'profile', return_to: 'profile' })
```

- Promotion card: `升级为「易如反掌」推广大使`.
- Action-list rows:
  - `合伙与推广说明书`
  - `积分记录`
  - `评测记录`
  - `修改密码`
  - `反馈问题`
- Account action button and footer matching local.
- Modal overlays matching local for:
  - points ledger
  - review history
  - feedback
  - profile editor
  - password editor
  - logout confirmation

Use the local file's state names and handlers where practical. Do not create a new simplified profile implementation if the local source can be adapted.

### 2. Replace SystemIntro.vue with a close local-source adaptation

The local `SystemIntro.vue` is a full-screen H5 manual. Replicate it closely.

Required traits:

- Full-screen mobile-first page/panel.
- Header and close/back behavior like local.
- Rich section structure, not a short summary.
- Pricing and partnership content close to local.
- Calculator/stateful sections close to local.
- Share/copy behavior can be adapted to AI Studio mock constraints, but the visible section structure should remain close.

Do not shorten this into a small modal or a brief documentation page.

### 3. Replace AmbassadorDetail.vue with a close local-source adaptation

Replicate the bundled local `AmbassadorDetail.vue` more closely.

Required traits:

- Full promoter rules page style and hierarchy.
- Benefit cards and threshold cards matching local.
- Conservative backend-rule-driven copy.
- CTA/closing section matching local.

Do not reintroduce fake invitation code, fake invitation URL, fake poster download, or fake live commission tracking.

## Mock Data And States

Keep the previous demo account matrix working:

- `13800138000`: high-points regression account
- `13600136000`: low-points unlock-insufficient account
- `13500135000`: base-insufficient account
- `13900139000`: empty-history high-points account

Profile must still demonstrate:

- guest state
- registered state
- avatar upload validation
- points balance
- points ledger modal
- review history modal
- empty history state
- profile editor
- password editor
- logout confirmation

If the local source references backend helpers that are absent in the AI Studio mock environment, implement the smallest compatibility shim in the AI Studio code without changing the visible product behavior.

## Do Not Change

- Do not rework Four Pillars/Bazi pages.
- Do not rework phone review waiting/result flow.
- Do not rework AI Agent layout.
- Do not change global navigation unless the profile source adaptation requires a compile fix.
- Do not convert Vue files to React/TSX.
- Do not invent product behavior that is not in the bundled local source.
- Do not add fake referral links, invitation codes, poster generation, or live commission tracking.
- Do not use remote Unsplash avatar presets.

## Acceptance Checklist

- `Profile.vue`, `SystemIntro.vue`, and `AmbassadorDetail.vue` are changed again.
- The resulting `Profile.vue` visibly follows the bundled local source section order and layout.
- The dark points card, promotion card, action list, account button, footer, and modal overlays match local much more closely.
- `SystemIntro.vue` is a rich full-screen manual close to the bundled local file, not a shortened summary.
- `AmbassadorDetail.vue` is close to the bundled local rules page.
- The profile surface does not use `同修`, `灵台`, `灵币`, or `玄想`.
- The recharge button still emits `{ source: 'profile', return_to: 'profile' }`.
- The app remains Vue 3 + Vite and builds successfully.
- Four Pillars, phone review, and AI Agent behavior remain stable.
