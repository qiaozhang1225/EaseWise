#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
. "$SCRIPT_DIR/lib.sh"

TARGET_NAME="production-preview"
RELEASE_ID=""
SYNC_ENV=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --release-id)
      RELEASE_ID="$2"
      shift 2
      ;;
    --sync-env)
      SYNC_ENV=1
      shift
      ;;
    *)
      TARGET_NAME="$1"
      shift
      ;;
  esac
done

load_target "$TARGET_NAME"
ensure_local_requirements
ensure_target_requirements

release_id="${RELEASE_ID:-$(new_release_id)}"
tmp_dir="$(mktemp -d)"
tarball="$tmp_dir/easewise-api-$release_id.tgz"
remote_tarball="/tmp/easewise-api-$release_id.tgz"

export COPYFILE_DISABLE=1
tar \
  --exclude='product/backend/api/data' \
  --exclude='product/backend/api/static/uploads' \
  --exclude='product/backend/api/static/voice/*.mp3' \
  --exclude='*/__pycache__' \
  --exclude='*.pyc' \
  --exclude='.DS_Store' \
  -czf "$tarball" -C "$REPO_ROOT" README.md features product/backend
scp_to_remote "$tarball" "$remote_tarball"

if [[ $SYNC_ENV -eq 1 && -f "$TARGET_SERVER_ENV_FILE" ]]; then
  scp_to_remote "$TARGET_SERVER_ENV_FILE" "$REMOTE_SERVICE_ENV_PATH"
fi

ssh_remote "bash -s" <<EOF
set -euo pipefail
release_id="$release_id"
app_root="$DEPLOY_APP_ROOT"
app_dir="$REMOTE_APP_DIR"
backup_dir="$REMOTE_BACKUP_DIR/api-\$release_id"
stage_dir="$REMOTE_STAGING_DIR/api-\$release_id"
mkdir -p "$REMOTE_BACKUP_DIR" "$REMOTE_STAGING_DIR" "$REMOTE_SHARED_DIR"
rm -rf "\$stage_dir"
mkdir -p "\$stage_dir"
if [ -d "\$app_dir" ]; then
  rm -rf "\$backup_dir"
  cp -a "\$app_dir" "\$backup_dir"
fi
tar -xzf "$remote_tarball" -C "\$stage_dir"
$REMOTE_VENV_DIR/bin/python3 - <<'PY'
from pathlib import Path
for path in Path("$REMOTE_STAGING_DIR").rglob("._*"):
    if path.is_file():
        path.unlink()
PY
$REMOTE_VENV_DIR/bin/pip install -r "\$stage_dir/product/backend/api/requirements.txt"
rm -rf "\$app_dir.previous"
if [ -d "\$app_dir" ]; then
  mv "\$app_dir" "\$app_dir.previous"
fi
mv "\$stage_dir" "\$app_dir"
rm -rf "\$app_dir.previous"
systemctl restart "$DEPLOY_SERVICE_NAME"
for _ in \$(seq 1 20); do
  if curl -fsS "http://127.0.0.1:$DEPLOY_API_PORT/health" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done
curl -fsS "http://127.0.0.1:$DEPLOY_API_PORT/health"
rm -f "$remote_tarball"
python3 - <<'PY'
import json
from pathlib import Path

release_id = "$release_id"
path = Path("$REMOTE_BACKUP_DIR") / f"release-{release_id}.json"
payload = {
    "release_id": release_id,
    "api_backup_dir": str(Path("$REMOTE_BACKUP_DIR") / f"api-{release_id}"),
    "h5_backup_dir": None,
    "service_name": "$DEPLOY_SERVICE_NAME",
}
path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print(path)
PY
EOF

rm -rf "$tmp_dir"
echo "API deployed with release $release_id"
