#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
. "$SCRIPT_DIR/lib.sh"

TARGET_NAME="${1:-production}"
load_target "$TARGET_NAME"
ensure_local_requirements
ensure_target_requirements

ssh_remote "bash -s" <<'EOF'
set -euo pipefail

systemctl stop phoneqimen-api 2>/dev/null || true
systemctl disable phoneqimen-api 2>/dev/null || true
rm -f /etc/systemd/system/phoneqimen-api.service
systemctl daemon-reload

rm -f /etc/nginx/sites-enabled/phoneqimen-api
rm -f /etc/nginx/sites-available/phoneqimen-api
rm -f /etc/nginx/sites-available/phoneqimen-api.bak-*
rm -f /etc/phoneqimen-api.env

rm -rf /opt/phoneqimen

nginx -t
systemctl restart nginx
EOF

echo "Legacy PhoneQimen cleanup completed."
