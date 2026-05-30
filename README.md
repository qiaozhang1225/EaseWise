# 易如反掌 / EaseWise

`EaseWise` 是一个全新的项目仓库。

## 项目名称

- 中文名：`易如反掌`
- 英文名：`EaseWise`

## 当前状态

- `product/` 是当前产品路径，包含 H5 前端、后端 API 与产品文档。
- `features/` 按平级产品能力组织功能边界，当前包含数字奇门手机号评测、黄历与四柱八字骨架。
- `features/phone_qimen/` 是当前手机号评测的知识、评分与渲染事实源。
- `archive/` 只保存已退出运行路径的历史内容，默认不作为新功能依赖。

## 目录

- `product/docs/`
  - 当前产品文档与 PRD
- `product/backend/`
  - 当前产品后端、API、LLM 渲染与运行时配置
- `product/frontend/`
  - 当前 H5 前端
- `features/`
  - 平级功能模块边界；新增能力必须先建立独立 feature
- `archive/`
  - 已归档的旧专项知识、旧渲染模块和无引用兼容包装器
