# EaseWise 部署流程

这套流程是按 `EaseWise` 当前实际情况设计的，不直接复用旧项目命名，也不和服务器上的 `phoneqimen` 目录混用。

## 当前判断

- 服务器 `123.57.72.212` 目前已经有 `nginx + systemd + python3.10`
- `EaseWise` 使用独立目录、独立服务名；正式部署时接管 80 端口，预览模式仍可保留
- 默认正式目录与服务：
  - 代码目录：`/opt/easewise/app`
  - 静态目录：`/opt/easewise/www/h5`
  - 数据目录：`/opt/easewise/shared`
  - 虚拟环境：`/opt/easewise/venv`
  - systemd 服务：`easewise-api`
  - 正式地址：`http://123.57.72.212`
  - 后端进程端口：`127.0.0.1:8000`

## 本地文件

- 正式目标模板：`product/deploy/targets/production.env.example`
- 预览目标模板：`product/deploy/targets/production-preview.env.example`
- 服务端环境变量模板：`product/deploy/server/easewise-api.env.example`
- 一次性清理旧站：`product/deploy/cleanup-legacy-phoneqimen.sh`
- 一次性初始化：`product/deploy/bootstrap-server.sh`
- 只发后端：`product/deploy/deploy-api.sh`
- 只发前端：`product/deploy/deploy-h5.sh`
- 前后端一起发：`product/deploy/deploy-all.sh`
- 健康检查：`product/deploy/check.sh`
- 回滚：`product/deploy/rollback.sh`

## 第一次使用

1. 准备本地部署目标文件：
   - `cp product/deploy/targets/production.env.example product/deploy/targets/production.env`
2. 准备服务端环境变量文件：
   - `cp product/deploy/server/easewise-api.env.example product/deploy/targets/production.server.env`
3. 按实际情况补齐 `product/deploy/targets/production.server.env` 中的：
   - `DEEPSEEK_API_KEY`
   - `EASEWISE_INTERNAL_ADMIN_TOKEN`
   - 微信相关参数
4. 如服务器仍有旧 `PhoneQimen`：
   - `bash product/deploy/cleanup-legacy-phoneqimen.sh production`
5. 执行服务器初始化：
   - `bash product/deploy/bootstrap-server.sh production`
6. 执行首次部署：
   - `bash product/deploy/deploy-all.sh production`

## 日常发布

- 只发后端：
  - `bash product/deploy/deploy-api.sh production`
- 只发前端：
  - `bash product/deploy/deploy-h5.sh production`
- 一起发：
  - `bash product/deploy/deploy-all.sh production`

## 验证

- 检查部署状态：
  - `bash product/deploy/check.sh production`
- 直接访问：
  - `http://123.57.72.212`

## 回滚

- 发布脚本会按时间戳生成备份目录：
  - `/opt/easewise/backup/api-<release-id>`
  - `/opt/easewise/backup/h5-<release-id>`
- 回滚命令：
  - `bash product/deploy/rollback.sh 20260523-220000 production`

## 预览模式

- 如需先共存验证，可继续使用：
  - `cp product/deploy/targets/production-preview.env.example product/deploy/targets/production-preview.env`
  - `cp product/deploy/server/easewise-api.env.example product/deploy/targets/production-preview.server.env`
  - `bash product/deploy/bootstrap-server.sh production-preview`
  - `bash product/deploy/deploy-all.sh production-preview`
- 预览入口默认是：`http://123.57.72.212:8080`
