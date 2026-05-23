#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

TARGET_NAME="${1:-production-preview}"
release_id="$(date '+%Y%m%d-%H%M%S')"

"$SCRIPT_DIR/deploy-api.sh" "$TARGET_NAME" --release-id "$release_id"
"$SCRIPT_DIR/deploy-h5.sh" "$TARGET_NAME" --release-id "$release_id"
"$SCRIPT_DIR/check.sh" "$TARGET_NAME"

echo "Full deployment completed with release $release_id"
