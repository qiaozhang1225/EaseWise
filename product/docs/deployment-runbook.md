# EaseWise 部署运行手册

- 状态：active
- 最近整理日期：2026-05-24
- 用途：记录当前服务器部署事实、固定入口、常用命令和回滚方法，避免下次再重新定位

## 当前线上事实

- 公网入口：`http://123.57.72.212`
- 服务器地址：`123.57.72.212`
- SSH 用户：`root`
- SSH key 本地路径：仓库根目录 `NonProductive.pem`
- 当前线上服务名：`easewise-api`
- 当前 Nginx 站点名：`easewise`
- 当前 Nginx 监听端口：`80`
- 当前后端进程地址：`127.0.0.1:8000`
- 当前项目目录：`/opt/easewise/app`
- 当前静态目录：`/opt/easewise/www/h5`
- 当前数据目录：`/opt/easewise/shared`
- 当前数据库文件：`/opt/easewise/shared/app.db`
- 当前虚拟环境：`/opt/easewise/venv`
- 当前备份目录：`/opt/easewise/backup`
- 当前服务端环境变量文件：`/etc/easewise-api.env`
- 当前 systemd 文件：`/etc/systemd/system/easewise-api.service`
- 当前 Nginx 配置文件：`/etc/nginx/sites-available/easewise`

## 当前仓库入口

- 部署总说明：`product/deploy/README.md`
- 部署公共逻辑：`product/deploy/lib.sh`
- 首次初始化：`product/deploy/bootstrap-server.sh`
- 全量部署：`product/deploy/deploy-all.sh`
- 后端部署：`product/deploy/deploy-api.sh`
- 前端部署：`product/deploy/deploy-h5.sh`
- 健康检查：`product/deploy/check.sh`
- 回滚：`product/deploy/rollback.sh`
- 目标模板：`product/deploy/targets/production.env.example`
- 服务端私有环境变量模板：`product/deploy/server/easewise-api.env.example`

## 本地私有文件

以下文件不进 Git，需要本地保留：

- `product/deploy/targets/production.env`
- `product/deploy/targets/production.server.env`

默认准备方式：

```bash
cp product/deploy/targets/production.env.example product/deploy/targets/production.env
cp product/deploy/server/easewise-api.env.example product/deploy/targets/production.server.env
```

## 标准部署流程

### 1. 首次部署或重建环境

```bash
bash product/deploy/bootstrap-server.sh production
```

作用：

- 初始化 `/opt/easewise`
- 安装或复用 `python3-venv`、`pip`、`nginx`
- 写入 `easewise-api.service`
- 写入 Nginx 站点 `easewise`
- 写入 `/etc/easewise-api.env`

### 2. 日常发布

全量发布：

```bash
bash product/deploy/deploy-all.sh production
```

只发后端：

```bash
bash product/deploy/deploy-api.sh production --sync-env
```

只发前端：

```bash
bash product/deploy/deploy-h5.sh production
```

说明：

- 如果服务端环境变量有变更，后端发布时带 `--sync-env`
- 如果只是代码变更但配置没变，后端发布可以不带 `--sync-env`
- 以后优先使用 `deploy-all.sh`，这样前后端会共用同一个 `release_id`，回滚最省事

## 发布后验证

统一检查：

```bash
bash product/deploy/check.sh production
```

手动核验入口：

- 首页：`http://123.57.72.212`
- 健康接口：`http://123.57.72.212/health`
- 公开运行配置：`http://123.57.72.212/api/v1/runtime-config/public?channel=h5`
- OpenAPI：`http://123.57.72.212/docs`

服务器内常用核验命令：

```bash
ssh -i ./NonProductive.pem root@123.57.72.212
systemctl status easewise-api --no-pager -l
journalctl -u easewise-api -n 100 --no-pager
nginx -t
ss -ltnp | grep -E ':80 |:8000 '
```

## 回滚

查看备份：

```bash
ssh -i ./NonProductive.pem root@123.57.72.212 'ls -la /opt/easewise/backup'
```

回滚命令：

```bash
bash product/deploy/rollback.sh <release-id> production
```

示例：

```bash
bash product/deploy/rollback.sh 20260523-223144 production
```

## 当前已知线上基线

2026-05-23 本次正式切换后，线上事实如下：

- 旧服务已清理，服务器当前只保留 `EaseWise`
- 当前公网主入口已经由 `EaseWise` 接管
- 当前正式后端发布号：`20260523-223144`
- 当前正式前端发布号：`20260523-223158`

注意：

- 这一次前后端是分别发的，所以当前线上前后端的 `release_id` 不一致
- 之后如需保持回滚简单，建议统一使用 `bash product/deploy/deploy-all.sh production`

2026-05-24 本次发布后，线上最新基线如下：

- 当前远端仓库提交：`7d4f55b`
- 当前正式全量发布号：`20260524-010031`
- 本次发布包含：
  - 本地 UI 对齐更新
  - 手机号评测 `stem` 映射修正
  - 旧评测结果 `product_view` 按 `rules_version` 自动刷新

当前若要按“最新稳定版本”回滚或追查，优先以这组信息为准。

## 本地联调注意事项

### 前后端默认端口分工

当前仓库本地联调默认不是“前后端共用一个端口”，而是：

- 前端 Vite：`3000`
- 后端 FastAPI：`8000`

本地前端请求基址逻辑在 `product/frontend/src/lib/api.ts` 中：

- 当页面运行在 `3000` 或 `5173` 时
- 前端会自动请求“同主机的 `8000` 端口”

也就是说：

- 打开 `http://127.0.0.1:3000` 时，前端会请求 `http://127.0.0.1:8000`
- 打开 `http://192.168.x.x:3000` 时，前端会请求 `http://192.168.x.x:8000`

### 本地/局域网调试常见坑

2026-05-24 已实际踩过一次，记录如下：

- 如果后端只监听 `127.0.0.1:8000`
- 那么本机访问 `127.0.0.1:3000` 正常
- 但局域网访问 `http://192.168.x.x:3000` 时，前端会去找 `http://192.168.x.x:8000`
- 此时会出现：
  - “今日黄历”一直加载中
  - “需要重新连接本地 API”
  - “本地体验数据暂时不可用”

根因不是前端没发请求，而是后端没有监听局域网地址。

### 正确启动方式

只在本机浏览器调试时：

```bash
uvicorn product.backend.api.main:app --host 127.0.0.1 --port 8000
```

需要让手机、平板或局域网其他设备访问前端时：

```bash
uvicorn product.backend.api.main:app --host 0.0.0.0 --port 8000
```

### 本地下次排查顺序

如果前端打开了但一直提示本地 API 不可用，按以下顺序检查：

1. 前端页面访问地址是不是 `3000`
2. 后端是否真的在 `8000` 监听
3. 如果是局域网地址访问前端，后端是否监听了 `0.0.0.0`
4. 直接打开：
   - `http://127.0.0.1:8000/health`
   - 或 `http://当前局域网IP:8000/health`
5. 再看浏览器请求是否已经命中 `/api/v1/almanac/today`

## 常见问题

### 后端启动失败

优先检查：

```bash
ssh -i ./NonProductive.pem root@123.57.72.212 'systemctl status easewise-api --no-pager -l && journalctl -u easewise-api -n 100 --no-pager'
```

重点看：

- `/etc/easewise-api.env` 是否缺参数
- `DEEPSEEK_API_KEY` 是否为空
- `uvicorn` 是否存在于 `/opt/easewise/venv/bin/uvicorn`

### 前端能打开但接口报错

优先检查：

- `http://123.57.72.212/health`
- `http://123.57.72.212/api/v1/runtime-config/public?channel=h5`
- Nginx 是否把 `/api/` 代理到 `127.0.0.1:8000`

### 需要重新初始化

只要服务文件或 Nginx 配置需要重建，可再次执行：

```bash
bash product/deploy/bootstrap-server.sh production
```

它会覆盖部署基建，但不会清空业务代码仓库目录之外的数据库文件。
