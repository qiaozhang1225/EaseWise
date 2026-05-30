# EaseWise Frontend

本地前端默认会自动连接“当前访问主机”的 `8000` 端口。
例如：

- 在这台 Mac 上访问 `http://127.0.0.1:3000` 时，会连 `http://127.0.0.1:8000`
- 在局域网设备上访问 `http://192.168.3.120:3000` 时，会连 `http://192.168.3.120:8000`

## 本地运行

1. 复制环境变量：
   `cp .env.example .env.local`
2. 如需手动指定后端地址，可在 `.env.local` 中设置 `VITE_API_BASE_URL`
3. 如需把前端发布到子路径，可额外设置 `VITE_APP_BASE_PATH`
4. 安装依赖：
   `npm install`
5. 启动开发环境：
   `npm run dev`

## 当前已接入的本地 API

- `POST /api/v1/auth/guest-session`
- `GET /api/v1/runtime-config/public`
- `GET /api/v1/almanac/today`
- `GET /api/v1/account/points`
- `GET /api/v1/account/points/ledger`
- `POST /api/v1/phone-qimen/reviews`
- `GET /api/v1/phone-qimen/reviews`
- `GET /api/v1/phone-qimen/reviews/{id}`
- `GET /api/v1/phone-qimen/reviews/{id}/aspect-unlocks`
- `POST /api/v1/phone-qimen/reviews/{id}/aspect-unlocks`
