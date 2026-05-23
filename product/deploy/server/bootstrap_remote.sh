#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="$1"
SERVICE_NAME="$2"
NGINX_SITE_NAME="$3"
SERVICE_ENV_PATH="$4"
WEB_MODE="$5"
WORK_DIR="$(cd "$(dirname "$0")" && pwd)"

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y python3-venv python3-pip nginx

mkdir -p "$APP_ROOT/app" "$APP_ROOT/shared" "$APP_ROOT/www" "$APP_ROOT/backup" "$APP_ROOT/staging"
if [[ ! -d "$APP_ROOT/venv" ]]; then
  python3 -m venv "$APP_ROOT/venv"
fi
"$APP_ROOT/venv/bin/pip" install --upgrade pip

install -m 644 "$WORK_DIR/service.conf" "/etc/systemd/system/$SERVICE_NAME.service"
install -m 644 "$WORK_DIR/nginx.conf" "/etc/nginx/sites-available/$NGINX_SITE_NAME"
ln -sf "/etc/nginx/sites-available/$NGINX_SITE_NAME" "/etc/nginx/sites-enabled/$NGINX_SITE_NAME"

if [[ "$WEB_MODE" == "root" && -e /etc/nginx/sites-enabled/phoneqimen-api ]]; then
  rm -f /etc/nginx/sites-enabled/phoneqimen-api
fi

install -m 600 "$WORK_DIR/easewise-api.env" "$SERVICE_ENV_PATH"

systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME" || true
nginx -t
systemctl restart nginx
