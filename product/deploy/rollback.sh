#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
. "$SCRIPT_DIR/lib.sh"

TARGET_NAME="production-preview"
RELEASE_ID="${1:-}"

if [[ -z "$RELEASE_ID" ]]; then
  echo "Usage: bash product/deploy/rollback.sh <release-id> [target]" >&2
  exit 1
fi

if [[ $# -ge 2 ]]; then
  TARGET_NAME="$2"
fi

load_target "$TARGET_NAME"
ensure_local_requirements
ensure_target_requirements

ssh_remote "bash -s" <<EOF
set -euo pipefail
release_id="$RELEASE_ID"
api_backup_dir="$REMOTE_BACKUP_DIR/api-\$release_id"
h5_backup_dir="$REMOTE_BACKUP_DIR/h5-\$release_id"
if [ -d "\$api_backup_dir" ]; then
  rm -rf "$REMOTE_APP_DIR.rollback"
  if [ -d "$REMOTE_APP_DIR" ]; then
    mv "$REMOTE_APP_DIR" "$REMOTE_APP_DIR.rollback"
  fi
  cp -a "\$api_backup_dir" "$REMOTE_APP_DIR"
  rm -rf "$REMOTE_APP_DIR.rollback"
  systemctl restart "$DEPLOY_SERVICE_NAME"
fi
if [ -d "\$h5_backup_dir" ]; then
  rm -rf "$REMOTE_H5_DIR.rollback"
  if [ -d "$REMOTE_H5_DIR" ]; then
    mv "$REMOTE_H5_DIR" "$REMOTE_H5_DIR.rollback"
  fi
  cp -a "\$h5_backup_dir" "$REMOTE_H5_DIR"
  rm -rf "$REMOTE_H5_DIR.rollback"
fi
curl -fsS "http://127.0.0.1:$DEPLOY_API_PORT/health"
EOF

echo "Rollback completed for release $RELEASE_ID"
