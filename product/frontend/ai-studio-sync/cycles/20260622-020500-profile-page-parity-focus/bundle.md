# EaseWise AI Studio Sync Bundle: Profile Page Parity Focus

## Handoff Summary

This is the next narrow iteration after AI Studio export `easewise-vue-sync (4).zip`.

The latest export successfully moved Four Pillars/Bazi into a usable first-result state. User testing confirms it is now close enough to the current local frontend to support further design work.

The personal center/profile area is still far from the local EaseWise H5 product state. This iteration must focus on profile parity only.

## Source Of Truth

- Local repo: `/Users/qiaoz-macmini/Projects/EaseWise`
- Local frontend root: `product/frontend`
- Local git ref: `a9d6be3`
- AI Studio export zip: `/Users/qiaoz-macmini/Downloads/easewise-vue-sync (4).zip`
- AI Studio zip sha256: `669765eb3cd58f1e4bcb4b1afeeaa315f89ff01de59940f0bce8c6ff0e4ddf02`

Local frontend behavior is authoritative. The AI Studio prototype should preserve Vue 3 + Vite and repair only the profile slice described below.

## Latest Export Status

AI Studio export 4 changed these profile-related files:

- `src/components/profile/Profile.vue`
- `src/components/profile/SystemIntro.vue`
- `src/components/profile/AmbassadorDetail.vue`

However, the profile area is still structurally divergent from local:

| File | Similarity to local | Required status |
| --- | ---: | --- |
| `Profile.vue` | 5.14% | Re-align to local personal-center structure |
| `SystemIntro.vue` | 1.78% | Rebuild as full-screen partnership/pricing manual |
| `AmbassadorDetail.vue` | 6.58% | Rebuild as formal promoter rules page |

## Do Not Disturb

Do not spend this iteration redesigning or rewriting:

- Four Pillars/Bazi analysis result pages
- Phone review waiting animation
- AI Agent bottom layout
- Global navigation
- App architecture

Those areas are either acceptable for now or outside this slice. Preserve the current working export behavior unless a profile change directly breaks the build.

## Target Files

Primary files:

- `src/components/profile/Profile.vue`
- `src/components/profile/SystemIntro.vue`
- `src/components/profile/AmbassadorDetail.vue`

Allowed support file:

- `server.ts`, only if profile demo data, ledger data, review history, or account state is missing

Do not rename routes or convert the app to another framework. Keep Vue 3 + Vite.

## Profile.vue Required State And Behavior

The profile page should be a local-equivalent personal center, not a new fantasy-style account dashboard.

### Required Composition API Dependencies

Use the local app state and helpers already exposed by the project pattern:

- `useEaseWiseApp`
- `state`
- `bootstrapApp`
- `requestRegisteredUser`
- `refreshPointsLedger`
- `refreshReviewHistory`
- `updateProfile`
- `updatePassword`
- `logout`
- `openCustomerServiceModal`
- `humanizeError`
- `resolveApiAssetUrl`

Use these only where the current AI Studio codebase already has compatible equivalents. If a helper name differs in the AI Studio export, adapt to the existing composable contract without changing the app architecture.

### Header

The local profile header includes:

- User avatar
- Avatar edit button over the avatar
- Nickname
- User identity badge
- Phone/account hint
- Guest fallback

Required copy:

- Guest nickname: `游客用户`
- Guest hint should plainly explain account limitations, not use `云端灵台` or `同修` language.

Identity labels should use the local product names:

- `普通用户`
- `推广大使`
- `VIP 推广大使`
- `SVIP 推广大使`
- `游客`

### Avatar Editing

Remove the current preset avatar strip and all remote Unsplash avatar options.

Local-equivalent behavior:

- Display avatar from `resolveApiAssetUrl(state.user?.avatar_url)`.
- Show initials or fallback when no avatar exists.
- Avatar edit button opens a hidden file input.
- Accept `image/jpeg`, `image/png`, `image/webp`.
- Reject files above 5 MB.
- Compress/resize locally before saving if the existing AI Studio code has the helper or can implement it safely.
- Save through the existing profile update path.

### Points Card

Use the local points card language and flow:

- Label: `我的积分结存`
- Amount: current service points
- Button: `去充值`

Recharge event must include the local context payload:

```ts
emit('navigate-to-tab', 'recharge', { source: 'profile', return_to: 'profile' })
```

Do not use `灵台余币`, `灵币`, or similar invented account currency labels on the profile page.

### Main Action List

Replace the current inline tabbed history/ledger section with the local compact action-list model.

Required rows:

- `合伙与推广说明书`
- `积分记录`
- `评测记录`
- `修改密码`
- `反馈问题`

Expected behavior:

- `合伙与推广说明书` opens `SystemIntro`.
- `积分记录` requires registered-user access, refreshes points ledger, then opens a modal overlay.
- `评测记录` requires registered-user access, refreshes review history, then opens a modal overlay.
- `修改密码` opens password editor overlay.
- `反馈问题` opens feedback overlay or customer service flow using the existing app helper.

Do not show `手机奇门历史 / 命盘八字历史 / 灵币账变流水` as inline tabs on the profile page.

### Modals

Keep the local modal pattern:

- profile editor modal
- password editor modal
- logout confirm modal
- points ledger modal
- review history modal
- feedback modal

Ledger and history should not be always visible in the main page body.

### Copy Constraints

Remove or avoid these current AI Studio phrases in the profile surface:

- `易客同修`
- `灵台余币`
- `云端灵台`
- `灵币账变流水`
- `灵阁`
- `修持`
- `密令`
- `玄想`

Use local plain product language instead:

- `游客用户`
- `我的积分结存`
- `去充值`
- `合伙与推广说明书`
- `积分记录`
- `评测记录`
- `修改密码`
- `反馈问题`
- `易如反掌 / EaseWise`

## SystemIntro.vue Required Direction

The current AI Studio `SystemIntro.vue` is too small and has the wrong purpose. It is an algorithm/theory introduction modal.

Rebuild it as a local-equivalent full-screen H5 flow for:

- `合伙与推广说明书`
- `商业定价与合伙提成全案`
- Service pricing
- User identity levels
- Promoter/application rules
- Commission/settlement interpretation
- Calculator/business explanation sections when practical

Required behavior:

- Full-screen mobile-first page/panel.
- Back/close button returns to Profile.
- The parent event contract must match `Profile.vue`.
- Do not present this as `易如反掌·灵台典籍` or a theoretical background modal.

The goal is not to invent new policy. Use conservative, backend-config-driven product language.

## AmbassadorDetail.vue Required Direction

The current AI Studio `AmbassadorDetail.vue` adds unsupported live business behavior.

Remove:

- fake invitation code such as `EW-AMB-xxxx`
- fake URL such as `easewise.test/claim`
- fake live commission tracking
- poster generation/download behavior
- any claim that live referral settlement is already implemented in the prototype

Rebuild it as a local-equivalent promoter rules page.

Required content:

- Title: `推广大使`
- Benefit cards:
  - `专属推广身份`
  - `邀请收益返佣`
  - `收益灵活处理`
- Threshold/rule cards:
  - `累计充值 398 元`
  - `累计充值 3980 元`
  - `以后台规则为准`
- Rules:
  - `推广身份需要用户主动申请，并由后台审核通过后生效。`
  - `推广收益只计算直邀用户，不存在团队层级收益。`
  - `返佣比例、提现门槛和结算周期以后台正式配置为准。`
  - `前台默认只展示服务积分，推广收益仅在推广大使相关页面展示。`

Use formal product-language. Do not create simulated business data that the current local product does not support.

## Demo Account Expectations

Keep the demo account matrix introduced in the last iteration unless a profile-specific adjustment is necessary:

- `13800138000`: high-points full regression account
- `13600136000`: low-points unlock-insufficient account
- `13500135000`: base-insufficient account
- `13900139000`: empty-history high-points account

For this iteration, make sure those accounts can demonstrate:

- guest profile state
- registered profile state
- points balance card
- points ledger modal
- review history modal
- empty history state
- insufficient-points state remains intact elsewhere

## Acceptance Checklist

Before exporting the next zip, verify:

- `Profile.vue`, `SystemIntro.vue`, and `AmbassadorDetail.vue` changed materially.
- Profile main page resembles the local current personal center.
- No inline history/ledger tabs remain on the main profile page.
- No preset avatar strip or Unsplash avatar options remain.
- Points card says `我的积分结存`.
- Recharge emits `{ source: 'profile', return_to: 'profile' }`.
- Ledger and review history open modal overlays.
- Guest state says `游客用户`.
- `SystemIntro.vue` is a full-screen partnership/pricing manual.
- `AmbassadorDetail.vue` is a formal promoter rules page without fake referral URL/code/poster/live commission.
- Four Pillars/Bazi current working result state is preserved.
- Vue 3 + Vite app still builds and runs.
