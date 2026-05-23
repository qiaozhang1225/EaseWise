#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
. "$SCRIPT_DIR/lib.sh"

TARGET_NAME="${1:-production-preview}"
load_target "$TARGET_NAME"
ensure_local_requirements
ensure_target_requirements

tmp_dir="$(mktemp -d)"
release_id="$(new_release_id)"
remote_tmp="/tmp/easewise-bootstrap-$release_id"

write_rendered_service_file > "$tmp_dir/$DEPLOY_SERVICE_NAME.service"
write_rendered_nginx_file > "$tmp_dir/$DEPLOY_NGINX_SITE_NAME.conf"

if [[ -f "$TARGET_SERVER_ENV_FILE" ]]; then
  cp "$TARGET_SERVER_ENV_FILE" "$tmp_dir/easewise-api.env"
else
  write_default_server_env > "$tmp_dir/easewise-api.env"
fi

scp_to_remote "$SCRIPT_DIR/server/bootstrap_remote.sh" "$remote_tmp-bootstrap.sh"
scp_to_remote "$tmp_dir/$DEPLOY_SERVICE_NAME.service" "$remote_tmp.service"
scp_to_remote "$tmp_dir/$DEPLOY_NGINX_SITE_NAME.conf" "$remote_tmp.nginx.conf"
scp_to_remote "$tmp_dir/easewise-api.env" "$remote_tmp.env"

ssh_remote "bash -s" <<EOF
set -euo pipefail
mkdir -p "$remote_tmp"
mv "$remote_tmp-bootstrap.sh" "$remote_tmp/bootstrap_remote.sh"
mv "$remote_tmp.service" "$remote_tmp/service.conf"
mv "$remote_tmp.nginx.conf" "$remote_tmp/nginx.conf"
mv "$remote_tmp.env" "$remote_tmp/easewise-api.env"
bash "$remote_tmp/bootstrap_remote.sh" \
  "$DEPLOY_APP_ROOT" \
  "$DEPLOY_SERVICE_NAME" \
  "$DEPLOY_NGINX_SITE_NAME" \
  "$REMOTE_SERVICE_ENV_PATH" \
  "$DEPLOY_WEB_MODE"
rm -rf "$remote_tmp"
EOF

rm -rf "$tmp_dir"
echo "Server bootstrap completed for $TARGET_NAME"
echo "Preview URL: $(public_web_url)"
