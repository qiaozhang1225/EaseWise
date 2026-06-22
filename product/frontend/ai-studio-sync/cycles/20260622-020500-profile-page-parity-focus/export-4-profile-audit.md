# AI Studio Export 4 Profile Audit

- Date: 2026-06-22
- Repo: `/Users/qiaoz-macmini/Projects/EaseWise`
- Local frontend root: `product/frontend`
- AI Studio export zip: `/Users/qiaoz-macmini/Downloads/easewise-vue-sync (4).zip`
- AI Studio zip sha256: `669765eb3cd58f1e4bcb4b1afeeaa315f89ff01de59940f0bce8c6ff0e4ddf02`
- Local git ref: `a9d6be3`

## User-Tested Status

The latest AI Studio export moved Four Pillars/Bazi into an acceptable first-result state. It is now close enough to the current local frontend to allow the next design pass.

The personal center/profile area is still far from the current local product state and should be the next narrow iteration.

## Export 4 Changes Claimed By AI Studio

AI Studio reported the following profile-related work:

- Added `src/components/profile/SystemIntro.vue`
- Added `src/components/profile/AmbassadorDetail.vue`
- Changed `src/components/profile/Profile.vue`
- Added an introduction modal for EaseWise theoretical background
- Added a promoter hub with referral invitation codes, live commission tracking, and poster generation
- Updated demo account matrix in `server.ts`

## Structural Similarity Snapshot

The code-level comparison shows that the profile implementation is still a rewrite rather than a close match to the local source of truth:

| File | Similarity | Local size | AI Studio size | Status |
| --- | ---: | ---: | ---: | --- |
| `src/components/profile/Profile.vue` | 5.14% | 43084 | 26758 | Still highly divergent |
| `src/components/profile/SystemIntro.vue` | 1.78% | 36602 | 2747 | Wrong product purpose and layout |
| `src/components/profile/AmbassadorDetail.vue` | 6.58% | 8318 | 5606 | Invented promoter behavior |

## Main Gaps

### 1. Profile.vue still uses the wrong product language

AI Studio currently uses copy such as:

- `灵台余币`
- `易客同修`
- `云端灵台`
- `灵币账变流水`
- `同修反馈`
- `修持`, `密令`, `灵阁`

The current local product uses plainer product/account language in the profile surface:

- `游客用户`
- `我的积分结存`
- `去充值`
- `合伙与推广说明书`
- `积分记录`
- `评测记录`
- `修改密码`
- `反馈问题`
- `易如反掌 / EaseWise`

The next iteration should remove invented metaphysical UI copy from the profile page unless it already appears in the local file.

### 2. Profile.vue uses the wrong interaction model

AI Studio currently places history and ledger content inline with tabs:

- `手机奇门历史`
- `命盘八字历史`
- `灵币账变流水`

The local profile page uses a compact personal-center action list. Ledger and history open protected modals, not inline tabs.

Required local-equivalent action rows:

- `合伙与推广说明书`
- `积分记录`
- `评测记录`
- `修改密码`
- `反馈问题`

### 3. Avatar editing is wrong

AI Studio currently includes a preset avatar strip with remote Unsplash images. The local profile does not work this way.

Local behavior:

- The avatar resolves `state.user?.avatar_url` through `resolveApiAssetUrl`.
- The avatar edit button opens a file input.
- Upload accepts `jpeg/png/webp`, validates max size, compresses to a data URL, and saves through `updateProfile`.
- Guest state keeps account actions available only through the correct guarded flows.

### 4. Recharge event payload is incomplete

AI Studio currently emits only:

```ts
emit('navigate-to-tab', 'recharge')
```

Local behavior includes the source and return context:

```ts
emit('navigate-to-tab', 'recharge', { source: 'profile', return_to: 'profile' })
```

### 5. SystemIntro.vue has the wrong purpose

AI Studio created a small theoretical-background modal about algorithms and source traditions.

Local `SystemIntro.vue` is a full-screen H5 flow for:

- `合伙与推广说明书`
- `商业定价与合伙提成全案`
- Service pricing
- User identity levels
- Promoter/application rules
- Calculator/business interpretation sections

The next iteration should rebuild `SystemIntro.vue` toward the local full-screen partnership/pricing manual, not an algorithm-theory modal.

### 6. AmbassadorDetail.vue invents unsupported behavior

AI Studio currently includes:

- fake invite code such as `EW-AMB-xxxx`
- fake claim URL such as `easewise.test/claim`
- fake live commission stats
- poster generation/download behavior

The local product does not currently expose those as working product contracts. The local promoter page is a formal rules page with conservative, backend-driven language.

Required local-equivalent promoter content:

- title: `推广大使`
- benefit cards: `专属推广身份`, `邀请收益返佣`, `收益灵活处理`
- thresholds: `累计充值 398 元`, `累计充值 3980 元`, `以后台规则为准`
- rules:
  - `推广身份需要用户主动申请，并由后台审核通过后生效。`
  - `推广收益只计算直邀用户，不存在团队层级收益。`
  - `返佣比例、提现门槛和结算周期以后台正式配置为准。`
  - `前台默认只展示服务积分，推广收益仅在推广大使相关页面展示。`

## Next Iteration Scope

Only repair the profile area:

- `src/components/profile/Profile.vue`
- `src/components/profile/SystemIntro.vue`
- `src/components/profile/AmbassadorDetail.vue`
- `server.ts` only if needed to support profile demo data, ledger records, review history, or account state

Do not rework Four Pillars, phone review waiting flow, or AI Agent bottom spacing in this iteration unless the build is broken by profile changes.

## Acceptance Criteria

- Profile main page visually and structurally resembles the local current profile page.
- No inline history/ledger tabs on the main profile page.
- `积分记录` and `评测记录` open protected modal overlays.
- No preset avatar strip and no remote Unsplash avatar options.
- Avatar edit uses a local file input pattern.
- Points card label is `我的积分结存`.
- Recharge button emits `navigate-to-tab` with `{ source: 'profile', return_to: 'profile' }`.
- Guest state uses `游客用户` and plain account/product copy.
- `SystemIntro.vue` is a full-screen partnership/pricing manual, not an algorithm source modal.
- `AmbassadorDetail.vue` removes fake referral code, fake live commission, fake poster download, and fake claim URL.
- Four Pillars current workable result state is preserved.
- Vue 3 + Vite architecture remains intact.
