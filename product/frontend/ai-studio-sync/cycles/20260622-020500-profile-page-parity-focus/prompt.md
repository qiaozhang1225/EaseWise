# Prompt For AI Studio

You are working on the EaseWise Vue 3 + Vite H5 prototype. Please perform a narrow profile-page parity repair based on the attached bundle.

Important context:

- The latest export made Four Pillars/Bazi usable enough for further design work.
- Do not rework Four Pillars, phone review waiting flow, AI Agent layout, global navigation, or the app architecture in this iteration.
- The personal center/profile area is still far from the local EaseWise H5 product state.
- Keep Vue 3 + Vite intact.

Please focus only on:

- `src/components/profile/Profile.vue`
- `src/components/profile/SystemIntro.vue`
- `src/components/profile/AmbassadorDetail.vue`
- `server.ts` only if profile demo data, ledger records, review history, or account state are missing

## Required Profile.vue Repair

Rebuild the profile main page toward the local current personal-center structure.

Use plain local product/account language:

- `游客用户`
- `我的积分结存`
- `去充值`
- `合伙与推广说明书`
- `积分记录`
- `评测记录`
- `修改密码`
- `反馈问题`
- `易如反掌 / EaseWise`

Remove the current fantasy-style profile copy such as:

- `易客同修`
- `灵台余币`
- `云端灵台`
- `灵币账变流水`
- `灵阁`
- `修持`
- `密令`
- `玄想`

Replace the current inline history/ledger tabs with the local action-list model:

- `合伙与推广说明书`
- `积分记录`
- `评测记录`
- `修改密码`
- `反馈问题`

`积分记录` and `评测记录` must open protected modal overlays. They should not be inline tabs on the main page.

The points card must say `我的积分结存`, and the recharge button must emit:

```ts
emit('navigate-to-tab', 'recharge', { source: 'profile', return_to: 'profile' })
```

Remove the preset avatar strip and remote Unsplash avatar options. Avatar editing should follow the local file-input pattern: resolve existing avatar URL, show fallback initials, accept jpeg/png/webp, reject files above 5 MB, and save through the existing profile update flow.

Keep local-equivalent modals for:

- profile editor
- password editor
- logout confirm
- points ledger
- review history
- feedback

## Required SystemIntro.vue Repair

The current AI Studio `SystemIntro.vue` is a small algorithm/theory modal. That is not the current local product page.

Rebuild it as a full-screen mobile-first H5 page/panel for:

- `合伙与推广说明书`
- `商业定价与合伙提成全案`
- service pricing
- user identity levels
- promoter/application rules
- commission/settlement interpretation
- calculator/business explanation sections if practical

It should close/back cleanly into `Profile.vue` using a consistent parent event contract.

Do not present this page as `易如反掌·灵台典籍`, and do not make it primarily about algorithm source/theory.

## Required AmbassadorDetail.vue Repair

Remove unsupported simulated business behavior:

- fake invitation code such as `EW-AMB-xxxx`
- fake URL such as `easewise.test/claim`
- fake live commission tracking
- fake poster download/generation

Rebuild it as a formal promoter rules page.

Required content:

- title: `推广大使`
- benefit cards: `专属推广身份`, `邀请收益返佣`, `收益灵活处理`
- threshold/rule cards: `累计充值 398 元`, `累计充值 3980 元`, `以后台规则为准`
- rules:
  - `推广身份需要用户主动申请，并由后台审核通过后生效。`
  - `推广收益只计算直邀用户，不存在团队层级收益。`
  - `返佣比例、提现门槛和结算周期以后台正式配置为准。`
  - `前台默认只展示服务积分，推广收益仅在推广大使相关页面展示。`

Use conservative, backend-rule-driven wording. Do not invent live referral settlement behavior.

## Preserve Existing Working Areas

Keep the demo accounts from the previous iteration:

- `13800138000`: high-points full regression account
- `13600136000`: low-points unlock-insufficient account
- `13500135000`: base-insufficient account
- `13900139000`: empty-history high-points account

Make sure the profile page can demonstrate:

- guest state
- registered state
- points balance card
- points ledger modal
- review history modal
- empty history state
- profile edit
- password edit
- logout confirmation

Do not break insufficient-points behavior elsewhere.

## Acceptance Criteria

Before returning the next zip:

- `Profile.vue`, `SystemIntro.vue`, and `AmbassadorDetail.vue` are materially repaired.
- The profile main page no longer has inline history/ledger tabs.
- The page no longer has preset Unsplash avatar choices.
- The points card says `我的积分结存`.
- The recharge button emits the full local context payload.
- Guest state uses `游客用户`.
- `SystemIntro.vue` is a full-screen partnership/pricing manual.
- `AmbassadorDetail.vue` is a formal promoter rules page with no fake referral URL, fake invitation code, fake live commission, or fake poster download.
- Four Pillars/Bazi current working result state is preserved.
- The Vue 3 + Vite app still builds and runs.
