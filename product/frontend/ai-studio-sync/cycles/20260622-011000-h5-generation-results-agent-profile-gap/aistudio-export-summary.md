# AI Studio Export Summary

- Source zip: `.aistudio-sync/aistudio-latest/source.zip`
- SHA256: `163b0b5f462afe2c3fa43ee55d00eafed2fc82f6378b40fd25e9da6f27b3d8e0`
- Extracted files: 34
- Text files scanned: 32

## Diff From Previous AI Studio Export

- Added text files: 0
- Removed text files: 0
- Changed text files: 2
- Patch: `.aistudio-sync/aistudio-latest/diff-from-previous.patch`

### Added
_None found._

### Removed
_None found._

### Changed
- `server.ts`
- `src/components/four-pillars/FourPillarsAnalysis.vue`

## Tree Excerpt

```text
.env.example
.gitignore
README.md
assets/
assets/.aistudio/
assets/.aistudio/.gitignore
index.html
metadata.json
package-lock.json
package.json
server.ts
src/
src/App.vue
src/components/
src/components/admin/
src/components/admin/AdminWorkspace.vue
src/components/ai-agent/
src/components/ai-agent/AIAgent.vue
src/components/analysis/
src/components/analysis/Analysis.vue
src/components/auth/
src/components/auth/AuthModal.vue
src/components/four-pillars/
src/components/four-pillars/FourPillarsAnalysis.vue
src/components/four-pillars/FourPillarsNatalTable.vue
src/components/home/
src/components/home/Home.vue
src/components/layout/
src/components/layout/BottomNav.vue
src/components/layout/Header.vue
src/components/points-claim/
src/components/points-claim/PointsClaimPage.vue
src/components/profile/
src/components/profile/Profile.vue
src/components/recharge/
src/components/recharge/RechargePage.vue
src/components/support/
src/components/support/ContactServiceModal.vue
src/composables/
src/composables/useEaseWiseApp.ts
src/composables/useVoicePlayback.ts
src/config/
src/config/pricing.ts
src/constants/
src/constants/storage.ts
src/index.css
src/lib/
src/lib/api.ts
src/main.ts
src/types/
src/types/api.ts
src/vite-env.d.ts
tsconfig.json
vite.config.ts
```

## Detected Pages

- `src/App.vue`
- `src/components/points-claim/PointsClaimPage.vue`
- `src/components/recharge/RechargePage.vue`

## Detected Components

- `src/components/admin/AdminWorkspace.vue`
- `src/components/ai-agent/AIAgent.vue`
- `src/components/analysis/Analysis.vue`
- `src/components/auth/AuthModal.vue`
- `src/components/four-pillars/FourPillarsAnalysis.vue`
- `src/components/four-pillars/FourPillarsNatalTable.vue`
- `src/components/home/Home.vue`
- `src/components/layout/BottomNav.vue`
- `src/components/layout/Header.vue`
- `src/components/points-claim/PointsClaimPage.vue`
- `src/components/profile/Profile.vue`
- `src/components/recharge/RechargePage.vue`
- `src/components/support/ContactServiceModal.vue`

## Behavior-Like Sources To Review Carefully

- `src/components/auth/AuthModal.vue`
- `src/components/support/ContactServiceModal.vue`
- `src/lib/api.ts`
- `src/types/api.ts`

## Mock Or Demo Sources

- `.env.example`

## State Signals

{
  "auth": 10,
  "permission": 1,
  "empty": 2,
  "error": 13,
  "success": 5,
  "disabled": 11,
  "login": 7,
  "payment": 5,
  "invalid": 3,
  "loading": 6,
  "expired": 1
}

## Local Sync Warning

This zip is authoritative for AI Studio's latest design output only. Do not copy its business logic, routing, API fields, auth, validation, payment, persistence, or state-management assumptions directly into the local app.
