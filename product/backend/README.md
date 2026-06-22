# EaseWise Backend

## Local Run

1. 在仓库根目录创建虚拟环境：
   - `python3 -m venv .venv`
   - `source .venv/bin/activate`
2. 安装依赖：
   - `pip install -r product/backend/api/requirements.txt`
3. 准备本地环境变量：
   - `cp .env.local.example .env.local`
4. 启动后端：
   - `uvicorn product.backend.api.main:app --host 127.0.0.1 --port 8000 --reload`

## Local Notes

- 本地默认数据库路径使用 `product/backend/api/data/local.db`
- 本地默认放开 `3000` 端口，方便和 `product/frontend` 的 Vite 开发服务联调
- 未配置 `DEEPSEEK_API_KEY` 时，手机号评测会自动退回到本地兜底文案，不会阻塞联调
- `product/backend/api/main.py` 只保留兼容启动入口；实际 app 组装在 `product/backend/api/app.py`，业务路由按领域放在 `product/backend/api/routers/`。
- 新增功能 API 必须使用独立命名空间，例如 `/api/v1/phone-qimen/*` 与未来的 `/api/v1/four-pillars/*`。
- 首页测试页：`http://127.0.0.1:8000/`
- OpenAPI 文档：`http://127.0.0.1:8000/docs`
