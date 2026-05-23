#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
. "$SCRIPT_DIR/lib.sh"

TARGET_NAME="${1:-production-preview}"
load_target "$TARGET_NAME"
ensure_local_requirements
ensure_target_requirements

echo "Internal health:"
ssh_remote "curl -fsS http://127.0.0.1:$DEPLOY_API_PORT/health"
echo
echo "Service status:"
ssh_remote "systemctl is-active $DEPLOY_SERVICE_NAME"
echo "Public entry:"
curl -fsS "$(public_web_url)" >/dev/null
echo "$(public_web_url)"
