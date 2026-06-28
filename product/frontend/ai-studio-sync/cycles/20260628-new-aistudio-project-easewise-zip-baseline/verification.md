# Verification

## Snapshot Registration

- Source zip: `/Users/qiaoz-macmini/Downloads/easewise.zip`
- SHA256: `4e4797899bd17e0ab05875946951933fe261a16baac711fbfb04c36ea285c958`
- Extracted temp dir: `/tmp/easewise-new-project`
- Git-tracked latest snapshot updated:
  - `product/frontend/ai-studio-sync/latest/extracted/**`
  - `product/frontend/ai-studio-sync/latest/manifest.json`
  - `product/frontend/ai-studio-sync/latest/tree.txt`
  - `product/frontend/ai-studio-sync/latest/diff-from-previous.patch`

## Generated Artifacts

- `aistudio-export-summary.md`
- `gap-analysis.md`
- `local-h5-repair-bundle.md`
- `local-admin-repair-bundle.md`
- `prompt.md`
- `verification.md`

## Ignore Rules Checked

```text
.gitignore:35:.aistudio-sync/    .aistudio-sync/ledger.md
product/frontend/ai-studio-sync/.gitignore:13:*.zip    product/frontend/ai-studio-sync/latest/source.zip
```

`product/frontend/ai-studio-sync/latest/extracted/src/App.vue` produced no `git check-ignore` output, so the latest source snapshot remains trackable.

## Size Checks

```text
local-h5-repair-bundle.md       697725 bytes
local-admin-repair-bundle.md    348497 bytes
latest/extracted/src/index.css      23 bytes
latest/extracted/src/App.vue       8702 bytes
latest/diff-from-previous.patch 619473 bytes
```

The 23-byte `latest/extracted/src/index.css` is intentionally preserved as evidence of the new AI Studio export gap. The repair bundle contains the full local `src/index.css` that should be pasted into AI Studio.

## Status

This cycle is ready to send back to AI Studio:

1. Paste `prompt.md`.
2. Paste `local-h5-repair-bundle.md`.
3. Ask AI Studio to reconstruct files exactly.
4. Only paste `local-admin-repair-bundle.md` if admin parity is needed.
5. Export again and compare against this cycle before continuing design iteration.
