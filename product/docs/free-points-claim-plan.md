# 积分领取功能落地计划

## 1. 目标与边界

本功能用于让客服或运营创建临时活动链接，用户访问链接后可免费领取指定积分。功能入口放在后台 `功能管理 > 积分领取`，前台提供独立领取页，页面视觉可复用现有充值页的积分钱包、登录引导和结果反馈结构。

V1 目标：

- 运营可以创建可过期的积分领取链接。
- 每条链接有独立积分额度，例如今天 500 分，明天 1000 分。
- 用户必须登录后领取。
- 每位用户每个自然周只能成功领取一次免费积分。
- 用户本周已领取时，即使拿到更高额度的新链接，也只能看到“本周已领取过免费积分”，不再发放。
- 所有成功与拦截结果都可追溯，客服可以查链接、查领取记录、查用户积分流水。

V1 不做：

- 不做邀请关系、推广返佣或裂变奖励。
- 不复用充值订单流程，不产生 0 元充值订单。
- 不把领取额度做成全局 runtime config，因为每条链接有独立有效期和运营记录。
- 不允许未登录用户先占位领取。

## 2. 现有代码锚点

后端：

- `product/backend/api/database.py`
  - 已有 `points_accounts`、`points_ledgers`，积分余额和流水应继续由后端权威写入。
  - `points_ledgers` 已有 `UNIQUE(user_id, idempotency_key)`，可作为重复提交兜底。
  - 表结构集中在 `CREATE_*_TABLE_SQL` 与 `ensure_schema()`。
  - 充值审批通过时使用 `_credit_points_in_connection()` 写入积分，领取功能应沿用同一类原子写法。
- `product/backend/api/app.py`
  - 所有 public/internal router 在这里 include。
- `product/backend/api/handlers.py`
  - 现有接口处理函数集中在这里。
  - `_utc_now()` 返回 UTC ISO 字符串；本功能的“每周一次”需要额外按 Asia/Shanghai 计算周边界。
- `product/backend/api/schemas.py`
  - Pydantic 响应模型集中在这里。
- `product/backend/api/config.py`
  - 已有 `get_public_base_url()`，可用于后台返回可复制的前台领取链接。

前端：

- `product/frontend/src/App.vue`
  - 当前没有 Vue Router，靠 pathname/query 判断 `/recharge`、`/admin` 和普通 tab。
  - 新领取页应扩展这里的轻量路由。
- `product/frontend/src/components/recharge/RechargePage.vue`
  - 可复用登录态判断、钱包展示、积分和人民币价值展示风格。
- `product/frontend/src/composables/useEaseWiseApp.ts`
  - 已有 `requestRegisteredUser()`、`refreshPoints()`、统一 auth modal 状态。
- `product/frontend/src/components/admin/AdminWorkspace.vue`
  - 后台主菜单和二级菜单在单文件内维护。
  - `FeatureNavKey` 目前为 `almanac | phone-review`，需要加入 `points-claim`。
- `product/frontend/src/lib/api.ts` 与 `product/frontend/src/types/api.ts`
  - 新增前后台 API 类型与请求封装。

## 3. 业务规则

### 3.1 链接生命周期

后台创建领取链接时配置：

- `title`：运营内部标题，例如 `6 月 6 日客服补偿链接`。
- `points_amount`：可领取积分，正整数。
- `display_value_cents`：前台展示的人民币价值，按每条链接配置，避免前台临时推算。
- `expires_in` 或 `expires_at`：有效期。预设建议为 `1 小时`、`7 小时`、`24 小时`、`7 天`，并保留自定义截止时间。
- `operator_note`：创建原因或投放场景，便于客服回溯。
- `status`：`active` / `disabled` / `expired`，过期可以由查询时动态判断，不一定后台定时改状态。

生效条件：

- 当前时间 >= `valid_from`。
- 当前时间 < `expires_at`。
- 链接 `status = active`。
- `points_amount > 0`。

### 3.2 登录限制

前台 GET 链接详情不要求登录，用于展示“未登录”和领取额度。

真正 POST 领取必须是 `require_registered_user`：

- 未登录：返回 401 `auth_required`，前端展示“未登录”，点击状态或按钮打开登录弹窗。
- 登录失效：前端清空本地身份后重新引导登录。
- 禁用账号：返回 403 `account_disabled`，不发放。

### 3.3 每周一次

周限制按北京时间自然周计算：

- 周起点：Asia/Shanghai 周一 00:00:00。
- `week_key`：建议存 `YYYY-Www`，例如 `2026-W23`。
- `week_starts_at`：建议存该周北京时间周一起点的 ISO 字符串，便于排查。

判断口径：

- 同一个 `user_id` 在同一个 `week_key` 内，只能有一条 `status = granted` 的领取记录。
- 该限制跨链接生效。用户本周领取 500 分后，访问 1000 分链接也返回 `already_claimed_this_week`。
- 重复点击同一链接、网络重试、刷新页面，均不得重复加分。

### 3.4 用户可见状态

前台领取页状态建议：

- `loading`：读取链接。
- `invalid`：链接不存在或 code 非法。
- `expired`：链接已过期。
- `disabled`：链接已停用。
- `auth_required`：未登录。
- `ready`：可领取。
- `submitting`：领取中。
- `granted`：领取成功，展示到账积分和最新余额。
- `already_claimed_this_week`：展示“本周已领取过免费积分”。
- `error`：其他异常，提示稍后重试或联系客服。

## 4. 数据模型

在 `product/backend/api/database.py` 新增两张表。

### 4.1 points_claim_links

```sql
CREATE TABLE IF NOT EXISTS points_claim_links (
    id TEXT PRIMARY KEY,
    claim_code TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    points_amount INTEGER NOT NULL,
    display_value_cents INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL,
    valid_from TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    created_by TEXT,
    disabled_by TEXT,
    disabled_at TEXT,
    operator_note TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

说明：

- `claim_code` 使用 `secrets.token_urlsafe(24)` 或同等随机码，不使用自增 ID 暴露在 URL。
- 前台链接格式建议为 `/points-claim/{claim_code}`。
- `display_value_cents` 是展示价值，不参与余额计算。

### 4.2 points_claim_records

```sql
CREATE TABLE IF NOT EXISTS points_claim_records (
    id TEXT PRIMARY KEY,
    claim_link_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    week_key TEXT NOT NULL,
    week_starts_at TEXT NOT NULL,
    status TEXT NOT NULL,
    points_amount_snapshot INTEGER NOT NULL,
    display_value_cents_snapshot INTEGER NOT NULL DEFAULT 0,
    ledger_id TEXT,
    failure_reason TEXT,
    request_ip TEXT,
    user_agent TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(claim_link_id) REFERENCES points_claim_links(id),
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(ledger_id) REFERENCES points_ledgers(id)
);
```

索引：

```sql
CREATE INDEX IF NOT EXISTS idx_points_claim_links_status_expires
ON points_claim_links(status, expires_at DESC);

CREATE INDEX IF NOT EXISTS idx_points_claim_records_link_created
ON points_claim_records(claim_link_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_points_claim_records_user_created
ON points_claim_records(user_id, created_at DESC);

CREATE UNIQUE INDEX IF NOT EXISTS idx_points_claim_records_user_week_granted
ON points_claim_records(user_id, week_key)
WHERE status = 'granted';
```

关键点：

- 成功领取用 partial unique index 保证 `user_id + week_key` 只有一条 `granted`。
- 失败/重复记录不进唯一约束，可以保留多次访问痕迹。
- `points_amount_snapshot` 固化当时额度，避免运营之后停用或复制链接时影响历史记录。

## 5. 后端实现

### 5.1 database.py

新增常量：

- `CREATE_POINTS_CLAIM_LINKS_TABLE_SQL`
- `CREATE_POINTS_CLAIM_RECORDS_TABLE_SQL`
- 对应索引 SQL 放入 `CREATE_INDEX_SQL`

新增数据函数：

- `create_points_claim_link(...)`
- `list_points_claim_links(...)`
- `get_points_claim_link(link_id)`
- `get_points_claim_link_by_code(claim_code)`
- `disable_points_claim_link(link_id, disabled_by, operator_note, now_text)`
- `list_points_claim_records(link_id=None, user_id=None, status=None, limit=20, offset=0)`
- `count_points_claim_records(...)`
- `claim_points_from_link(claim_code, user_id, request_ip, user_agent, now_dt)`

领取原子算法：

```python
with open_connection() as connection:
    link = _get_points_claim_link_by_code_in_connection(connection, claim_code)
    if link is None:
        return invalid
    if link is disabled or expired:
        insert rejected record if user is known, then return disabled/expired

    week_key, week_starts_at = _build_shanghai_week_key(now_dt)
    existing_grant = _get_granted_claim_for_user_week(connection, user_id, week_key)
    if existing_grant is not None:
        insert duplicate record with status='already_claimed_this_week'
        return already_claimed_this_week

    record_id = uuid4().hex
    try:
        insert points_claim_records(status='granted', ...)
    except sqlite3.IntegrityError:
        existing_grant = _get_granted_claim_for_user_week(...)
        return already_claimed_this_week

    ledger = _credit_points_in_connection(
        connection,
        user_id=user_id,
        points_amount=link.points_amount,
        change_type='gift',
        biz_type='free_points_claim',
        biz_id=record_id,
        idempotency_key=f'free_points_claim:{user_id}:{week_key}',
        remark=f'claim_link:{link.id}',
        now_text=now_text,
    )
    update points_claim_records set ledger_id = ledger['ledger_id']
    return granted
```

不要调用 `adjust_points()` 作为主实现，因为它会把正向积分记成 `manual_adjust`。本功能应直接在 `database.py` 内复用 `_credit_points_in_connection()`，并使用 `change_type='gift'`、`biz_type='free_points_claim'`。

### 5.2 schemas.py

新增模型建议：

- `PointsClaimLinkCreateRequest`
  - `title: str`
  - `points_amount: int`
  - `display_value_cents: int = 0`
  - `expires_in_hours: int | None`
  - `expires_at: str | None`
  - `operator_note: str | None`
- `PointsClaimLinkResponse`
  - `claim_link_id`
  - `claim_code`
  - `claim_url`
  - `title`
  - `points_amount`
  - `display_value_cents`
  - `status`
  - `effective_status`
  - `valid_from`
  - `expires_at`
  - `claimed_user_count`
  - `granted_points_total`
  - `created_by`
  - `created_at`
  - `updated_at`
- `PointsClaimLinkListResponse`
- `PointsClaimRecordResponse`
- `PointsClaimRecordListResponse`
- `PublicPointsClaimLinkResponse`
  - 不返回后台 note，不返回内部用户信息。
- `PointsClaimSubmitResponse`
  - `claim_status: granted | already_claimed_this_week`
  - `message`
  - `points: PointsAccountResponse | None`
  - `ledger: PointsLedgerEntryResponse | None`
  - `record: PointsClaimRecordResponse | None`
  - `already_claimed_record: PointsClaimRecordResponse | None`

### 5.3 handlers.py

新增处理函数：

Internal:

- `get_internal_points_claim_links(...)`
- `post_internal_points_claim_link(...)`
- `get_internal_points_claim_link_detail(claim_link_id)`
- `post_internal_points_claim_link_disable(claim_link_id, payload)`
- `get_internal_points_claim_records(...)`

Public:

- `get_public_points_claim_link(claim_code, current_user=Depends(resolve_authenticated_user))`
  - 未登录也返回链接信息。
  - 如果已登录，额外返回 `current_user_claim_status`，便于页面直接显示已领取。
- `post_public_points_claim(claim_code, request, current_user=Depends(require_registered_user))`
  - 成功或本周重复都返回 200，靠 `claim_status` 区分。
  - 链接不存在用 404。
  - 过期/停用用 409。

错误码建议：

- `claim_link_not_found`
- `claim_link_expired`
- `claim_link_disabled`
- `claim_link_not_started`
- `already_claimed_this_week`
- `claim_points_failed`

### 5.4 routers

新增：

- `product/backend/api/routers/points_claim.py`
  - prefix `/api/v1/points-claims`
  - `GET /{claim_code}`
  - `POST /{claim_code}/claim`
- `product/backend/api/routers/internal/points_claim.py`
  - prefix `/api/v1/internal/points-claims`
  - `GET ""`
  - `POST ""`
  - `GET "/{claim_link_id}"`
  - `POST "/{claim_link_id}/disable"`
  - `GET "/{claim_link_id}/records"`

在 `product/backend/api/app.py` include 两个 router。

## 6. 后台页面计划

修改 `product/frontend/src/components/admin/AdminWorkspace.vue`。

### 6.1 导航

- `FeatureNavKey` 改为 `almanac | phone-review | points-claim`。
- `featureNavItems` 加入 `{key: 'points-claim', label: '积分领取'}`。
- 图标建议用 lucide `Gift` 或 `Link2`。
- `activeHeaderTitle` 增加 `运营积分领取链接中心`。
- `isFeatureNavKey()` 支持 `points-claim`。
- `selectFeature()` 切换到该页时加载链接列表。
- `restoreAdminStateFromLocation()` 支持 `feature=points-claim`。

### 6.2 页面结构

顶部指标：

- 当前有效链接数。
- 今日成功领取人数。
- 本周成功领取人数。
- 本周已发放积分总数。

创建区域：

- 标题。
- 积分数量。
- 展示人民币价值。
- 有效期预设：1 小时 / 7 小时 / 24 小时 / 7 天 / 自定义。
- 运营备注。
- 创建按钮。

创建后反馈：

- 展示完整链接。
- 一键复制链接。
- 展示过期时间。

列表字段：

- 状态。
- 标题。
- 积分。
- 展示价值。
- 有效期。
- 成功领取人数。
- 已发积分。
- 创建人 / 创建时间。
- 操作：复制链接、查看记录、停用。

记录抽屉：

- 用户 UID / 手机号 / 昵称。
- 领取状态。
- 领取积分快照。
- 周 key。
- ledger_id。
- IP / user agent。
- 创建时间。
- 跳转用户管理。

### 6.3 API 封装与类型

修改：

- `product/frontend/src/types/api.ts`
  - 增加 link、record、submit response 类型。
- `product/frontend/src/lib/api.ts`
  - `listInternalPointsClaimLinks`
  - `createInternalPointsClaimLink`
  - `getInternalPointsClaimLink`
  - `disableInternalPointsClaimLink`
  - `listInternalPointsClaimRecords`

## 7. 前台领取页计划

新增组件：

- `product/frontend/src/components/points-claim/PointsClaimPage.vue`

### 7.1 路由

修改 `product/frontend/src/App.vue`：

- `AppTab` 增加 `points-claim`。
- `readCurrentRoute()` 支持：
  - `/points-claim/{claim_code}`
  - `/claim/{claim_code}` 可作为短路径兼容。
- `syncRouteState()` 对领取页保持 pathname，不走底部 tab。
- 模板中渲染 `<PointsClaimPage :claim-code="routeQuery.claim_code" />`。
- 领取页不显示 `BottomNav`。

### 7.2 页面交互

页面顶部：

- 使用充值页钱包区域风格。
- 已登录显示当前积分余额和用户身份。
- 未登录显示 `未登录` 状态，点击打开登录弹窗。

核心区域：

- 展示 `可领取 X 积分`。
- 展示 `价值 ¥Y`，金额来自后端 `display_value_cents`。
- 主按钮：`领取积分`。

按钮行为：

- 未登录点击：调用 `requestRegisteredUser('领取免费积分')`，登录成功后自动继续领取。
- 已登录点击：调用 `claimPublicPointsClaim(claim_code)`。
- 成功：调用 `refreshPoints()`，展示 `已到账`、本次积分、当前余额。
- 本周已领：展示 `本周已领取过免费积分`，不再自动重试。
- 过期/停用：展示明确原因和联系客服入口。

### 7.3 前台 API 封装

修改 `product/frontend/src/lib/api.ts`：

- `getPublicPointsClaimLink(claimCode: string, accessToken?: string | null)`
- `claimPublicPointsClaim(accessToken: string, claimCode: string)`

为了让 GET 链接详情能在已登录时返回个人领取状态，`requestJson` 已支持可选 `accessToken`，可直接复用。

## 8. 安全与防重复

必须满足：

- 链接 code 随机且不可预测。
- 只在后端判断有效期，前端倒计时仅作展示。
- 只在后端判断每周一次，前端状态不能作为领取凭证。
- 成功发放和记录写入必须在同一个数据库事务内。
- `points_claim_records(user_id, week_key) WHERE status='granted'` 是最终互斥锁。
- `points_ledgers(user_id, idempotency_key)` 是积分流水级兜底。
- 本周重复访问不同链接，只返回重复提示，不调用 `_credit_points_in_connection()`。
- 后台停用链接后，已成功领取记录保留，未领取用户不能再领。
- 所有时间对外展示可按北京时间格式化，数据库继续存 ISO 字符串。

建议但 V1 可后置：

- 单链接领取人数上限。
- 单 IP 访问频率限制。
- 后台重新生成链接 code。
- 链接短链或二维码。

## 9. 验证计划

后端最小用例：

1. 创建 500 分链接，登录用户领取成功，余额增加 500，流水 `biz_type=free_points_claim`。
2. 同一用户重复点击同一链接，返回 `already_claimed_this_week`，余额不变。
3. 同一用户本周访问另一个 1000 分链接，返回 `already_claimed_this_week`，余额不变。
4. 新用户访问 1000 分链接，可成功领取。
5. 过期链接不能领取。
6. 停用链接不能领取。
7. 未登录 POST 返回 401。
8. 并发两次 POST 同一链接，只产生一条 `granted` 记录和一条积分流水。
9. 周边界用 Asia/Shanghai：周日 23:59 与周一 00:00 属于不同周。

前端检查：

1. 未登录打开链接：显示 `未登录` 和领取额度。
2. 点击未登录状态或领取按钮：弹出登录。
3. 登录完成后自动发起领取。
4. 成功后页面显示到账、最新余额。
5. 已领取用户再次打开任意领取链接：显示 `本周已领取过免费积分`。
6. 过期/停用链接显示不可领取，不展示误导性的成功按钮。
7. 移动端 375px 宽度下按钮、金额、积分数字不溢出。

命令建议：

- 后端：新增 pytest 后运行 `PYTHONPATH=. pytest product/backend/api/tests -q`。
- 前端：`cd product/frontend && npm run lint && npm run build`。
- 本地联调：启动 API 与 Vite，访问 `/points-claim/{claim_code}`。

## 10. 实施顺序

第一阶段：后端闭环

1. 新增数据库表、索引与数据函数。
2. 新增 Pydantic schema。
3. 新增 public/internal handlers 与 routers。
4. 在 `app.py` include router。
5. 添加后端最小测试或脚本级验证，重点覆盖每周互斥和并发。

第二阶段：后台运营页

1. 扩展 `AdminWorkspace.vue` 功能管理二级菜单。
2. 新增创建链接表单。
3. 新增链接列表、复制、停用。
4. 新增领取记录抽屉。
5. 增加 `types/api.ts` 与 `lib/api.ts` 封装。

第三阶段：前台领取页

1. 新增 `PointsClaimPage.vue`。
2. 修改 `App.vue` 轻量路由。
3. 接入登录引导和登录后自动领取。
4. 成功后刷新积分余额。
5. 适配过期、停用、本周已领状态。

第四阶段：联调与验收

1. 后台创建 500 分链接，前台领取成功。
2. 同周重复领取被拦截。
3. 后台再创建 1000 分链接，同用户仍被拦截。
4. 新用户领取 1000 分成功。
5. 后台用户详情、积分流水、领取记录三处证据一致。
6. 生产部署前确认 `EASEWISE_PUBLIC_BASE_URL` 已配置正式域名，否则后台复制链接可能生成空 base URL 或本地 URL。
