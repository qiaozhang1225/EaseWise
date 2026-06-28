# New AI Studio Project Export Summary

- Source zip: `/Users/qiaoz-macmini/Downloads/easewise.zip`
- SHA256: `4e4797899bd17e0ab05875946951933fe261a16baac711fbfb04c36ea285c958`
- Extracted temp dir: `/tmp/easewise-new-project`
- Export file count: `34`

## File Tree

```text
.env.example
.gitignore
README.md
assets/.aistudio/.gitignore
index.html
metadata.json
package.json
server.ts
src/App.vue
src/components/admin/AdminWorkspace.vue
src/components/ai-agent/AIAgent.vue
src/components/analysis/Analysis.vue
src/components/auth/AuthModal.vue
src/components/bazi/BaziAnalysis.vue
src/components/four-pillars/mockLocations.ts
src/components/home/Home.vue
src/components/layout/BottomNav.vue
src/components/layout/Header.vue
src/components/meihua/MeihuaAnalysis.vue
src/components/points-claim/PointsClaimPage.vue
src/components/profile/Profile.vue
src/components/recharge/RechargePage.vue
src/components/support/ContactServiceModal.vue
src/composables/useEaseWiseApp.ts
src/composables/useVoicePlayback.ts
src/config/pricing.ts
src/constants/storage.ts
src/index.css
src/lib/api.ts
src/main.ts
src/types/api.ts
src/vite-env.d.ts
tsconfig.json
vite.config.ts
```

## Immediate Findings

- `src/index.css` is only 23 bytes: `@import "tailwindcss";`. All EaseWise theme tokens, font declarations, global body style, hidden-scrollbar rules, and icon animations are missing.
- The new project routes `bazi` to `src/components/bazi/BaziAnalysis.vue`, while the current local frontend routes `bazi` to `src/components/four-pillars/FourPillarsAnalysis.vue` and also uses `FourPillarsNatalTable.vue`.
- Several current local components are missing from the new project export: AdminSelect, FourPillarsAnalysis, FourPillarsNatalTable, AmbassadorDetail, SystemIntro.
- Many shared files differ materially: App.vue, API client, types, useEaseWiseApp, Analysis, Profile, Recharge, PointsClaim, Meihua, etc.

## Local Only Files To Restore

```text
src/components/admin/AdminSelect.vue
src/components/four-pillars/FourPillarsAnalysis.vue
src/components/four-pillars/FourPillarsNatalTable.vue
src/components/profile/AmbassadorDetail.vue
src/components/profile/SystemIntro.vue
```

## Remote Only Files To Classify

```text
README.md
assets/.aistudio/.gitignore
metadata.json
server.ts
src/components/bazi/BaziAnalysis.vue
src/components/four-pillars/mockLocations.ts
```

## Common Files With Different Content

```text
.env.example	remote=445	local=116
index.html	remote=310	local=298
package.json	remote=890	local=770
src/App.vue	remote=8702	local=8846
src/components/admin/AdminWorkspace.vue	remote=1210	local=348028
src/components/ai-agent/AIAgent.vue	remote=10339	local=13492
src/components/analysis/Analysis.vue	remote=24945	local=114609
src/components/auth/AuthModal.vue	remote=19266	local=22416
src/components/home/Home.vue	remote=24635	local=19656
src/components/layout/BottomNav.vue	remote=1449	local=1422
src/components/layout/Header.vue	remote=1342	local=1288
src/components/meihua/MeihuaAnalysis.vue	remote=11114	local=25422
src/components/points-claim/PointsClaimPage.vue	remote=10256	local=21294
src/components/profile/Profile.vue	remote=14095	local=48184
src/components/recharge/RechargePage.vue	remote=11615	local=36568
src/components/support/ContactServiceModal.vue	remote=5768	local=6546
src/composables/useEaseWiseApp.ts	remote=26838	local=34993
src/composables/useVoicePlayback.ts	remote=17385	local=17125
src/index.css	remote=23	local=2785
src/lib/api.ts	remote=32074	local=48164
src/types/api.ts	remote=23646	local=37104
src/vite-env.d.ts	remote=189	local=186
tsconfig.json	remote=508	local=484
vite.config.ts	remote=1117	local=1120
```
