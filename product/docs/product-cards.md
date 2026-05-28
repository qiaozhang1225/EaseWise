# 易如反掌 Product Cards

- Status: active bootstrap index
- Baseline date: 2026-05-23
- External product name: `易如反掌`
- English product name: `EaseWise`
- Current repository name: `EaseWise`
- Purpose: record active product planning before implementation resumes in the new repository
- Related docs: `product/docs/product-prd.md`

## Current Card

- `product/docs/product-prd.md`
  - current product truth baseline for the `EaseWise` repository
- `product/docs/admin-prd.md`
  - current admin-console planning baseline for local testing and operations
- `product/docs/deployment-runbook.md`
  - current deployment memory, server facts, release commands, and rollback entry

## Admin Backlog

### ADMIN-009 大模型密钥管理占位

- 位置：`系统配置 > 大模型密钥管理`
- V1 目标：
  - 先做列表占位、表单占位和数据结构预留
  - 不接入并发监控、自动切换和真实密钥托管
  - 不暴露真实 `DEEPSEEK_API_KEY`
- 页面能力：
  - 支持查看密钥名称、模型供应商、模型名称、启用状态、备注、最后更新时间、最后操作人
  - 密钥值默认脱敏展示
  - 支持新增、编辑、启用/停用、删除的后台操作入口，但可先标记为待接入
- 后端预留：
  - 预留 `llm_api_keys` 数据表
  - 预留后续并发监控、失败率统计、自动切换 key 的扩展位

### ADMIN-010 功能使用记录与搜索

- 位置：`功能管理` 下的统一记录区，后续可扩展为独立页面
- V1 覆盖功能：
  - 数字奇门手机号评测
  - 维度解锁
  - 智能体玄学技能调用
  - 黄历查询
  - 五行属性查询
- 页面能力：
  - 按用户、功能、状态、渠道、时间、关联业务 ID 搜索
  - 支持从用户详情跳转到功能使用记录并自动带入筛选条件
  - 支持从记录详情查看用户基础信息和最近订单摘要
- 后端预留：
  - 统一使用 `usage_records` 作为底层记录源
  - 允许继续补齐 feature、channel、关联业务和摘要字段

### ADMIN-011 功能端用户查看

- 位置：功能使用记录详情抽屉内
- V1 展示范围：
  - 用户 ID、昵称、姓名或手机号、当前状态、身份等级、注册渠道、最近活跃时间
  - 近期订单数量、累计充值金额、最近订单状态
- 订单摘要：
  - 显示最近 3 到 5 笔订单
  - 仅展示订单 ID、金额、状态、创建时间、支付时间
- 权限边界：
  - 只允许查看基础信息和订单摘要
  - 不在这里提供积分调整、身份调整、禁用启用、上级归属调整
  - 需要完整操作时跳转到用户管理页

## Ops Memory

- Deployment single source of truth: `product/docs/deployment-runbook.md`
- Current public entry: `http://123.57.72.212`
- Current online service name: `easewise-api`
- Current online app root: `/opt/easewise/app`
- Current online data path: `/opt/easewise/shared/app.db`
- When deployment is mentioned in a future session, read `product/docs/deployment-runbook.md` first before asking for server details again

## Governance Rules

- Any change that modifies product scope, core UX, pricing / points logic, private-domain strategy, or release path should be reflected here before implementation starts.
- `PRD` records product truth and stage direction.
- Implementation-oriented `spec` should only be created after the new repository structure and delivery plan are confirmed.

## Frontend-Backend Integration Guide

### Goal

后续前后端联调时，前端应逐步移除本地写死数据、`localStorage` 模拟状态和占位文案，改为以后端接口返回结果为准。

当前阶段的联调原则：

- `PRD` 仍然是产品真相来源
- 前端交互流程保持现状，优先替换数据来源，不先改大交互
- 默认展示值可以保留作为兜底，但一旦接口接入，前端展示必须以后端返回为准
- 所有积分、评测结果、用户信息、推广信息都不能再由前端写死

### Integration Priority

建议按以下优先级联调：

1. 认证与用户信息
2. 积分余额与积分流水
3. 手机号评测提交与结果返回
4. 九维度解锁状态与积分扣减
5. 评测历史记录
6. 首页黄历与安全能力入口数据
7. 推广大使信息
8. 智能体上下文数据

### Required API Domains

#### 1. 认证与用户信息

目标：替换当前本地登录态和用户快照。

前端当前本地依赖：

- `easewise_access_token`
- `easewise_user_snapshot`

后端至少需要提供：

- 登录 / 注册接口
- 获取当前用户信息接口
- 登录态失效 / 刷新机制

前端需要以后端返回这些字段为准：

- `user_id`
- `nickname`
- `avatar`
- `account_label`
- `ambassador_status`

涉及页面：

- `product/frontend/src/components/profile/Profile.vue`
- `product/frontend/src/components/ai-agent/AIAgent.vue`

#### 2. 积分余额与积分流水

目标：替换当前积分余额、本地默认值 `2480`、账单占位数据。

前端当前本地依赖：

- `easewise_points`
- `DEFAULT_BASE_REVIEW_POINTS`
- `DEFAULT_ASPECT_UNLOCK_POINTS`

后端至少需要提供：

- 当前用户积分余额接口
- 积分流水接口
- 当前阶段生效中的积分规则配置

前端需要以后端返回这些字段为准：

- `current_points`
- `base_review_points`
- `aspect_unlock_points`
- `ledger_records[]`
  - `type`
  - `desc`
  - `change`
  - `created_at`

涉及页面：

- `product/frontend/src/components/home/Home.vue`
- `product/frontend/src/components/analysis/Analysis.vue`
- `product/frontend/src/components/profile/Profile.vue`
- `product/frontend/src/config/pricing.ts`

#### 3. 手机号评测提交与结果返回

目标：替换当前手机号评测页中的本地模拟结果。

当前前端保留的交互流程：

- 点击首页主入口
- 进入手机号评测输入页
- 点击评测
- 进入等待状态
- 等待后展示结果页

后端至少需要提供：

- 提交手机号评测任务 / 同步评测接口
- 查询评测结果接口（如需要）

前端提交参数至少包括：

- `phone_number`
- `gender`

前端结果页需要以后端返回这些字段为准：

- `report_id`
- `phone_number`
- `gender`
- `score`
- `summary`
- `stability_judgement`
- `long_term_advice[]`
- `board`
- `board_analysis`
- `created_at`

涉及页面：

- `product/frontend/src/components/analysis/Analysis.vue`

#### 4. 盘面数据与总评结构

目标：确保前端已经对齐 PRD 的展示顺序后，后端直接按该结构返回。

当前前端结果结构顺序固定为：

1. 评分
2. 盘面概览
3. 盘面分析 / 总评
4. 长期使用建议 / 稳定性判断
5. 九个重点维度

后端建议返回结构：

- `score`
- `board.cells[]`
- `board_analysis.title`
- `board_analysis.content`
- `summary.title`
- `summary.content`
- `stability_judgement.label`
- `stability_judgement.value`
- `long_term_advice[]`

说明：

- “稳定性”不作为单独解锁维度
- 它属于基础结果区
- 导出图片内容也要复用同一份结果数据

#### 5. 九个重点维度与解锁状态

目标：替换当前九维度的本地文案、本地解锁布尔值和本地扣分逻辑。

前端当前本地依赖：

- `aspectsUnlocked`
- `aspectsList`
- 解锁时直接本地扣积分

后端至少需要提供：

- 九维度列表接口，或评测结果中直接返回
- 单维度解锁接口
- 解锁后返回最新积分余额和最新可见内容

前端需要以后端返回这些字段为准：

- `aspects[]`
  - `aspect_id`
  - `title`
  - `level`
  - `is_unlocked`
  - `unlock_points`
  - `core_judge`
  - `explain`
  - `signal`
  - `suggestion`

说明：

- 维度标题可以由前端保留展示名
- 但内容、等级、解锁状态、所需积分必须以后端返回为准

#### 6. 评测历史记录

目标：替换当前仅保存最后一条记录的本地历史。

前端当前本地依赖：

- `easewise_last_phone_report`

后端至少需要提供：

- 用户评测记录列表接口
- 单条评测详情接口（后续可选）

前端需要以后端返回这些字段为准：

- `report_id`
- `phone_number`
- `gender`
- `score`
- `created_at`

涉及页面：

- `product/frontend/src/components/profile/Profile.vue`

#### 7. 首页黄历与安全能力入口

目标：替换首页黄历日期、宜忌、积分余额等本地展示值。

当前前端存在明显写死数据：

- 日期 `2026年5月22日`
- 星期、干支、宜忌、吉神信息
- 积分余额本地读取

后端至少需要提供：

- 首页聚合接口，或黄历信息接口

前端需要以后端返回这些字段为准：

- `almanac.date`
- `almanac.weekday`
- `almanac.lunar_text`
- `almanac.yi[]`
- `almanac.ji[]`
- `almanac.gods_text`
- `almanac.taboo_text`
- `current_points`

涉及页面：

- `product/frontend/src/components/home/Home.vue`

#### 8. 推广大使信息

目标：替换当前“推广大使”区域的占位状态与文案判断。

前端当前本地依赖：

- `ambassadorStatus`
- `VIP推广大使` 前端条件显示

后端至少需要提供：

- 当前用户推广身份接口
- 推广权益说明接口，或聚合到用户信息中

前端需要以后端返回这些字段为准：

- `ambassador_status`
- `ambassador_title`
- `commission_rate`
- `upgrade_requirements`
- `benefits[]`

涉及页面：

- `product/frontend/src/components/profile/Profile.vue`

#### 9. 客服与私域信息

目标：替换当前前端写死客服微信号。

当前前端存在明显写死数据：

- `yirufanzhang888`

后端至少需要提供：

- 当前有效客服联系方式接口
- 可选：按场景返回不同联系方式

前端需要以后端返回这些字段为准：

- `service_wechat`
- `service_label`
- `service_notice`

涉及页面：

- `product/frontend/src/components/home/Home.vue`
- `product/frontend/src/components/analysis/Analysis.vue`
- `product/frontend/src/components/profile/Profile.vue`

#### 10. 智能体上下文数据

说明：当前不是开发重点，但后续联调时也不要继续沿用本地写死欢迎语与上下文。

当前前端本地依赖：

- `easewise_agent_conversation`
- 写死的欢迎词
- 写死的推荐问题

后端后续建议提供：

- 会话列表 / 消息列表接口
- 发送消息接口
- 当前用户上下文摘要

涉及页面：

- `product/frontend/src/components/ai-agent/AIAgent.vue`

### Local Mock Data To Replace

以下内容后续必须逐步移除或降级为兜底值：

- 本地积分默认值 `2480`
- 评测默认评分 `85`
- 本地最后一条评测记录
- 首页黄历全部静态字段
- 客服微信写死值
- 推广大使本地状态
- 九维度本地内容文案
- 解锁逻辑前端直接扣积分
- 登录成功后本地写入的模拟用户信息

### Delivery Rule

后续开始联调时，建议每完成一个域就同步完成这三件事：

1. 删掉对应本地写死数据
2. 保留必要空态 / 加载态 / 失败态
3. 在 `PRD` 或 `spec` 中补齐接口字段约束

如果联调顺序与这里不同，需先更新本卡，再开始实现。

## Pending Change Card

### 手机号评测结果页｜盘面概览改版（已完成）

#### Goal

把当前“盘面概览”从“看起来像九宫格、但盘内信息并不专业准确”的状态，改成“用户一眼能感知奇门盘面专业感，同时盘内展示字段全部有明确方法论依据”的状态。

本次改版目标不是做完整传统奇门飞盘，而是做一个对当前手机号评测体系真实、可解释、可落地的 `手机号落宫九宫示意盘`。

#### Current Problem

当前九宫格存在两个问题：

- 视觉上像完整盘面，但实际只有一个落宫结构被稳定算出
- 中宫和非落宫位置混入了 `score_band`、`main_axis`、`confidence` 这类非盘面符号，专业上不成立

因此用户虽然会觉得“有盘面”，但专业用户一看会发现字段层级混乱。

#### Product Decision

本次改版按以下原则执行：

- 中宫只显示 `引干`
- 不在前台显示 `后七位`
- 不向用户暴露“通过后七位定盘”的产品实现细节
- 九宫格本体只承载“定盘层信息”
- 关系判断、四害、特殊组合、封顶因素移到九宫格下方或旁侧，不再塞进宫格正文
- `main_axis`、`main_contradiction`、总评文案保留在“盘面分析 / 总评”区域，不放进九宫格

#### Scope Boundary

当前阶段不做：

- 完整传统奇门九宫飞盘的九宫全量排布
- 为其余八宫伪造 `神 / 星 / 门 / 天盘 / 地盘`
- 在盘面 UI 中加入代码层未锁定的格局名词、门派术语或扩展判断

#### Frontend Change Plan

前端结果页的“盘面概览”调整为：

1. `中宫`
   - 仅显示：`引干`
   - 不显示：`后七位`

2. `落宫格`
   - 显示真实落宫信息：
     - `宫名`
     - `方位`
     - `神`
     - `星`
     - `门`
     - `天盘干`
     - `地盘干`
   - 该宫做高亮态，明确告诉用户“本盘当前落在此宫”

3. `其余八宫`
   - 仅显示固定静态宫位信息：
     - `宫名`
     - `方位`
   - 可选补充：
     - `五行`
   - 不显示伪造的 `神 / 星 / 门 / 天盘 / 地盘`

4. `九宫格外的信息区`
   - 使用标签或信息条展示：
     - `宫门关系`
     - `后两干关系`
     - `四害`
     - `特殊组合`
     - `结构封顶`

5. `盘面分析 / 总评`
   - 保持现有独立模块
   - 承接：
     - `main_axis`
     - `main_contradiction`
     - `practical_manifestation`

涉及页面：

- `product/frontend/src/components/analysis/Analysis.vue`

#### Backend Change Plan

后端公开给前端的 `board` 结果结构需要从当前“仅适配旧 UI 的薄结构”改成“适配示意盘 UI 的结构化字段”。

当前公开结构问题：

- 只提供 `focus_*` 与 `cells`
- `cells` 中心位混入了 `score_band`、`main_axis`、`confidence`
- 没有把当前方法论已锁定的 `引干 / 天盘干 / 地盘干 / 宫门关系 / 后两干关系 / 四害 / 特殊组合 / 封顶因素` 正常公开给前端

建议新增或调整为以下公开结构：

- `board.center_basis`
  - `trigger`

- `board.active_basis`
  - `palace`
  - `direction`
  - `god`
  - `star`
  - `door`
  - `heaven_stem`
  - `earth_stem`

- `board.grid_cells[]`
  - `slot_id`
  - `palace_key`
  - `palace_name`
  - `direction`
  - `wuxing`（可选）
  - `is_active`

- `board.relations`
  - `palace_door_relation`
  - `stem_pair_relation`

- `board.risks`
  - `four_harms`
    - `emptiness`
    - `door_pressure`
    - `tomb`
    - `punishment_hit`
  - `pattern_flags[]`
  - `risk_pairs[]`
  - `structural_cap_reasons[]`

- `board.summary`
  - `main_axis`
  - `main_contradiction`

说明：

- `last7` 可以继续保留在内部计算链路中
- 但前台公开接口不再返回 `last7`
- 如确有调试需求，应仅保留在内部调试对象或测试工具中，不进入正式 H5 用户接口

涉及文件：

- `product/backend/api/phone_review_view.py`
- `product/backend/api/schemas.py`
- 如需同步类型：
  - `product/frontend/src/types/api.ts`

#### Methodology Source Mapping

本次改版只允许使用当前知识与代码中已经锁定的盘面事实：

- 定盘层必须覆盖：
  - `引干 / 宫 / 神 / 星 / 门 / 天干 / 地干`
- 核心关系层必须覆盖：
  - `宫门关系`
  - `后两干关系`
- 风险层可承接：
  - `四害`
  - `特殊组合`
  - `结构封顶`

参考来源：

- `knowledge/sections/phone_summary/judgement-knowledge.md`
- `knowledge/sections/phone_summary/taxonomy.md`
- `knowledge/shared/model-baseline.md`
- `scoring/total_score/engine.py`
- `scoring/total_score/score_facts.py`

#### Acceptance Criteria

改版完成后，应满足以下验收标准：

1. 用户一眼能看出“这是奇门九宫盘面”
2. 宫格内所有动态字段都能追溯到当前已锁定方法论
3. 不再出现把评分、主轴、置信度伪装成盘面符号的情况
4. 不在前台暴露 `后七位`
5. 非专业用户能感知专业度，专业用户也不会一眼看出结构错误

#### Execution Rule

本项当前状态：`implemented / locally validated`

执行要求：

- 前后端返回结构已同步落地
- 前台接口已移除 `last7`
- 已完成本地构建验证，可继续进入下一轮联调

### 我的页面｜评测记录点击后恢复结果页（planned）

#### Goal

让用户在“我的”页面查看历史评测记录时，不只是看到摘要列表，而是可以点击任意一条记录，重新打开该次评测对应的结果页。

目标体验：

- 用户进入“我的”页面
- 打开“评测记录”弹窗
- 点击某条记录
- 系统拉取该 `review_id` 对应的完整评测详情
- 自动切换到手机号评测页，并恢复到该条记录对应的结果态 / 等待态 / 失败态

#### Current Problem

当前“我的”页面中的评测记录只有列表展示，没有“查看结果”的能力。

这会带来两个问题：

- 用户无法回看以前已经完成的完整评测内容
- 当前产品已经有 `review detail` 能力与 `currentReview` 全局状态，但没有在用户路径里真正打通

因此现在的“评测记录”更像日志，而不是可回访的历史资产入口。

#### Product Decision

本次改动按以下原则执行：

- 不新增独立“历史结果详情页”
- 继续复用当前“手机号评测页与结果页同页”的产品结构
- 由“我的”页负责触发打开记录
- 由全局状态负责加载并持有目标 `currentReview`
- 由手机号评测页根据 `currentReview.status` 自动恢复正确页面状态

#### Frontend Change Plan

前端改动拆为三层：

1. `Profile.vue`
   - 把评测记录列表从“纯展示卡片”升级为“可点击记录项”
   - 点击后抛出 `open-review` 事件，并携带 `review.id`
   - 点击时关闭当前 history 弹窗
   - 建议增加轻量 loading / disabled 状态，避免重复点击

2. `App.vue`
   - 新增统一方法，例如 `openReviewFromHistory(reviewId)`
   - 方法内部先调用 `refreshCurrentReview(reviewId, { setAsCurrent: true })`
   - 拉取成功后切到 `activeTab = 'phone'`
   - `Profile` 通过事件把该行为交给 `App` 承接，避免跨组件直接操作状态

3. `Analysis.vue`
   - 新增 `syncViewFromCurrentReview()` 一类的状态同步逻辑
   - 对 `state.currentReview` 建立监听，并根据 review 状态恢复页面：
     - `completed` → `appState = 'result'`
     - `processing` → `appState = 'waiting'`
     - `failed` → `appState = 'error_state'`
   - 同步恢复：
     - `phoneNumber`
     - `gender`
     - `currentProgressStage`
     - `currentProgressMessage`
     - `activeAspect`

涉及页面：

- `product/frontend/src/components/profile/Profile.vue`
- `product/frontend/src/App.vue`
- `product/frontend/src/components/analysis/Analysis.vue`
- `product/frontend/src/composables/useEaseWiseApp.ts`

#### Backend Dependency

本项不要求新增后端接口。

直接复用当前已有能力即可：

- 评测记录列表接口
- 单条评测详情接口

前提是详情接口对历史记录仍可稳定返回完整结果结构：

- `summary`
- `board`
- `board_analysis`
- `stability_judgement`
- `long_term_advice`
- `aspects`
- `progress_stage`
- `progress_message`
- `error_message`

#### Interaction Notes

- 点击已完成记录：直接恢复结果页
- 点击处理中记录：进入等待态，并继续展示进度文案
- 点击失败记录：进入失败态，并展示该记录已有失败原因
- 若详情拉取失败：停留在当前页，并给出 toast / 错误提示

#### Scope Boundary

当前阶段不做：

- 单独的新路由结果详情页
- 评测记录列表分页 / 搜索 / 筛选
- 历史记录的分享、删除、重命名
- 在“我的”页内直接嵌入完整结果内容

#### Coordination Note

本项需要修改 `Analysis.vue`。

由于当前已有其他 session 正在处理该文件，执行时应遵循：

- 先把本卡作为产品与实现基线
- 等当前并行修改完成后，再进入代码落地
- 落地前先重新拉取 `Analysis.vue` 最新版本，避免覆盖他人改动

#### Acceptance Criteria

完成后应满足：

1. 用户在“我的 > 评测记录”中点击任意一条记录，可以重新进入对应评测结果
2. 已完成 / 处理中 / 失败三种记录都能恢复到正确页面态
3. 不新增独立详情页，继续保持“手机号评测页与结果页同页”
4. 当前全局 `currentReview` 与本地最近一次记录缓存保持一致
5. 交互过程中不会出现弹窗未关闭、切页后状态错乱或结果页空白

#### Execution Rule

本项当前状态：`planned / pending implementation`

执行要求：

- 先等待当前并行 session 完成 `Analysis.vue` 相关改动
- 再进入前端落地与联调
- 实现后需补一次点击历史记录的完整手工回归验证

### DeepSeek 并发容量与生产压测（planned / deferred）

#### Background

当前手机号评测链路已经大量依赖 DeepSeek：

- 第一阶段：用户提交手机号和性别后，先生成总评与稳定性结果
- 第二阶段：系统继续在后台预热 12 个专项内容，并写入数据库
- 单个用户请求在峰值时可能触发多路 DeepSeek 请求

DeepSeek 官方并发限制以账号为单位。未提交扩容工单时，即使传入不同 `user_id`，普通账号在 DeepSeek V3 Pro / V4 Pro 等模型下仍共享账号级并发限制；超过账号并发限制会收到 `HTTP 429`。

#### Current Decision

本问题当前阶段暂不进入代码落地。

原因：

- 当前仍处于开发与早期联调阶段
- 实际测试不会产生数百级 DeepSeek 瞬时并发
- 即使短时间多人测试，也不太可能触达 DeepSeek 账号级上限
- 生产服务器规格、部署进程数、网络能力、数据库写入能力尚未经过压测

#### Future Direction

生产部署前后需要补一轮压力测试，并根据真实结果决定是否启用并发治理。

待验证内容：

- 单台生产服务器在当前同步 HTTP + 线程池模式下可承受的 DeepSeek 并发数
- 单用户评测请求在第一阶段与第二阶段的实际峰值并发
- 多用户同时提交时的排队、响应时间、后台任务完成时间
- SQLite / 后续数据库在频繁写入专项结果时的锁等待情况
- DeepSeek 返回 `429`、超时或网络错误时的恢复策略

#### Candidate Technical Plan

后续如进入生产容量治理，优先考虑：

- 增加全局 DeepSeek 并发监控
- 增加账号级 DeepSeek key pool，备用 key 必须来自不同 DeepSeek 账号
- 每个账号维护 `max_concurrency`、`soft_limit`、`inflight`、`cooldown_until`
- 请求前获取并发令牌，请求完成、失败、超时后释放令牌
- 触发 `429` 后对该账号短暂熔断，并切换到其他可用账号
- 区分前台核心链路与后台专项预热的优先级
- 后台 12 个专项应进入全局队列，不应随着用户数无限扩张线程数

#### Initial Capacity Guideline

在没有生产压测数据前，不建议直接按 DeepSeek key 数量放大并发。

初始建议：

- 全局 DeepSeek 并发先控制在 `60-100`
- 核心链路并发优先保障，后台专项预热让路
- 单用户专项并发保持可配置，例如 `EASEWISE_ASPECT_WORKERS=4-8`
- 如果将来多进程或多服务器部署，需要使用 Redis 等集中式计数器管理并发令牌

#### Execution Rule

本项当前状态：`planned / deferred`

暂不修改代码。等项目部署到真实生产服务器后，先做压力测试，再根据压测结果决定：

- 是否启用跨 DeepSeek 账号 key pool
- 服务器级全局并发阈值
- 前台 / 后台任务优先级
- 429 熔断与排队策略
