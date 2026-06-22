# AI Studio Sync Archive

This directory stores the Git-tracked, frontend-specific archive for EaseWise AI Studio synchronization.

## Source Of Truth

- `.aistudio-sync/` at the repository root remains the local working cache for zip registration, extraction, generated prompts, and temporary analysis.
- `product/frontend/ai-studio-sync/` is the lightweight Git archive for durable frontend sync evidence.
- Local EaseWise source code remains authoritative for routes, APIs, auth, validation, state, payments, and business behavior.
- AI Studio exports are design evidence only until reviewed and merged intentionally.

## What Belongs Here

- `ledger.md`: copied sync ledger for frontend AI Studio work.
- `latest/`: latest AI Studio export manifest, tree, patch, and extracted source snapshot.
- `cycles/<timestamp>-<slice>/`: selected prompt, bundle, audit, gap analysis, export summary, verification, and other text evidence for important iterations.

## What Does Not Belong Here

- Original AI Studio zip files.
- Screenshots, videos, or other binary preview assets.
- `node_modules`, `dist`, `.vite`, or other generated dependency/build output.
- Secrets, env files, or local machine-only caches.

## Update Rule

After registering a new AI Studio zip in `.aistudio-sync/`, copy only the durable, diffable evidence into this directory. Then verify with:

```sh
git check-ignore -v product/frontend/ai-studio-sync/ledger.md
git check-ignore -v product/frontend/ai-studio-sync/latest/extracted/src/App.vue
git check-ignore -v product/frontend/ai-studio-sync/latest/source.zip
git status --short product/frontend/ai-studio-sync
```
