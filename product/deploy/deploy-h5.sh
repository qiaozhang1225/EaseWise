#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
. "$SCRIPT_DIR/lib.sh"

TARGET_NAME="production-preview"
RELEASE_ID=""
SKIP_BUILD=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --release-id)
      RELEASE_ID="$2"
      shift 2
      ;;
    --skip-build)
      SKIP_BUILD=1
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
frontend_dir="$REPO_ROOT/product/frontend"
dist_dir="$frontend_dir/dist"
tmp_dir="$(mktemp -d)"
tarball="$tmp_dir/easewise-h5-$release_id.tgz"
remote_tarball="/tmp/easewise-h5-$release_id.tgz"

if [[ $SKIP_BUILD -eq 0 ]]; then
  pushd "$frontend_dir" >/dev/null
  prepare_frontend_build_env
  npm run build
  popd >/dev/null
fi

if [[ ! -d "$dist_dir" ]]; then
  echo "Missing frontend dist directory: $dist_dir" >&2
  exit 1
fi

export COPYFILE_DISABLE=1
tar -czf "$tarball" -C "$dist_dir" .
scp_to_remote "$tarball" "$remote_tarball"

ssh_remote "bash -s" <<EOF
set -euo pipefail
release_id="$release_id"
h5_dir="$REMOTE_H5_DIR"
backup_dir="$REMOTE_BACKUP_DIR/h5-\$release_id"
stage_dir="$REMOTE_STAGING_DIR/h5-\$release_id"
mkdir -p "$REMOTE_BACKUP_DIR" "$REMOTE_STAGING_DIR"
rm -rf "\$stage_dir"
mkdir -p "\$stage_dir"
if [ -d "\$h5_dir" ]; then
  rm -rf "\$backup_dir"
  cp -a "\$h5_dir" "\$backup_dir"
fi
tar -xzf "$remote_tarball" -C "\$stage_dir"
python3 - <<'PY'
from pathlib import Path
for path in Path("$REMOTE_STAGING_DIR").rglob("._*"):
    if path.is_file():
        path.unlink()
PY
rm -rf "\$h5_dir.previous"
if [ -d "\$h5_dir" ]; then
  mv "\$h5_dir" "\$h5_dir.previous"
fi
mkdir -p "$(dirname "$REMOTE_H5_DIR")"
mv "\$stage_dir" "\$h5_dir"
rm -rf "\$h5_dir.previous"
rm -f "$remote_tarball"
python3 - <<'PY'
import json
from pathlib import Path

release_id = "$release_id"
path = Path("$REMOTE_BACKUP_DIR") / f"release-{release_id}.json"
if path.exists():
    payload = json.loads(path.read_text(encoding="utf-8"))
else:
    payload = {"release_id": release_id, "api_backup_dir": None}
payload["release_id"] = release_id
payload["h5_backup_dir"] = str(Path("$REMOTE_BACKUP_DIR") / f"h5-{release_id}")
path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print(path)
PY
EOF

rm -rf "$tmp_dir"
echo "H5 deployed with release $release_id"
echo "Public URL: $(public_web_url)"
