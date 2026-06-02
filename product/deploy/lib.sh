#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PRODUCT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

TARGET=""
TARGET_FILE=""
TARGET_SERVER_ENV_FILE=""
DEPLOY_HOST=""
DEPLOY_PORT=""
DEPLOY_USER=""
DEPLOY_KEY_PATH=""
DEPLOY_APP_ROOT=""
DEPLOY_SERVICE_NAME=""
DEPLOY_WEB_MODE=""
DEPLOY_WEB_PORT=""
DEPLOY_API_PORT=""
DEPLOY_SERVER_NAME=""
DEPLOY_PUBLIC_BASE_URL=""
DEPLOY_FRONTEND_API_BASE=""
REMOTE_APP_DIR=""
REMOTE_H5_DIR=""
REMOTE_SHARED_DIR=""
REMOTE_BACKUP_DIR=""
REMOTE_STAGING_DIR=""
REMOTE_VENV_DIR=""
REMOTE_SERVICE_ENV_PATH=""
DEPLOY_NGINX_SITE_NAME=""

trim() {
  local value="$1"
  value="${value#"${value%%[![:space:]]*}"}"
  value="${value%"${value##*[![:space:]]}"}"
  printf '%s' "$value"
}

resolve_path() {
  python3 - "$1" "$REPO_ROOT" <<'PY'
import os
import sys

path = sys.argv[1]
repo_root = sys.argv[2]
if os.path.isabs(path):
    print(os.path.abspath(path))
else:
    print(os.path.abspath(os.path.join(repo_root, path)))
PY
}

source_env_file() {
  local env_file="$1"
  while IFS= read -r raw_line || [[ -n "$raw_line" ]]; do
    local line
    line="$(trim "$raw_line")"
    if [[ -z "$line" || "${line:0:1}" == "#" ]]; then
      continue
    fi
    local key="${line%%=*}"
    local value=""
    if [[ "$line" == *"="* ]]; then
      value="${line#*=}"
    fi
    key="$(trim "$key")"
    value="$(trim "$value")"
    value="${value%\"}"
    value="${value#\"}"
    value="${value%\'}"
    value="${value#\'}"
    export "$key=$value"
  done < "$env_file"
}

load_target() {
  TARGET="${1:-production-preview}"
  TARGET_FILE="$SCRIPT_DIR/targets/${TARGET}.env"
  TARGET_SERVER_ENV_FILE="$SCRIPT_DIR/targets/${TARGET}.server.env"
  if [[ ! -f "$TARGET_FILE" ]]; then
    echo "Missing deploy target: $TARGET_FILE" >&2
    exit 1
  fi

  source_env_file "$TARGET_FILE"

  DEPLOY_HOST="${DEPLOY_HOST:-}"
  DEPLOY_PORT="${DEPLOY_PORT:-22}"
  DEPLOY_USER="${DEPLOY_USER:-root}"
  DEPLOY_KEY_PATH="$(resolve_path "${DEPLOY_KEY_PATH:-./NonProductive.pem}")"
  DEPLOY_APP_ROOT="${DEPLOY_APP_ROOT:-/opt/easewise}"
  DEPLOY_SERVICE_NAME="${DEPLOY_SERVICE_NAME:-easewise-api}"
  DEPLOY_WEB_MODE="${DEPLOY_WEB_MODE:-preview}"
  DEPLOY_WEB_PORT="${DEPLOY_WEB_PORT:-8080}"
  DEPLOY_API_PORT="${DEPLOY_API_PORT:-8010}"
  DEPLOY_SERVER_NAME="${DEPLOY_SERVER_NAME:-_}"
  DEPLOY_PUBLIC_BASE_URL="${DEPLOY_PUBLIC_BASE_URL:-}"
  DEPLOY_FRONTEND_API_BASE="${DEPLOY_FRONTEND_API_BASE:-}"
  DEPLOY_NGINX_SITE_NAME="${DEPLOY_NGINX_SITE_NAME:-easewise-$DEPLOY_WEB_MODE}"
  REMOTE_APP_DIR="$DEPLOY_APP_ROOT/app"
  REMOTE_H5_DIR="$DEPLOY_APP_ROOT/www/h5"
  REMOTE_SHARED_DIR="$DEPLOY_APP_ROOT/shared"
  REMOTE_BACKUP_DIR="$DEPLOY_APP_ROOT/backup"
  REMOTE_STAGING_DIR="$DEPLOY_APP_ROOT/staging"
  REMOTE_VENV_DIR="$DEPLOY_APP_ROOT/venv"
  REMOTE_SERVICE_ENV_PATH="${DEPLOY_SERVICE_ENV_PATH:-/etc/easewise-api.env}"
}

require_command() {
  local command_name="$1"
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "Missing required command: $command_name" >&2
    exit 1
  fi
}

ensure_local_requirements() {
  add_local_node_bin_to_path
  require_command ssh
  require_command scp
  require_command tar
  require_command python3
}

add_local_node_bin_to_path() {
  if command -v node >/dev/null 2>&1 && command -v npm >/dev/null 2>&1; then
    return
  fi

  local candidate_globs=(
    "$HOME/.local/node/node-v*/bin"
    "$HOME/.openclaw/tools/node/node-v*/bin"
  )
  local candidate_dir=""
  local matched=0
  for candidate_dir in "${candidate_globs[@]}"; do
    for expanded_dir in $candidate_dir; do
      if [[ -x "$expanded_dir/node" && -x "$expanded_dir/npm" ]]; then
        export PATH="$expanded_dir:$PATH"
        matched=1
        break
      fi
    done
    if [[ $matched -eq 1 ]]; then
      break
    fi
  done
}

ensure_target_requirements() {
  local missing=()
  [[ -n "$DEPLOY_HOST" ]] || missing+=("DEPLOY_HOST")
  [[ -n "$DEPLOY_USER" ]] || missing+=("DEPLOY_USER")
  [[ -n "$DEPLOY_KEY_PATH" ]] || missing+=("DEPLOY_KEY_PATH")
  [[ -f "$DEPLOY_KEY_PATH" ]] || missing+=("DEPLOY_KEY_PATH(file)")
  [[ -n "$DEPLOY_APP_ROOT" ]] || missing+=("DEPLOY_APP_ROOT")
  [[ -n "$DEPLOY_SERVICE_NAME" ]] || missing+=("DEPLOY_SERVICE_NAME")
  if [[ "${#missing[@]}" -gt 0 ]]; then
    printf 'Missing deploy config: %s\n' "${missing[*]}" >&2
    exit 1
  fi
}

ssh_target() {
  printf '%s@%s' "$DEPLOY_USER" "$DEPLOY_HOST"
}

ssh_remote() {
  ssh -p "$DEPLOY_PORT" -o StrictHostKeyChecking=accept-new -i "$DEPLOY_KEY_PATH" "$(ssh_target)" "$@"
}

scp_to_remote() {
  local local_path="$1"
  local remote_path="$2"
  scp -P "$DEPLOY_PORT" -o StrictHostKeyChecking=accept-new -i "$DEPLOY_KEY_PATH" "$local_path" "$(ssh_target):$remote_path"
}

new_release_id() {
  date '+%Y%m%d-%H%M%S'
}

public_web_url() {
  if [[ -n "$DEPLOY_PUBLIC_BASE_URL" ]]; then
    printf '%s' "${DEPLOY_PUBLIC_BASE_URL%/}"
    return
  fi
  if [[ "$DEPLOY_WEB_MODE" == "preview" ]]; then
    printf 'http://%s:%s' "$DEPLOY_HOST" "$DEPLOY_WEB_PORT"
    return
  fi
  printf 'http://%s' "$DEPLOY_HOST"
}

prepare_frontend_build_env() {
  export VITE_APP_BASE_PATH="${VITE_APP_BASE_PATH:-/}"
  if [[ -n "$DEPLOY_FRONTEND_API_BASE" ]]; then
    export VITE_API_BASE_URL="$DEPLOY_FRONTEND_API_BASE"
  else
    unset VITE_API_BASE_URL || true
  fi
}

write_default_server_env() {
  cat <<EOF
EASEWISE_DB_PATH=$REMOTE_SHARED_DIR/app.db
EASEWISE_CORS_ORIGINS=*
EASEWISE_INITIAL_POINTS=10000
EASEWISE_PHONE_REVIEW_BASE_POINTS_COST=100
EASEWISE_AUTH_TOKEN_TTL_HOURS=720
EASEWISE_ALLOW_MOCK_WECHAT_LOGIN=0
EASEWISE_WECHAT_APP_ID=
EASEWISE_WECHAT_APP_SECRET=
EASEWISE_WECHAT_OA_APP_ID=
EASEWISE_WECHAT_OA_APP_SECRET=
EASEWISE_PUBLIC_BASE_URL=$(public_web_url)
EASEWISE_INTERNAL_ADMIN_TOKEN=
DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-pro
DEEPSEEK_TIMEOUT_SECONDS=120
DEEPSEEK_TEMPERATURE=0.3
EASEWISE_REVIEW_RENDER_STRATEGY=batched
EASEWISE_REVIEW_MODEL=deepseek-v4-pro
EASEWISE_REVIEW_BOARD_MAX_TOKENS=650
EASEWISE_REVIEW_ASPECTS_MAX_TOKENS=1800
EASEWISE_REVIEW_BATCH_GROUP_SIZE=5
EASEWISE_REVIEW_RENDER_WORKERS=4
EASEWISE_ASPECT_WORKERS=8
EOF
}

write_rendered_service_file() {
  cat <<EOF
[Unit]
Description=EaseWise FastAPI service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$REMOTE_APP_DIR
EnvironmentFile=-$REMOTE_SERVICE_ENV_PATH
ExecStart=$REMOTE_VENV_DIR/bin/uvicorn product.backend.api.main:app --host 127.0.0.1 --port $DEPLOY_API_PORT
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
}

write_rendered_nginx_file() {
  if [[ "$DEPLOY_WEB_MODE" == "preview" ]]; then
    cat <<EOF
server {
    listen $DEPLOY_WEB_PORT;
    listen [::]:$DEPLOY_WEB_PORT;
    server_name $DEPLOY_SERVER_NAME;

    client_max_body_size 10m;
    root $REMOTE_H5_DIR;
    index index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:$DEPLOY_API_PORT;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 120s;
    }

    location = /health {
        proxy_pass http://127.0.0.1:$DEPLOY_API_PORT;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 120s;
    }

    location /h5/ {
        proxy_pass http://127.0.0.1:$DEPLOY_API_PORT;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 120s;
    }

    location /docs {
        proxy_pass http://127.0.0.1:$DEPLOY_API_PORT;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 120s;
    }

    location = /openapi.json {
        proxy_pass http://127.0.0.1:$DEPLOY_API_PORT;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 120s;
    }

    location / {
        try_files \$uri \$uri/ /index.html;
    }
}
EOF
    return
  fi

  cat <<EOF
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name $DEPLOY_SERVER_NAME;

    client_max_body_size 10m;
    root $REMOTE_H5_DIR;
    index index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:$DEPLOY_API_PORT;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 120s;
    }

    location = /health {
        proxy_pass http://127.0.0.1:$DEPLOY_API_PORT;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 120s;
    }

    location /h5/ {
        proxy_pass http://127.0.0.1:$DEPLOY_API_PORT;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 120s;
    }

    location /docs {
        proxy_pass http://127.0.0.1:$DEPLOY_API_PORT;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 120s;
    }

    location = /openapi.json {
        proxy_pass http://127.0.0.1:$DEPLOY_API_PORT;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 120s;
    }

    location / {
        try_files \$uri \$uri/ /index.html;
    }
}
EOF
}
