<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, type Component } from 'vue';
import {
  AlertTriangle,
  Award,
  Calendar,
  Coins,
  LogOut,
  Search,
  Settings,
  ShoppingBag,
  Sliders,
  Smartphone,
  TrendingUp,
  Users,
} from 'lucide-vue-next';
import {
  ApiError,
  adjustInternalUserPoints,
  createInternalLlmApiKey,
  createInternalRechargeOrderRefund,
  deleteInternalLlmApiKey,
  getInternalDashboard,
  getInternalPromotionApplication,
  getInternalPromotionCommission,
  getInternalPromotionRules,
  getInternalPromotionWithdrawal,
  getInternalRechargeOrder,
  getInternalUsageRecord,
  getInternalUserAdminSummary,
  getInternalRuntimeConfigSchema,
  listInternalLlmApiKeys,
  listInternalPromotionApplications,
  listInternalPromotionCommissions,
  listInternalPromotionWithdrawals,
  listInternalRechargeOrders,
  listInternalRuntimeConfig,
  listInternalUsageRecords,
  listInternalUsers,
  markInternalPromotionWithdrawalPaid,
  reviewInternalPromotionApplication,
  reviewInternalPromotionWithdrawal,
  reviewInternalRechargeOrder,
  retryInternalPromotionWithdrawalPayout,
  updateInternalLlmApiKey,
  updateInternalPromotionRules,
  updateInternalRuntimeConfig,
  updateInternalUserIdentity,
  updateInternalUserPromoterParent,
  updateInternalUserStatus,
  type InternalLlmApiKeyPayload,
} from '../../lib/api';
import AdminSelect from './AdminSelect.vue';
import type {
  DashboardResponse,
  InternalUserAdminSummaryResponse,
  InternalUserResponse,
  LlmApiKeyResponse,
  PromotionApplicationResponse,
  PromotionCommissionResponse,
  PromotionRulesResponse,
  PromotionWithdrawalResponse,
  RechargeOrderResponse,
  RuntimeConfigEntryResponse,
  RuntimeConfigEntryUpsertRequest,
  RuntimeConfigSchemaItemResponse,
  UsageRecordDetailResponse,
  UsageRecordResponse,
} from '../../types/api';

const ADMIN_TOKEN_KEY = 'easewise_internal_admin_token';

type PrimaryNavKey = 'dashboard' | 'orders' | 'users' | 'features' | 'promotion' | 'settings';
type FeatureNavKey = 'almanac' | 'phone-review';
type PromotionNavKey = 'review' | 'withdrawals' | 'commissions' | 'rules';
type DashboardMetric = DashboardResponse['sections'][number]['metrics'][number];
type UserLinkedDestination = 'orders' | 'usage';
type UserPointOperation = 'increase' | 'decrease' | 'set';
type FeatureUsageWindowKey = 'today' | 'yesterday' | 'week' | 'month';
type SelectedUserInfoCard = {
  key: 'identity' | 'channel' | 'registered_at' | 'phone' | 'unionid';
  label: string;
  value: string;
  sub: string;
};
type FeatureUsageRankItem = {
  name: string;
  count: number;
  percentage: number;
};
type FeatureUsageWindowCard = {
  key: FeatureUsageWindowKey;
  label: string;
  total: string;
  sub: string;
  items: FeatureUsageRankItem[];
};
type AdminRouteQuery = {
  view: PrimaryNavKey;
  feature?: FeatureNavKey;
  promotion?: PromotionNavKey;
  modal?: 'user';
  user_id?: string;
  return?: 'user';
};

const primaryNavItems: Array<{key: PrimaryNavKey; label: string; desc: string}> = [
  {key: 'dashboard', label: '数据大盘', desc: '核心收益与运营摘要'},
  {key: 'orders', label: '订单管理', desc: '充值订单与退款线索'},
  {key: 'users', label: '用户管理', desc: '用户搜索与排查'},
  {key: 'features', label: '功能管理', desc: '规则、开关与使用记录'},
  {key: 'promotion', label: '推广合作', desc: '审核、提现、返佣'},
  {key: 'settings', label: '系统配置', desc: '套餐、积分、密钥'},
];

const featureNavItems: Array<{key: FeatureNavKey; label: string}> = [
  {key: 'almanac', label: '黄历相关设置'},
  {key: 'phone-review', label: '数字奇门手机号评测'},
];

const promotionNavItems: Array<{key: PromotionNavKey; label: string}> = [
  {key: 'review', label: '推广审核'},
  {key: 'withdrawals', label: '提现申请审核'},
  {key: 'commissions', label: '返佣记录'},
  {key: 'rules', label: '规则配置'},
];

const flatNavItems = primaryNavItems.filter((item) => item.key === 'dashboard' || item.key === 'orders' || item.key === 'users');
const settingsNavItem = primaryNavItems.find((item) => item.key === 'settings');
const primaryNavIcons: Record<PrimaryNavKey, Component> = {
  dashboard: TrendingUp,
  orders: ShoppingBag,
  users: Users,
  features: Sliders,
  promotion: Award,
  settings: Settings,
};
const featureNavIcons: Record<FeatureNavKey, Component> = {
  almanac: Calendar,
  'phone-review': Smartphone,
};
const promotionNavIcons: Record<PromotionNavKey, Component> = {
  review: Users,
  withdrawals: Coins,
  commissions: Search,
  rules: Settings,
};

const orderStatusSelectOptions = [
  {value: '', label: '全状态流转', dotClass: 'bg-indigo-500'},
  {value: 'unpaid', label: '未支付', dotClass: 'bg-amber-500'},
  {value: 'paid', label: '已支付', dotClass: 'bg-blue-500'},
  {value: 'completed', label: '已完成', dotClass: 'bg-emerald-500'},
  {value: 'refund_pending', label: '退款中', dotClass: 'bg-red-500 animate-pulse'},
  {value: 'refunded', label: '已退款', dotClass: 'bg-gray-400'},
  {value: 'closed', label: '已关闭', dotClass: 'bg-slate-400'},
];

const userStatusSelectOptions = [
  {value: '', label: '全状态', dotClass: 'bg-indigo-500'},
  {value: 'active', label: '正常', dotClass: 'bg-emerald-500'},
  {value: 'guest', label: '游客', dotClass: 'bg-amber-500'},
  {value: 'disabled', label: '禁用', dotClass: 'bg-red-500'},
];

const userEditStatusSelectOptions = [
  {value: 'guest', label: '游客', dotClass: 'bg-amber-500'},
  {value: 'active', label: '正常', dotClass: 'bg-emerald-500'},
  {value: 'disabled', label: '禁用', dotClass: 'bg-red-500'},
  {value: 'blocked', label: '封禁', dotClass: 'bg-slate-500'},
];

const userIdentitySelectOptions = [
  {value: '', label: '全身份', dotClass: 'bg-indigo-500'},
  {value: 'normal_user', label: '普通会员', dotClass: 'bg-gray-400'},
  {value: 'promoter', label: '推广大使', dotClass: 'bg-emerald-500'},
  {value: 'senior_promoter', label: '高级推广大使', dotClass: 'bg-purple-500'},
];

const userEditIdentitySelectOptions = userIdentitySelectOptions.filter((option) => option.value !== '');

const usageSceneSelectOptions = [
  {value: '', label: '全部功能', dotClass: 'bg-indigo-500'},
  {value: 'phone_review_base', label: '手机号评测', dotClass: 'bg-blue-500'},
  {value: 'phone_review_aspect_unlock', label: '维度解锁', dotClass: 'bg-emerald-500'},
  {value: 'agent_reply', label: '智能体对话', dotClass: 'bg-purple-500'},
  {value: 'almanac_query', label: '黄历查询', dotClass: 'bg-amber-500'},
  {value: 'five_elements_query', label: '五行属性查询', dotClass: 'bg-cyan-500'},
];

const booleanToggleSelectOptions = [
  {value: true, label: '开启', dotClass: 'bg-emerald-500'},
  {value: false, label: '关闭', dotClass: 'bg-gray-400'},
];

const userPointOperationOptions: Array<{value: UserPointOperation; label: string; desc: string}> = [
  {value: 'increase', label: '增加', desc: '在当前余额上增加'},
  {value: 'decrease', label: '减少', desc: '从当前余额中扣减'},
  {value: 'set', label: '设置', desc: '直接设置为目标值'},
];

const savedToken = typeof window !== 'undefined' ? window.localStorage.getItem(ADMIN_TOKEN_KEY) : '';
const adminToken = ref(savedToken || '');
const loginToken = ref(savedToken || '');
const activePrimary = ref<PrimaryNavKey>('dashboard');
const activeFeature = ref<FeatureNavKey>('phone-review');
const activePromotion = ref<PromotionNavKey>('review');
const isFeaturesMenuOpen = ref(true);
const isPromoMenuOpen = ref(true);
const globalMessage = ref('');

const dashboard = ref<DashboardResponse | null>(null);
const dashboardLoading = ref(false);
const dashboardError = ref('');

const llmKeys = ref<LlmApiKeyResponse[]>([]);
const llmLoading = ref(false);
const llmError = ref('');
const llmSchema = ref<RuntimeConfigSchemaItemResponse[]>([]);
const llmKeyFormMode = ref<'create' | 'edit' | null>(null);
const llmEditingKeyId = ref('');
const llmKeyForm = ref<InternalLlmApiKeyPayload>({
  provider: 'deepseek',
  model: 'deepseek-chat',
  display_name: '',
  masked_key: '',
  secret_ref: '',
  enabled: true,
  priority: 100,
  remark: '',
  last_operator: 'internal_admin',
});

const usageLoading = ref(false);
const usageError = ref('');
const usageRecords = ref<UsageRecordResponse[]>([]);
const usageFilters = ref({
  keyword: '',
  scene: '',
  status: '',
  channel: '',
  target_id: '',
  date_from: '',
  date_to: '',
  user_id: '',
});
const selectedUsage = ref<UsageRecordDetailResponse | null>(null);
const usageDetailLoading = ref(false);

const userLoading = ref(false);
const userError = ref('');
const userQuery = ref('');
const userFilters = ref({
  status: '',
  identity_level: '',
  channel: '',
});
const users = ref<InternalUserResponse[]>([]);
const selectedUser = ref<InternalUserAdminSummaryResponse | null>(null);
const expandedUserInfoKey = ref('');
const adminReturnContext = ref<{
  userId: string;
  userLabel: string;
  destination: UserLinkedDestination;
} | null>(null);
const userEditOpen = ref(false);
const userEditMode = ref<'points' | 'status' | 'identity' | 'parent' | null>(null);
const userPointOperation = ref<UserPointOperation>('increase');
const userEditValue = ref('');
const userEditReason = ref('');
const userEditNote = ref('');

const orderLoading = ref(false);
const orderError = ref('');
const orderSearchText = ref('');
const orderFilters = ref({user_id: '', status: '', channel: ''});
const orders = ref<RechargeOrderResponse[]>([]);
const selectedOrder = ref<RechargeOrderResponse | null>(null);
const orderDetailLoading = ref(false);
const orderRefundReason = ref('');
const orderReviewNote = ref('');
const orderActionMessage = ref('');

const isLoggedIn = computed(() => Boolean(adminToken.value.trim()));
const activeOrderReturnContext = computed(() => (
  adminReturnContext.value?.destination === 'orders' && orderFilters.value.user_id
    ? adminReturnContext.value
    : null
));
const activeUsageReturnContext = computed(() => (
  adminReturnContext.value?.destination === 'usage' && usageFilters.value.user_id
    ? adminReturnContext.value
    : null
));
const userPointInputPlaceholder = computed(() => {
  if (userPointOperation.value === 'increase') return '请输入要增加的积分数';
  if (userPointOperation.value === 'decrease') return '请输入要减少的积分数';
  return '请输入要设置成的积分余额';
});
const userPointDeltaPreview = computed(() => {
  if (!selectedUser.value || userEditMode.value !== 'points') return '';
  const amount = Number(userEditValue.value || 0);
  if (!Number.isFinite(amount)) return '';
  const normalizedAmount = Math.trunc(Math.max(0, amount));
  const current = selectedUser.value.user.points_balance;
  if (userPointOperation.value === 'increase') return `提交后预计增加 ${normalizedAmount} 积分`;
  if (userPointOperation.value === 'decrease') return `提交后预计减少 ${normalizedAmount} 积分`;
  const delta = normalizedAmount - current;
  if (delta === 0) return '目标值与当前积分一致';
  return delta > 0 ? `提交后预计增加 ${delta} 积分` : `提交后预计减少 ${Math.abs(delta)} 积分`;
});
const selectedUserInfoCards = computed<SelectedUserInfoCard[]>(() => {
  if (!selectedUser.value) return [];
  const user = selectedUser.value.user;
  const identityValue = selectedUserIdentityValue();
  const registeredAt = formatTime(user.registered_at || user.created_at);
  const firstLoginAt = formatTime(user.first_login_at || user.created_at);
  return [
    {key: 'identity', label: '主身份', value: identitySourceLabel(user.primary_identity_type), sub: '身份来源'},
    {key: 'channel', label: '注册渠道', value: user.registered_channel || '--', sub: '来源渠道'},
    {key: 'registered_at', label: '注册时间', value: registeredAt, sub: `首次 ${firstLoginAt}`},
    {key: 'phone', label: '手机号', value: user.primary_phone || '--', sub: user.phone_verified_at ? `验证 ${formatTime(user.phone_verified_at)}` : '待绑定'},
    {key: 'unionid', label: 'UnionID / Guest', value: identityValue, sub: identityValue === '--' ? '待绑定' : '点击查看全文'},
  ];
});
const expandedUserInfoCard = computed(() => selectedUserInfoCards.value.find((item) => item.key === expandedUserInfoKey.value) || null);
const activeCode = computed(() => {
  if (activePrimary.value === 'features') {
    return activeFeature.value === 'almanac' ? 'features_almanac' : 'features_phone';
  }
  if (activePrimary.value === 'promotion') {
    return `promo_${activePromotion.value}`;
  }
  return activePrimary.value === 'settings' ? 'configs' : activePrimary.value;
});
const activeHeaderTitle = computed(() => {
  if (activePrimary.value === 'dashboard') return '经营决策中心';
  if (activePrimary.value === 'orders') return '会员充值订单审计部';
  if (activePrimary.value === 'users') return '测算用户流水分账部';
  if (activePrimary.value === 'features' && activeFeature.value === 'almanac') return '日常黄历万年历日课定制';
  if (activePrimary.value === 'features') return '手算五行手机号评测算法';
  if (activePrimary.value === 'promotion' && activePromotion.value === 'review') return '合伙人入驻资质审批中心';
  if (activePrimary.value === 'promotion' && activePromotion.value === 'withdrawals') return '合伙佣金提现风险审计部';
  if (activePrimary.value === 'promotion' && activePromotion.value === 'commissions') return '大众代理推广返佣流水';
  if (activePrimary.value === 'promotion') return '推广合作规则维护';
  return '全局系统基础配置部';
});

const revenueCards = computed(() => [
  {label: '昨日收益', value: metricCurrency('收益', ['昨日收益', '昨日支付金额', '昨日支付'], '0.00'), tone: 'text-emerald-600'},
  {label: '本月收益', value: metricCurrency('收益', ['本月收益', '本月支付金额', '本月支付'], '0.00'), tone: 'text-emerald-600'},
  {label: '上月收益', value: metricCurrency('收益', ['上月收益', '上月支付金额', '上月支付'], '0.00'), tone: 'text-emerald-700'},
  {label: '本年度收益', value: metricCurrency('收益', ['本年度收益', '当年收益', '今年支付'], '0.00'), tone: 'text-brand-primary-strong'},
  {label: '上年度收益', value: metricCurrency('收益', ['上年度收益', '去年收益', '上年支付'], '0.00'), tone: 'text-slate-500'},
  {label: '累计总收益', value: metricCurrency('收益', ['累计总收益', '总收益', '累计支付'], '0.00'), tone: 'text-emerald-700', featured: true},
]);

const userOverviewCards = computed(() => [
  {label: '当前总用户量', value: metricText('用户', ['总用户', '当前总用户量'], String(users.value.length || 0)), sub: '系统累计注册'},
  {label: '今日新增用户', value: metricText('用户', ['今日新增'], '0'), sub: 'UTC+8 今日'},
  {label: '本周新增用户', value: metricText('用户', ['本周新增'], '0'), sub: '自然周累计'},
  {label: '上周新增用户', value: metricText('用户', ['上周新增'], '0'), sub: '上一自然周'},
  {label: '本月新增用户', value: metricText('用户', ['本月新增'], '0'), sub: '自然月累计'},
  {label: '上月新增用户', value: metricText('用户', ['上月新增'], '0'), sub: '上一自然月'},
  {label: '日活用户 (DAU)', value: metricText('用户', ['日活', '今日活跃', '活跃用户'], '0'), sub: `月活: ${metricText('用户', ['月活', '30日活跃'], '0')}`},
]);

const featureUsageSceneLabels: Record<string, string> = {
  phone_review_base: '手机号评测',
  phone_review_aspect_unlock: '维度解锁',
  agent_reply: '智能体玄学技能',
  almanac_query: '黄历查询',
  five_elements_query: '五行属性查询',
};

const featureUsageWindowConfigs: Array<{key: FeatureUsageWindowKey; label: string; sub: string}> = [
  {key: 'today', label: '今日使用', sub: 'UTC+8 今日'},
  {key: 'yesterday', label: '昨日使用', sub: '上一自然日'},
  {key: 'week', label: '本周使用', sub: '自然周累计'},
  {key: 'month', label: '本月使用', sub: '自然月累计'},
];

const featureUsageWindowCards = computed<FeatureUsageWindowCard[]>(() => {
  return featureUsageWindowConfigs.map((config) => {
    const total = metricNumber('功能使用', [config.label], 0);
    const metrics = getSectionMetrics('功能使用')
      .filter((metric) => metric.label.startsWith(`${config.label}·`))
      .map((metric) => {
        const name = metric.label.slice(config.label.length + 1);
        const count = Number(metric.value);
        return {
          name,
          count: Number.isFinite(count) ? count : 0,
          percentage: total > 0 ? Math.round((Number.isFinite(count) ? count : 0) / total * 100) : 0,
        };
      })
      .sort((left, right) => right.count - left.count)
      .slice(0, 5);

    if (metrics.length > 0) {
      return {
        key: config.key,
        label: config.label,
        total: metricText('功能使用', [config.label], '0'),
        sub: config.sub,
        items: metrics,
      };
    }

    const fallbackItems = buildFeatureUsageFallbackItems(config.key, total);
    return {
      key: config.key,
      label: config.label,
      total: metricText('功能使用', [config.label], '0'),
      sub: config.sub,
      items: fallbackItems,
    };
  });
});

const orderCards = computed(() => [
  {label: '今日支付订单数', value: metricText('订单', ['今日支付订单数', '今日支付', '今日订单'], String(orders.value.filter(isPaidOrder).length)), sub: '已支付口径', tone: 'text-amber-700'},
  {label: '待完成订单', value: metricText('订单', ['待完成订单', '待完成'], String(orders.value.filter((order) => order.status === 'paid').length)), sub: '等待完成判定', tone: 'text-slate-700'},
  {label: '退款中', value: metricText('订单', ['退款中'], String(orders.value.filter((order) => order.status === 'refund_pending').length)), sub: '后台处理', tone: 'text-red-600'},
  {label: '本年度订单数量', value: metricText('订单', ['本年度订单数量', '本年度订单'], String(orders.value.length)), sub: '自然年累计', tone: 'text-slate-700'},
  {label: '已退款', value: metricText('订单', ['已退款'], String(orders.value.filter((order) => order.status === 'refunded').length)), sub: '退款归档', tone: 'text-slate-400'},
  {label: '总订单数量', value: metricText('订单', ['订单总数', '总订单数量'], String(orders.value.length)), sub: '全生命周期', tone: 'text-amber-700', featured: true},
]);

const promoCards = computed(() => [
  {label: '普通推广大使人数', value: metricText('推广合作', ['推广用户', '普通大使'], '0'), sub: '返佣比例可配置'},
  {label: '高级推广大使人数', value: metricText('推广合作', ['高级推广', '高级大使'], '0'), sub: '高级返佣比例可配置'},
]);

const promotionApplicationLoading = ref(false);
const promotionApplicationError = ref('');
const promotionApplications = ref<PromotionApplicationResponse[]>([]);
const selectedPromotionApplication = ref<PromotionApplicationResponse | null>(null);
const promotionRejectReason = ref('');
const promotionReviewNote = ref('');

const promotionCommissionLoading = ref(false);
const promotionCommissionError = ref('');
const promotionCommissions = ref<PromotionCommissionResponse[]>([]);
const selectedPromotionCommission = ref<PromotionCommissionResponse | null>(null);

const promotionWithdrawalLoading = ref(false);
const promotionWithdrawalError = ref('');
const promotionWithdrawals = ref<PromotionWithdrawalResponse[]>([]);
const selectedPromotionWithdrawal = ref<PromotionWithdrawalResponse | null>(null);
const withdrawalRejectReason = ref('');
const withdrawalReviewNote = ref('');
const withdrawalPayoutMethod = ref('');
const withdrawalPayoutProof = ref('');

const promotionRulesLoading = ref(false);
const promotionRulesError = ref('');
const promotionRules = ref<PromotionRulesResponse | null>(null);
const promotionRulesDraft = ref<PromotionRulesResponse | null>(null);
const promotionRulesSaving = ref(false);

const runtimeConfigLoading = ref(false);
const runtimeConfigError = ref('');
const runtimeConfigSchemaLoading = ref(false);
const runtimeConfigEntries = ref<RuntimeConfigEntryResponse[]>([]);
const runtimeConfigSchema = ref<RuntimeConfigSchemaItemResponse[]>([]);
const runtimeConfigDrafts = ref<Record<string, unknown>>({});
const runtimeConfigDirty = ref(false);

const featureConfigItems = computed(() => runtimeConfigSchema.value.filter((item) => item.group === '功能管理'));
const systemConfigItems = computed(() => runtimeConfigSchema.value.filter((item) => item.group === '系统配置'));

const visibleOrders = computed(() => {
  const keyword = orderSearchText.value.trim().toLowerCase();
  return orders.value.filter((order) => {
    const passKeyword = !keyword || [
      order.order_id,
      order.user_id,
      order.user_nickname || '',
      order.package_title,
      order.external_order_id || '',
    ].some((value) => value.toLowerCase().includes(keyword));
    const passStatus = !orderFilters.value.status || order.status === orderFilters.value.status;
    const passChannel = !orderFilters.value.channel || (order.channel || '').includes(orderFilters.value.channel);
    const passUser = !orderFilters.value.user_id || order.user_id.includes(orderFilters.value.user_id);
    return passKeyword && passStatus && passChannel && passUser;
  });
});

const latestPaidOrders = computed(() => visibleOrders.value.filter(isPaidOrder).slice(0, 2));

const visibleUsers = computed(() => {
  const keyword = userQuery.value.trim().toLowerCase();
  if (!keyword) {
    return users.value;
  }
  return users.value.filter((user) => [
    user.user_id,
    user.nickname || '',
    user.primary_phone || '',
    user.primary_unionid || '',
    user.unionid || '',
    user.guest_key || '',
    user.guest_unionid || '',
  ].some((value) => value.toLowerCase().includes(keyword)));
});

function isPrimaryNavKey(value: string | null): value is PrimaryNavKey {
  return ['dashboard', 'orders', 'users', 'features', 'promotion', 'settings'].includes(value || '');
}

function isFeatureNavKey(value: string | null): value is FeatureNavKey {
  return ['almanac', 'phone-review'].includes(value || '');
}

function isPromotionNavKey(value: string | null): value is PromotionNavKey {
  return ['review', 'withdrawals', 'commissions', 'rules'].includes(value || '');
}

function userDisplayLabel(userId: string) {
  if (selectedUser.value?.user.user_id === userId) {
    return selectedUser.value.user.nickname || selectedUser.value.user.primary_phone || shortText(userId, 8, 4);
  }
  const user = users.value.find((item) => item.user_id === userId);
  return user?.nickname || user?.primary_phone || shortText(userId, 8, 4);
}

function setUserReturnContext(userId: string, destination: UserLinkedDestination) {
  adminReturnContext.value = {
    userId,
    userLabel: userDisplayLabel(userId),
    destination,
  };
}

function clearLinkedUserContext() {
  adminReturnContext.value = null;
}

function clearLinkedUserFilters() {
  clearLinkedUserContext();
  usageFilters.value.user_id = '';
  orderFilters.value.user_id = '';
}

function writeAdminHistory(query: AdminRouteQuery, mode: 'push' | 'replace' = 'push') {
  if (typeof window === 'undefined') return;
  const url = new URL('/admin', window.location.origin);
  Object.entries(query).forEach(([key, value]) => {
    if (value) {
      url.searchParams.set(key, String(value));
    }
  });
  const state = {easewiseAdmin: true, ...query};
  if (mode === 'replace') {
    window.history.replaceState(state, '', url);
  } else {
    window.history.pushState(state, '', url);
  }
}

function clearOverlayState() {
  selectedUsage.value = null;
  selectedUser.value = null;
  selectedOrder.value = null;
  selectedPromotionApplication.value = null;
  selectedPromotionCommission.value = null;
  selectedPromotionWithdrawal.value = null;
  userEditOpen.value = false;
  userEditMode.value = null;
  userPointOperation.value = 'increase';
  expandedUserInfoKey.value = '';
}

async function restoreAdminStateFromLocation() {
  if (typeof window === 'undefined') {
    await loadActivePage();
    return;
  }
  const params = new URLSearchParams(window.location.search);
  const view = params.get('view');
  const userId = params.get('user_id') || '';
  if (!isPrimaryNavKey(view)) {
    activePrimary.value = 'dashboard';
    clearLinkedUserFilters();
    clearOverlayState();
    await loadActivePage();
    return;
  }

  activePrimary.value = view;
  clearOverlayState();

  if (view === 'features') {
    const featureParam = params.get('feature');
    activeFeature.value = isFeatureNavKey(featureParam) ? featureParam : 'phone-review';
    isFeaturesMenuOpen.value = true;
  }
  if (view === 'promotion') {
    const promotionParam = params.get('promotion');
    activePromotion.value = isPromotionNavKey(promotionParam) ? promotionParam : 'review';
    isPromoMenuOpen.value = true;
  }

  if (view === 'orders' && userId) {
    orderFilters.value.user_id = userId;
    if (params.get('return') === 'user') {
      setUserReturnContext(userId, 'orders');
    } else {
      clearLinkedUserContext();
    }
    await loadOrders();
    return;
  }

  if (view === 'features' && userId) {
    usageFilters.value.user_id = userId;
    if (params.get('return') === 'user') {
      setUserReturnContext(userId, 'usage');
    } else {
      clearLinkedUserContext();
    }
    await loadActivePage();
    return;
  }

  if (view === 'users') {
    clearLinkedUserFilters();
    if (userId) {
      userQuery.value = userId;
    }
    await loadUsers();
    if (params.get('modal') === 'user' && userId) {
      await openUserSummary(userId, {syncHistory: false});
    }
    return;
  }

  clearLinkedUserFilters();
  await loadActivePage();
}

function login() {
  const token = loginToken.value.trim();
  if (!token) {
    globalMessage.value = '请输入 Internal Admin Token';
    return;
  }
  adminToken.value = token;
  if (typeof window !== 'undefined') {
    window.localStorage.setItem(ADMIN_TOKEN_KEY, token);
  }
  globalMessage.value = '';
  void restoreAdminStateFromLocation();
}

function logout() {
  adminToken.value = '';
  loginToken.value = '';
  if (typeof window !== 'undefined') {
    window.localStorage.removeItem(ADMIN_TOKEN_KEY);
    window.history.replaceState({easewiseAdmin: true, view: 'dashboard'}, '', '/admin');
  }
  clearLinkedUserFilters();
  clearOverlayState();
  userEditOpen.value = false;
  userEditMode.value = null;
}

function goToFrontend() {
  if (typeof window !== 'undefined') {
    window.location.href = '/';
  }
}

function switchPrimary(key: PrimaryNavKey) {
  clearLinkedUserFilters();
  activePrimary.value = key;
  clearOverlayState();
  if (key === 'features') {
    isFeaturesMenuOpen.value = true;
  }
  if (key === 'promotion') {
    isPromoMenuOpen.value = true;
  }
  writeAdminHistory({
    view: key,
    feature: key === 'features' ? activeFeature.value : undefined,
    promotion: key === 'promotion' ? activePromotion.value : undefined,
  });
  void loadActivePage();
}

function toggleFeaturesPrimary() {
  clearLinkedUserFilters();
  isFeaturesMenuOpen.value = !isFeaturesMenuOpen.value;
  activePrimary.value = 'features';
  clearOverlayState();
  writeAdminHistory({view: 'features', feature: activeFeature.value});
  void loadActivePage();
}

function togglePromotionPrimary() {
  clearLinkedUserFilters();
  isPromoMenuOpen.value = !isPromoMenuOpen.value;
  activePrimary.value = 'promotion';
  clearOverlayState();
  writeAdminHistory({view: 'promotion', promotion: activePromotion.value});
  void loadPromotionPage();
}

async function loadActivePage() {
  if (!adminToken.value) {
    return;
  }
  if (activePrimary.value === 'dashboard') {
    await Promise.allSettled([loadDashboard(), loadOrders(), loadUsers(), loadUsageRecords(), loadLlmKeys()]);
  }
  if (activePrimary.value === 'features') {
    await Promise.allSettled([loadRuntimeSchema(), loadRuntimeConfig()]);
  }
  if (activePrimary.value === 'settings') {
    await Promise.allSettled([loadLlmKeys(), loadRuntimeSchema(), loadRuntimeConfig()]);
  }
  if (activePrimary.value === 'features' && activeFeature.value === 'phone-review') {
    await loadUsageRecords();
  }
  if (activePrimary.value === 'users') {
    await loadUsers();
  }
  if (activePrimary.value === 'orders') {
    await loadOrders();
  }
  if (activePrimary.value === 'promotion') {
    await loadPromotionPage();
  }
}

async function loadDashboard() {
  dashboardLoading.value = true;
  dashboardError.value = '';
  try {
    dashboard.value = await getInternalDashboard(adminToken.value);
    globalMessage.value = '';
  } catch (error) {
    const message = resolveError(error);
    dashboardError.value = message;
    globalMessage.value = message;
  } finally {
    dashboardLoading.value = false;
  }
}

async function loadLlmKeys() {
  llmLoading.value = true;
  llmError.value = '';
  try {
    llmKeys.value = (await listInternalLlmApiKeys(adminToken.value)).items;
    globalMessage.value = '';
  } catch (error) {
    const message = resolveError(error);
    llmError.value = message;
    globalMessage.value = message;
  } finally {
    llmLoading.value = false;
  }
}

async function loadRuntimeSchema() {
  runtimeConfigSchemaLoading.value = true;
  runtimeConfigError.value = '';
  try {
    runtimeConfigSchema.value = (await getInternalRuntimeConfigSchema(adminToken.value)).items;
    globalMessage.value = '';
  } catch (error) {
    const message = resolveError(error);
    runtimeConfigError.value = message;
    globalMessage.value = message;
  } finally {
    runtimeConfigSchemaLoading.value = false;
  }
}

async function loadRuntimeConfig() {
  runtimeConfigLoading.value = true;
  runtimeConfigError.value = '';
  try {
    runtimeConfigEntries.value = (await listInternalRuntimeConfig(adminToken.value)).items;
    runtimeConfigDrafts.value = {};
    for (const entry of runtimeConfigEntries.value) {
      runtimeConfigDrafts.value[entry.config_key] = entry.value !== null && typeof entry.value === 'object'
        ? JSON.stringify(entry.value, null, 2)
        : entry.value;
    }
    runtimeConfigDirty.value = false;
    globalMessage.value = '';
  } catch (error) {
    const message = resolveError(error);
    runtimeConfigError.value = message;
    globalMessage.value = message;
  } finally {
    runtimeConfigLoading.value = false;
  }
}

async function loadUsageRecords() {
  usageLoading.value = true;
  usageError.value = '';
  try {
    usageRecords.value = (await listInternalUsageRecords(adminToken.value, {
      ...usageFilters.value,
      include_hidden: activePrimary.value === 'features' ? false : undefined,
    })).items;
    globalMessage.value = '';
  } catch (error) {
    const message = resolveError(error);
    usageError.value = message;
    globalMessage.value = message;
  } finally {
    usageLoading.value = false;
  }
}

async function openUsageDetail(record: UsageRecordResponse) {
  usageDetailLoading.value = true;
  try {
    selectedUsage.value = await getInternalUsageRecord(adminToken.value, record.usage_record_id);
    globalMessage.value = '';
  } catch (error) {
    globalMessage.value = resolveError(error);
  } finally {
    usageDetailLoading.value = false;
  }
}

async function loadUsers() {
  userLoading.value = true;
  userError.value = '';
  try {
    users.value = (await listInternalUsers(adminToken.value, {
      keyword: userQuery.value,
      ...userFilters.value,
    })).items;
    globalMessage.value = '';
  } catch (error) {
    const message = resolveError(error);
    userError.value = message;
    globalMessage.value = message;
  } finally {
    userLoading.value = false;
  }
}

function resetUserFilters() {
  userQuery.value = '';
  userFilters.value = {status: '', identity_level: '', channel: ''};
}

async function openUserSummary(userId: string, options: {syncHistory?: boolean} = {}) {
  userLoading.value = true;
  userEditOpen.value = false;
  userEditMode.value = null;
  expandedUserInfoKey.value = '';
  try {
    selectedUser.value = await getInternalUserAdminSummary(adminToken.value, userId);
    if (options.syncHistory !== false) {
      writeAdminHistory({view: 'users', modal: 'user', user_id: userId});
    }
    globalMessage.value = '';
  } catch (error) {
    globalMessage.value = resolveError(error);
  } finally {
    userLoading.value = false;
  }
}

function closeUserSummary() {
  selectedUser.value = null;
  userEditOpen.value = false;
  userEditMode.value = null;
  userEditValue.value = '';
  userEditReason.value = '';
  userEditNote.value = '';
  userPointOperation.value = 'increase';
  expandedUserInfoKey.value = '';
  if (activePrimary.value === 'users') {
    writeAdminHistory({view: 'users'}, 'replace');
  }
}

async function loadOrders() {
  orderLoading.value = true;
  orderError.value = '';
  try {
    orders.value = (await listInternalRechargeOrders(adminToken.value, {
      ...orderFilters.value,
      keyword: orderSearchText.value,
    })).items;
    globalMessage.value = '';
  } catch (error) {
    const message = resolveError(error);
    orderError.value = message;
    globalMessage.value = message;
  } finally {
    orderLoading.value = false;
  }
}

async function openOrderDetail(order: RechargeOrderResponse) {
  orderDetailLoading.value = true;
  selectedOrder.value = null;
  orderActionMessage.value = '';
  orderReviewNote.value = '';
  orderRefundReason.value = '';
  try {
    selectedOrder.value = await getInternalRechargeOrder(adminToken.value, order.order_id);
    globalMessage.value = '';
  } catch (error) {
    globalMessage.value = resolveError(error);
  } finally {
    orderDetailLoading.value = false;
  }
}

async function reviewSelectedOrder(action: 'approve' | 'reject') {
  if (!selectedOrder.value) return;
  orderActionMessage.value = '';
  try {
    const result = await reviewInternalRechargeOrder(adminToken.value, selectedOrder.value.order_id, {
      action,
      review_note: orderReviewNote.value || null,
    });
    selectedOrder.value = result.order;
    orderActionMessage.value = action === 'approve' ? '订单已通过，已进入积分发放流程' : '订单已拒绝';
    orderReviewNote.value = '';
    await loadOrders();
  } catch (error) {
    orderActionMessage.value = resolveError(error);
  }
}

async function createRefundFromSelectedOrder() {
  if (!selectedOrder.value) return;
  orderActionMessage.value = '';
  try {
    const refund = await createInternalRechargeOrderRefund(adminToken.value, selectedOrder.value.order_id, {
      reason: orderRefundReason.value || null,
      operator_note: orderReviewNote.value || null,
    });
    orderActionMessage.value = `已创建退款请求：${refund.refund_id}`;
    orderRefundReason.value = '';
    orderReviewNote.value = '';
    await openOrderDetail(selectedOrder.value);
    await loadOrders();
  } catch (error) {
    orderActionMessage.value = resolveError(error);
  }
}

function jumpToUser(userId: string) {
  activePrimary.value = 'users';
  userQuery.value = userId;
  clearLinkedUserFilters();
  clearOverlayState();
  writeAdminHistory({view: 'users', modal: 'user', user_id: userId});
  void loadUsers().then(() => openUserSummary(userId, {syncHistory: false}));
}

function jumpToUsageForUser(userId: string) {
  activePrimary.value = 'features';
  activeFeature.value = 'phone-review';
  isFeaturesMenuOpen.value = true;
  usageFilters.value.user_id = userId;
  setUserReturnContext(userId, 'usage');
  clearOverlayState();
  writeAdminHistory({view: 'features', feature: 'phone-review', user_id: userId, return: 'user'});
  void loadActivePage();
}

function jumpToOrders(userId: string) {
  activePrimary.value = 'orders';
  orderFilters.value.user_id = userId;
  setUserReturnContext(userId, 'orders');
  clearOverlayState();
  writeAdminHistory({view: 'orders', user_id: userId, return: 'user'});
  void loadOrders();
}

function returnToUserFile() {
  const userId = adminReturnContext.value?.userId;
  if (!userId) return;
  activePrimary.value = 'users';
  userQuery.value = userId;
  clearLinkedUserFilters();
  clearOverlayState();
  writeAdminHistory({view: 'users', modal: 'user', user_id: userId});
  void loadUsers().then(() => openUserSummary(userId, {syncHistory: false}));
}

function clearOrderUserScope() {
  orderFilters.value.user_id = '';
  clearLinkedUserContext();
  selectedOrder.value = null;
  writeAdminHistory({view: 'orders'}, 'replace');
  void loadOrders();
}

function clearUsageUserScope() {
  usageFilters.value.user_id = '';
  clearLinkedUserContext();
  selectedUsage.value = null;
  writeAdminHistory({view: 'features', feature: activeFeature.value}, 'replace');
  void loadUsageRecords();
}

function selectFeature(key: FeatureNavKey) {
  clearLinkedUserFilters();
  isFeaturesMenuOpen.value = true;
  activeFeature.value = key;
  activePrimary.value = 'features';
  selectedUsage.value = null;
  writeAdminHistory({view: 'features', feature: key});
  if (key === 'phone-review') {
    void loadUsageRecords();
  }
}

function selectPromotion(key: PromotionNavKey) {
  clearLinkedUserFilters();
  isPromoMenuOpen.value = true;
  activePromotion.value = key;
  activePrimary.value = 'promotion';
  selectedPromotionApplication.value = null;
  selectedPromotionCommission.value = null;
  selectedPromotionWithdrawal.value = null;
  writeAdminHistory({view: 'promotion', promotion: key});
  void loadPromotionPage();
}

async function loadPromotionPage() {
  if (activePromotion.value === 'review') {
    await loadPromotionApplications();
  }
  if (activePromotion.value === 'withdrawals') {
    await loadPromotionWithdrawals();
  }
  if (activePromotion.value === 'commissions') {
    await loadPromotionCommissions();
  }
  if (activePromotion.value === 'rules') {
    await loadPromotionRules();
  }
}

async function loadPromotionApplications() {
  promotionApplicationLoading.value = true;
  promotionApplicationError.value = '';
  try {
    promotionApplications.value = (await listInternalPromotionApplications(adminToken.value)).items;
    globalMessage.value = '';
  } catch (error) {
    const message = resolveError(error);
    promotionApplicationError.value = message;
    globalMessage.value = message;
  } finally {
    promotionApplicationLoading.value = false;
  }
}

async function openPromotionApplication(applicationId: string) {
  selectedPromotionApplication.value = null;
  promotionRejectReason.value = '';
  promotionReviewNote.value = '';
  try {
    selectedPromotionApplication.value = await getInternalPromotionApplication(adminToken.value, applicationId);
  } catch (error) {
    globalMessage.value = resolveError(error);
  }
}

async function reviewPromotionApplication(action: 'approve' | 'reject') {
  if (!selectedPromotionApplication.value) return;
  try {
    selectedPromotionApplication.value = await reviewInternalPromotionApplication(adminToken.value, selectedPromotionApplication.value.application_id, {
      action,
      reject_reason: action === 'reject' ? promotionRejectReason.value || null : null,
      review_note: promotionReviewNote.value || null,
      operator_note: promotionReviewNote.value || null,
    });
    promotionRejectReason.value = '';
    promotionReviewNote.value = '';
    await loadPromotionApplications();
  } catch (error) {
    globalMessage.value = resolveError(error);
  }
}

async function loadPromotionCommissions() {
  promotionCommissionLoading.value = true;
  promotionCommissionError.value = '';
  try {
    promotionCommissions.value = (await listInternalPromotionCommissions(adminToken.value)).items;
    globalMessage.value = '';
  } catch (error) {
    const message = resolveError(error);
    promotionCommissionError.value = message;
    globalMessage.value = message;
  } finally {
    promotionCommissionLoading.value = false;
  }
}

async function openPromotionCommission(commissionId: string) {
  selectedPromotionCommission.value = null;
  try {
    selectedPromotionCommission.value = await getInternalPromotionCommission(adminToken.value, commissionId);
  } catch (error) {
    globalMessage.value = resolveError(error);
  }
}

async function loadPromotionWithdrawals() {
  promotionWithdrawalLoading.value = true;
  promotionWithdrawalError.value = '';
  try {
    promotionWithdrawals.value = (await listInternalPromotionWithdrawals(adminToken.value)).items;
    globalMessage.value = '';
  } catch (error) {
    const message = resolveError(error);
    promotionWithdrawalError.value = message;
    globalMessage.value = message;
  } finally {
    promotionWithdrawalLoading.value = false;
  }
}

async function openPromotionWithdrawal(withdrawalId: string) {
  selectedPromotionWithdrawal.value = null;
  withdrawalRejectReason.value = '';
  withdrawalReviewNote.value = '';
  withdrawalPayoutMethod.value = '';
  withdrawalPayoutProof.value = '';
  try {
    selectedPromotionWithdrawal.value = await getInternalPromotionWithdrawal(adminToken.value, withdrawalId);
  } catch (error) {
    globalMessage.value = resolveError(error);
  }
}

async function reviewPromotionWithdrawal(action: 'approve' | 'reject') {
  if (!selectedPromotionWithdrawal.value) return;
  try {
    selectedPromotionWithdrawal.value = await reviewInternalPromotionWithdrawal(adminToken.value, selectedPromotionWithdrawal.value.withdrawal_id, {
      action,
      reject_reason: action === 'reject' ? withdrawalRejectReason.value || null : null,
      review_note: withdrawalReviewNote.value || null,
      operator_note: withdrawalReviewNote.value || null,
    });
    withdrawalRejectReason.value = '';
    withdrawalReviewNote.value = '';
    await loadPromotionWithdrawals();
  } catch (error) {
    globalMessage.value = resolveError(error);
  }
}

async function retryPromotionWithdrawal() {
  if (!selectedPromotionWithdrawal.value) return;
  try {
    selectedPromotionWithdrawal.value = await retryInternalPromotionWithdrawalPayout(adminToken.value, selectedPromotionWithdrawal.value.withdrawal_id, {
      operator_note: withdrawalReviewNote.value || null,
    });
    withdrawalReviewNote.value = '';
    await loadPromotionWithdrawals();
  } catch (error) {
    globalMessage.value = resolveError(error);
  }
}

async function markPromotionWithdrawalPaid() {
  if (!selectedPromotionWithdrawal.value) return;
  try {
    selectedPromotionWithdrawal.value = await markInternalPromotionWithdrawalPaid(adminToken.value, selectedPromotionWithdrawal.value.withdrawal_id, {
      payout_method: withdrawalPayoutMethod.value || null,
      payout_proof: withdrawalPayoutProof.value || null,
      operator_note: withdrawalReviewNote.value || null,
    });
    withdrawalPayoutMethod.value = '';
    withdrawalPayoutProof.value = '';
    withdrawalReviewNote.value = '';
    await loadPromotionWithdrawals();
  } catch (error) {
    globalMessage.value = resolveError(error);
  }
}

async function loadPromotionRules() {
  promotionRulesLoading.value = true;
  promotionRulesError.value = '';
  try {
    promotionRules.value = await getInternalPromotionRules(adminToken.value);
    promotionRulesDraft.value = {...promotionRules.value};
    globalMessage.value = '';
  } catch (error) {
    const message = resolveError(error);
    promotionRulesError.value = message;
    globalMessage.value = message;
  } finally {
    promotionRulesLoading.value = false;
  }
}

async function savePromotionRules() {
  if (!promotionRulesDraft.value) return;
  promotionRulesSaving.value = true;
  try {
    promotionRules.value = await updateInternalPromotionRules(adminToken.value, promotionRulesDraft.value);
    promotionRulesDraft.value = {...promotionRules.value};
    globalMessage.value = '';
  } catch (error) {
    globalMessage.value = resolveError(error);
  } finally {
    promotionRulesSaving.value = false;
  }
}

function normalizeRuntimeConfigValue(item: RuntimeConfigSchemaItemResponse, rawValue: unknown) {
  if (item.value_type === 'bool') {
    return Boolean(rawValue);
  }
  if (item.value_type === 'int') {
    const parsed = Number.parseInt(String(rawValue), 10);
    return Number.isFinite(parsed) ? parsed : item.default_value;
  }
  if (item.value_type === 'float') {
    const parsed = Number.parseFloat(String(rawValue));
    return Number.isFinite(parsed) ? parsed : item.default_value;
  }
  if (item.value_type === 'json') {
    if (typeof rawValue === 'string') {
      try {
        return JSON.parse(rawValue);
      } catch {
        return item.default_value;
      }
    }
    return rawValue;
  }
  return rawValue;
}

function runtimeConfigDisplayValue(item: RuntimeConfigSchemaItemResponse) {
  const value = runtimeConfigDrafts.value[item.config_key];
  if (value === undefined || value === null || value === '') {
    return item.default_value;
  }
  return value;
}

async function saveRuntimeConfig() {
  if (!runtimeConfigSchema.value.length) return;
  const entries: RuntimeConfigEntryUpsertRequest[] = runtimeConfigSchema.value.map((item) => ({
    scope_type: item.scope_type,
    scope_key: item.scope_key,
    config_key: item.config_key,
    value: normalizeRuntimeConfigValue(item, runtimeConfigDrafts.value[item.config_key]),
  }));
  runtimeConfigLoading.value = true;
  try {
    const result = await updateInternalRuntimeConfig(adminToken.value, entries);
    runtimeConfigEntries.value = result.items;
    runtimeConfigDirty.value = false;
    globalMessage.value = '系统配置已保存';
  } catch (error) {
    globalMessage.value = resolveError(error);
  } finally {
    runtimeConfigLoading.value = false;
  }
}

function beginCreateLlmKey() {
  llmKeyFormMode.value = 'create';
  llmEditingKeyId.value = '';
  llmKeyForm.value = {
    provider: 'deepseek',
    model: 'deepseek-chat',
    display_name: '',
    masked_key: '',
    secret_ref: '',
    enabled: true,
    priority: 100,
    remark: '',
    last_operator: 'internal_admin',
  };
}

function beginEditLlmKey(item: LlmApiKeyResponse) {
  llmKeyFormMode.value = 'edit';
  llmEditingKeyId.value = item.key_id;
  llmKeyForm.value = {
    provider: item.provider,
    model: item.model,
    display_name: item.display_name,
    masked_key: item.masked_key,
    secret_ref: item.secret_ref,
    enabled: item.enabled,
    priority: item.priority,
    remark: item.remark || '',
    last_operator: item.last_operator || 'internal_admin',
  };
}

async function submitLlmKeyForm() {
  llmLoading.value = true;
  try {
    if (llmKeyFormMode.value === 'edit' && llmEditingKeyId.value) {
      await updateInternalLlmApiKey(adminToken.value, llmEditingKeyId.value, llmKeyForm.value);
    } else {
      await createInternalLlmApiKey(adminToken.value, llmKeyForm.value);
    }
    llmKeyFormMode.value = null;
    llmEditingKeyId.value = '';
    await loadLlmKeys();
  } catch (error) {
    globalMessage.value = resolveError(error);
  } finally {
    llmLoading.value = false;
  }
}

async function removeLlmKey(keyId: string) {
  if (typeof window !== 'undefined' && !window.confirm('确认删除该密钥占位配置？')) return;
  try {
    await deleteInternalLlmApiKey(adminToken.value, keyId);
    await loadLlmKeys();
  } catch (error) {
    globalMessage.value = resolveError(error);
  }
}

function openUserEditor(mode: 'points' | 'status' | 'identity' | 'parent') {
  userEditMode.value = mode;
  userEditOpen.value = true;
  userEditReason.value = '';
  userEditNote.value = '';
  userEditValue.value = '';
  if (!selectedUser.value) return;
  if (mode === 'points') {
    userPointOperation.value = 'increase';
    userEditValue.value = '0';
  }
  if (mode === 'status') {
    userEditValue.value = selectedUser.value.user.status;
  }
  if (mode === 'identity') {
    userEditValue.value = selectedUser.value.identity_level || selectedUser.value.user.identity_level;
  }
  if (mode === 'parent') {
    userEditValue.value = selectedUser.value.promoter_parent_user_id || '';
  }
}

async function submitUserEdit() {
  if (!selectedUser.value || !userEditMode.value) return;
  userLoading.value = true;
  try {
    const userId = selectedUser.value.user.user_id;
    if (userEditMode.value === 'points') {
      const rawAmount = Number(userEditValue.value);
      if (!Number.isFinite(rawAmount) || rawAmount < 0) {
        globalMessage.value = '请输入不小于 0 的积分数';
        return;
      }
      const amount = Math.trunc(rawAmount);
      const currentBalance = selectedUser.value.user.points_balance;
      const delta = userPointOperation.value === 'increase'
        ? amount
        : userPointOperation.value === 'decrease'
          ? -amount
          : amount - currentBalance;
      await adjustInternalUserPoints(adminToken.value, userId, {
        delta,
        reason: userEditReason.value || null,
        operator_note: userEditNote.value || null,
      });
    } else if (userEditMode.value === 'status') {
      await updateInternalUserStatus(adminToken.value, userId, {
        status: userEditValue.value,
        reason: userEditReason.value || null,
        operator_note: userEditNote.value || null,
      });
    } else if (userEditMode.value === 'identity') {
      await updateInternalUserIdentity(adminToken.value, userId, {
        identity_level: userEditValue.value,
        reason: userEditReason.value || null,
        operator_note: userEditNote.value || null,
      });
    } else if (userEditMode.value === 'parent') {
      await updateInternalUserPromoterParent(adminToken.value, userId, {
        promoter_parent_user_id: userEditValue.value || null,
        reason: userEditReason.value || null,
        operator_note: userEditNote.value || null,
      });
    }
    await openUserSummary(userId, {syncHistory: false});
    userEditOpen.value = false;
    userEditMode.value = null;
    await loadUsers();
  } catch (error) {
    globalMessage.value = resolveError(error);
  } finally {
    userLoading.value = false;
  }
}

function findMetric(sectionTitle: string, labels: string[]): DashboardMetric | null {
  const section = dashboard.value?.sections.find((item) => item.title === sectionTitle);
  if (!section) {
    return null;
  }
  return section.metrics.find((metric) => labels.includes(metric.label)) || null;
}

function getSectionMetrics(sectionTitle: string) {
  return dashboard.value?.sections.find((item) => item.title === sectionTitle)?.metrics || [];
}

function metricText(sectionTitle: string, labels: string[], fallback: string) {
  return findMetric(sectionTitle, labels)?.display_value || fallback;
}

function metricNumber(sectionTitle: string, labels: string[], fallback = 0) {
  const value = findMetric(sectionTitle, labels)?.value;
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value;
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function metricCurrency(sectionTitle: string, labels: string[], fallback: string) {
  return metricText(sectionTitle, labels, fallback).replace(/^¥|^￥/, '');
}

function featureUsageDisplayName(scene: string, featureName: string | null | undefined) {
  return featureUsageSceneLabels[scene] || featureName || scene || '未知功能';
}

function parseUtc8DateKey(value: string | null | undefined) {
  if (!value) return '';
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return '';
  const shifted = new Date(parsed.getTime() + 8 * 60 * 60 * 1000);
  return `${shifted.getUTCFullYear()}-${String(shifted.getUTCMonth() + 1).padStart(2, '0')}-${String(shifted.getUTCDate()).padStart(2, '0')}`;
}

function currentUtc8DateKey() {
  const shifted = new Date(Date.now() + 8 * 60 * 60 * 1000);
  return `${shifted.getUTCFullYear()}-${String(shifted.getUTCMonth() + 1).padStart(2, '0')}-${String(shifted.getUTCDate()).padStart(2, '0')}`;
}

function currentUtc8MonthKey() {
  const shifted = new Date(Date.now() + 8 * 60 * 60 * 1000);
  return `${shifted.getUTCFullYear()}-${String(shifted.getUTCMonth() + 1).padStart(2, '0')}`;
}

function currentUtc8WeekStartKey() {
  const shifted = new Date(Date.now() + 8 * 60 * 60 * 1000);
  const day = shifted.getUTCDay();
  const diffToMonday = (day + 6) % 7;
  const monday = new Date(Date.UTC(
    shifted.getUTCFullYear(),
    shifted.getUTCMonth(),
    shifted.getUTCDate() - diffToMonday,
  ));
  return `${monday.getUTCFullYear()}-${String(monday.getUTCMonth() + 1).padStart(2, '0')}-${String(monday.getUTCDate()).padStart(2, '0')}`;
}

function isUsageRecordInWindow(record: UsageRecordResponse, windowKey: FeatureUsageWindowKey) {
  const dateKey = parseUtc8DateKey(record.created_at);
  if (!dateKey) return false;
  const todayKey = currentUtc8DateKey();
  if (windowKey === 'today') {
    return dateKey === todayKey;
  }
  if (windowKey === 'yesterday') {
    const today = new Date(Date.UTC(
      Number(todayKey.slice(0, 4)),
      Number(todayKey.slice(5, 7)) - 1,
      Number(todayKey.slice(8, 10)),
    ));
    const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000);
    const yesterdayKey = `${yesterday.getUTCFullYear()}-${String(yesterday.getUTCMonth() + 1).padStart(2, '0')}-${String(yesterday.getUTCDate()).padStart(2, '0')}`;
    return dateKey === yesterdayKey;
  }
  if (windowKey === 'week') {
    return dateKey >= currentUtc8WeekStartKey();
  }
  if (windowKey === 'month') {
    return dateKey.slice(0, 7) === currentUtc8MonthKey();
  }
  return false;
}

function buildFeatureUsageFallbackItems(windowKey: FeatureUsageWindowKey, total: number): FeatureUsageRankItem[] {
  const counts = new Map<string, number>();
  usageRecords.value
    .filter((record) => isUsageRecordInWindow(record, windowKey))
    .forEach((record) => {
      const name = featureUsageDisplayName(record.scene, record.feature_name);
      counts.set(name, (counts.get(name) || 0) + 1);
    });
  return [...counts.entries()]
    .map(([name, count]) => ({
      name,
      count,
      percentage: total > 0 ? Math.round((count / total) * 100) : 0,
    }))
    .sort((left, right) => right.count - left.count)
    .slice(0, 5);
}

function isPaidOrder(order: RechargeOrderResponse) {
  return order.status === 'paid' || order.status === 'completed';
}

function formatAmount(cents: number) {
  return `¥${(cents / 100).toFixed(2)}`;
}

function formatRate(rate: number | null | undefined) {
  if (rate === null || rate === undefined) {
    return '--';
  }
  return `${(rate * 100).toFixed(1)}%`;
}

function formatTime(value: string | null | undefined) {
  if (!value) {
    return '--';
  }
  return value.replace('T', ' ').replace('+00:00', '');
}

function orderStatusLabel(status: string) {
  const map: Record<string, string> = {
    unpaid: '待支付',
    paid: '已支付',
    completed: '已完成',
    refund_pending: '退款中',
    refunded: '已退款',
    closed: '已关闭',
  };
  return map[status] || status;
}

function orderStatusClass(status: string) {
  if (status === 'completed') return 'bg-emerald-50 text-emerald-600 border-emerald-100';
  if (status === 'paid') return 'bg-blue-50 text-blue-600 border-blue-100';
  if (status === 'refund_pending') return 'bg-red-50 text-red-600 border-red-100 animate-pulse';
  if (status === 'refunded') return 'bg-gray-50 text-gray-400 border-gray-200';
  if (status === 'closed') return 'bg-slate-50 text-slate-400 border-slate-200';
  return 'bg-amber-50 text-amber-600 border-amber-100';
}

function usageStatusClass(status: string) {
  if (status === 'success' || status === 'completed') return 'bg-emerald-50 text-emerald-600 border-emerald-100';
  if (status === 'failed') return 'bg-red-50 text-red-600 border-red-100';
  return 'bg-amber-50 text-amber-600 border-amber-100';
}

function userStatusLabel(status: string) {
  const map: Record<string, string> = {
    active: '正常活动中',
    guest: '游客',
    disabled: '已禁用',
    blocked: '已封禁',
    inactive: '未激活',
  };
  return map[status] || status;
}

function identityLabel(identity: string | null | undefined) {
  const map: Record<string, string> = {
    normal_user: '普通会员',
    promoter: '推广大使',
    promotion_ambassador: '推广大使',
    senior_promoter: '高级推广大使',
    senior_promotion_ambassador: '高级推广大使',
  };
  return map[identity || ''] || identity || '--';
}

function identitySourceLabel(identityType: string | null | undefined) {
  const map: Record<string, string> = {
    phone: '手机号',
    wechat_unionid: '微信 UnionID',
    wechat_pending_unionid: '微信待补 UnionID',
    session: 'Session 临时态',
  };
  return map[identityType || 'session'] || identityType || 'Session 临时态';
}

function userPrimaryIdentityLine(user: InternalUserResponse) {
  return user.primary_phone || user.primary_unionid || user.guest_key || user.user_id;
}

function selectedUserIdentityValue() {
  const user = selectedUser.value?.user;
  if (!user) return '--';
  return user.primary_unionid || user.guest_key || user.guest_unionid || user.guest_openid || '--';
}

function toggleUserInfoCard(key: string) {
  expandedUserInfoKey.value = expandedUserInfoKey.value === key ? '' : key;
}

function compactUserInfoValue(item: SelectedUserInfoCard) {
  if (!item.value || item.value === '--') return '--';
  if (item.key === 'registered_at') return item.value.slice(0, 16);
  if (item.key === 'unionid') return shortText(item.value, 8, 4);
  return shortText(item.value, 10, 6);
}

function compactUserInfoSub(item: SelectedUserInfoCard) {
  if (!item.sub || item.sub === '--') return '--';
  if (item.key === 'registered_at') return item.sub.slice(0, 19);
  return shortText(item.sub, 9, 4);
}

function shortText(value: string | null | undefined, head = 8, tail = 4) {
  if (!value) return '--';
  if (value.length <= head + tail + 3) return value;
  return `${value.slice(0, head)}...${value.slice(-tail)}`;
}

function promotionStatusLabel(status: string) {
  const map: Record<string, string> = {
    pending: '待审核',
    approved: '已通过',
    rejected: '已拒绝',
    paying: '打款中',
    paid: '已打款',
    payout_failed: '打款失败',
    settled: '已结算',
    revoked: '已撤回',
  };
  return map[status] || status;
}

function promotionStatusClass(status: string) {
  if (status === 'approved' || status === 'settled' || status === 'paid') return 'bg-emerald-50 text-emerald-600 border-emerald-100';
  if (status === 'pending' || status === 'paying') return 'bg-amber-50 text-amber-700 border-amber-100';
  if (status === 'payout_failed') return 'bg-red-50 text-red-600 border-red-100';
  if (status === 'rejected' || status === 'revoked') return 'bg-slate-50 text-slate-500 border-slate-200';
  return 'bg-gray-50 text-gray-500 border-gray-100';
}

function runtimeInputText(item: RuntimeConfigSchemaItemResponse) {
  const value = runtimeConfigDisplayValue(item);
  if (item.value_type === 'json') {
    return JSON.stringify(value ?? item.default_value, null, 2);
  }
  return String(value ?? '');
}

function resolveError(error: unknown) {
  if (error instanceof ApiError) {
    if (error.status === 401) {
      return '后台 token 无效，请重新登录';
    }
    if (error.status === 503) {
      return '后台 token 尚未在服务端配置';
    }
    return `${error.status}: ${error.detail}`;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return '请求失败，请稍后重试';
}

function handleAdminPopState() {
  if (isLoggedIn.value) {
    void restoreAdminStateFromLocation();
  }
}

onMounted(() => {
  if (typeof window !== 'undefined') {
    window.addEventListener('popstate', handleAdminPopState);
  }
  if (isLoggedIn.value) {
    void restoreAdminStateFromLocation();
  }
});

onBeforeUnmount(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('popstate', handleAdminPopState);
  }
});
</script>

<template>
  <div class="min-h-screen bg-brand-paper text-brand-ink font-sans leading-normal overflow-x-hidden relative select-none">
    <div v-if="!isLoggedIn" class="min-h-screen flex items-center justify-center p-6 bg-brand-paper relative">
      <div class="absolute inset-0 pointer-events-none opacity-5" style="background-image: radial-gradient(#4F46E5 1px, transparent 1px); background-size: 20px 20px;"></div>

      <div class="w-full max-w-md bg-white border border-gray-100 rounded-3xl p-8 shadow-xl relative overflow-hidden z-10">
        <div class="absolute -top-12 -left-12 w-40 h-40 bg-brand-primary/5 rounded-full blur-3xl"></div>
        <div class="absolute -bottom-12 -right-12 w-40 h-40 bg-brand-primary/5 rounded-full blur-3xl"></div>

        <div class="text-center space-y-3 mb-8">
          <div class="w-16 h-16 bg-gradient-to-tr from-brand-primary to-brand-primary-strong rounded-2xl mx-auto flex items-center justify-center shadow-md transform rotate-6 hover:rotate-12 transition-transform duration-300">
            <span class="text-3xl font-serif text-white font-bold">易</span>
          </div>
          <h1 class="text-2xl font-serif font-bold text-brand-ink-strong tracking-widest">易如反掌运营中枢</h1>
          <p class="text-xs text-brand-secondary">EaseWise Admin — 数字化现代命理桌面管理端</p>
        </div>

        <div class="space-y-4">
          <div class="space-y-1">
            <label class="text-[11px] font-bold tracking-wider text-brand-secondary uppercase font-mono block">OPERATOR INTERNAL ACCESS TOKEN</label>
            <input
              v-model="loginToken"
              type="password"
              placeholder="请输入 Internal Admin Token"
              @keyup.enter="login"
              class="w-full bg-white border border-gray-200 p-3 rounded-xl text-xs text-center font-mono text-brand-ink focus:border-brand-primary outline-none transition-colors"
            />
            <p v-if="globalMessage" class="text-[10px] text-red-500 font-medium">{{ globalMessage }}</p>
          </div>

          <button
            @click="login"
            class="w-full bg-brand-primary hover:bg-brand-primary-strong text-white font-bold py-3 px-4 rounded-xl text-xs transition-all outline-none cursor-pointer shadow-md shadow-brand-primary/10 active:scale-[0.98]"
          >
            校合进入中枢 (Access System)
          </button>
        </div>
      </div>
    </div>

    <div v-else class="min-h-screen flex text-left relative">
      <aside class="w-64 shrink-0 bg-white border-r border-gray-100 flex flex-col justify-between sticky top-0 h-screen select-none font-mono">
        <div class="flex flex-col">
          <div class="p-6 border-b border-gray-100 flex items-center gap-3">
            <div class="w-10 h-10 bg-brand-primary rounded-xl flex items-center justify-center shrink-0 shadow-md shadow-brand-primary/10">
              <span class="text-xl font-serif text-white font-bold">易</span>
            </div>
            <div class="block">
              <h1 class="text-sm font-bold text-brand-ink-strong tracking-widest leading-none font-sans">易如反掌</h1>
              <p class="text-[9.5px] text-brand-secondary mt-1 uppercase">EaseWise Admin</p>
            </div>
          </div>

          <nav class="p-4 space-y-1 font-sans">
            <button
              v-for="(item, index) in flatNavItems"
              :key="item.key"
              @click="switchPrimary(item.key)"
              class="w-full flex items-center justify-between p-3 rounded-lg text-xs font-bold transition-all outline-none cursor-pointer"
              :class="activePrimary === item.key ? 'bg-brand-primary text-white shadow-md shadow-brand-primary/15' : 'text-brand-ink/70 hover:bg-brand-paper hover:text-brand-ink-strong'"
            >
              <div class="flex items-center gap-2.5">
                <component :is="primaryNavIcons[item.key]" :size="15" />
                <span>{{ index + 1 }}. {{ item.label }}</span>
              </div>
            </button>

            <div class="block">
              <button
                @click="toggleFeaturesPrimary"
                class="w-full flex items-center justify-between p-3 rounded-lg text-xs font-bold transition-all outline-none cursor-pointer"
                :class="activePrimary === 'features' ? 'bg-brand-paper border-l-4 border-brand-primary text-brand-primary' : 'text-brand-ink/70 hover:bg-brand-paper hover:text-brand-ink-strong'"
              >
                <div class="flex items-center gap-2.5">
                  <Sliders :size="15" />
                  <span>4. 功能管理</span>
                </div>
                <span class="text-[9px] font-mono select-none text-brand-secondary">{{ isFeaturesMenuOpen ? '▼' : '▶' }}</span>
              </button>

              <div v-show="isFeaturesMenuOpen" class="pl-3.5 pr-1 py-1 space-y-1 block ml-4 border-l border-gray-100">
                <button
                  v-for="(item, index) in featureNavItems"
                  :key="item.key"
                  @click="selectFeature(item.key)"
                  class="w-full flex items-center justify-between px-2 py-1.5 rounded-md text-[10.5px] font-semibold transition-all outline-none cursor-pointer"
                  :class="activePrimary === 'features' && activeFeature === item.key ? 'bg-brand-paper/80 text-brand-primary font-bold' : 'text-brand-ink/60 hover:text-brand-ink-strong hover:bg-brand-paper/30'"
                >
                  <div class="flex items-center gap-2">
                    <component :is="featureNavIcons[item.key]" :size="13" />
                    <span>4.{{ index + 1 }} {{ item.label }}</span>
                  </div>
                </button>
              </div>
            </div>

            <div class="block">
              <button
                @click="togglePromotionPrimary"
                class="w-full flex items-center justify-between p-3 rounded-lg text-xs font-bold transition-all outline-none cursor-pointer"
                :class="activePrimary === 'promotion' ? 'bg-brand-paper border-l-4 border-brand-primary text-brand-primary' : 'text-brand-ink/70 hover:bg-brand-paper hover:text-brand-ink-strong'"
              >
                <div class="flex items-center gap-2.5">
                  <Award :size="15" />
                  <span>5. 推广合作</span>
                </div>
                <span class="text-[9px] font-mono select-none text-brand-secondary">{{ isPromoMenuOpen ? '▼' : '▶' }}</span>
              </button>

              <div v-show="isPromoMenuOpen" class="pl-3.5 pr-1 py-1 space-y-1 block ml-4 border-l border-gray-100">
                <button
                  v-for="(item, index) in promotionNavItems"
                  :key="item.key"
                  @click="selectPromotion(item.key)"
                  class="w-full flex items-center justify-between px-2 py-1.5 rounded-md text-[10.5px] font-semibold transition-all outline-none cursor-pointer"
                  :class="activePrimary === 'promotion' && activePromotion === item.key ? 'bg-brand-paper/80 text-brand-primary font-bold' : 'text-brand-ink/60 hover:text-brand-ink-strong hover:bg-brand-paper/30'"
                >
                  <div class="flex items-center gap-2">
                    <component :is="promotionNavIcons[item.key]" :size="13" />
                    <span>5.{{ index + 1 }} {{ item.label }}</span>
                  </div>
                </button>
              </div>
            </div>

            <button
              v-if="settingsNavItem"
              @click="switchPrimary('settings')"
              class="w-full flex items-center justify-between p-3 rounded-lg text-xs font-bold transition-all outline-none cursor-pointer"
              :class="activePrimary === 'settings' ? 'bg-brand-primary text-white shadow-md shadow-brand-primary/15' : 'text-brand-ink/70 hover:bg-brand-paper hover:text-brand-ink-strong'"
            >
              <div class="flex items-center gap-2.5">
                <Settings :size="15" />
                <span>6. {{ settingsNavItem.label }}</span>
              </div>
            </button>
          </nav>
        </div>

        <div class="p-4 border-t border-gray-100 space-y-3 font-sans">
          <div class="bg-brand-paper p-3 rounded-xl border border-gray-100 text-[10px] space-y-1 block">
            <div class="flex items-center gap-1.5 text-brand-ink/80">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse shrink-0"></span>
              <span class="font-bold">安全管理模式生效中</span>
            </div>
            <p class="text-brand-secondary truncate font-mono" title="Operator ID: auth_internal_admin">ADMIN_RFZ_V1_2026</p>
          </div>

          <div class="flex gap-1.5">
            <button
              @click="goToFrontend"
              class="flex-1 py-2 bg-brand-paper hover:bg-gray-100 text-brand-ink-strong text-[11px] font-bold rounded-lg transition-all outline-none cursor-pointer text-center border border-gray-100"
            >
              运行前端
            </button>
            <button
              @click="logout"
              class="py-2 px-2.5 bg-red-50 hover:bg-red-100 text-red-600 rounded-lg transition-all outline-none cursor-pointer border border-red-100"
              title="登出中枢"
            >
              <LogOut :size="14" />
            </button>
          </div>
        </div>
      </aside>

      <main class="flex-1 flex flex-col bg-brand-paper min-h-screen relative overflow-y-auto">
        <header class="p-6 border-b border-gray-100 flex items-center justify-between sticky top-0 bg-brand-paper/85 backdrop-blur-md z-45">
          <div class="space-y-0.5 block">
            <div class="text-[10.5px] font-mono text-brand-secondary flex items-center gap-1.5 uppercase font-bold">
              <span>EaseWise Admin</span>
              <span>/</span>
              <span class="text-brand-primary">{{ activeCode }}</span>
            </div>
            <h2 class="text-base font-serif font-bold text-brand-ink-strong tracking-wide">{{ activeHeaderTitle }}</h2>
          </div>

          <div class="flex items-center gap-2">
            <div class="text-xs bg-white border border-gray-100 px-4 py-2.5 rounded-xl font-mono text-brand-secondary shadow-sm">
              当前时区: <span class="text-brand-primary font-bold">UTC+8 (自然日)</span>
            </div>
            <div v-if="globalMessage" class="text-xs bg-white border border-red-100 px-4 py-2.5 rounded-xl font-mono text-red-600 shadow-sm max-w-[360px] truncate">
              {{ globalMessage }}
            </div>
          </div>
        </header>

        <div class="p-6 w-full max-w-none space-y-6">
          <div v-if="activePrimary === 'dashboard'" class="space-y-6">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 xl:gap-5 2xl:gap-6 items-stretch auto-rows-fr">
              <div class="bg-white/95 border border-[#E2E8F0]/80 rounded-2xl p-5 2xl:p-6 shadow-[0_12px_36px_rgba(15,23,42,0.045)] flex flex-col justify-between hover:shadow-[0_16px_44px_rgba(15,23,42,0.065)] transition-all text-left min-h-[330px]">
                <div>
                  <div class="flex items-center justify-between gap-3 mb-4 min-h-7">
                    <h3 class="font-bold text-xs text-brand-secondary font-mono tracking-wider uppercase flex items-center gap-1.5">
                      <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
                      <span>左上角 · 收益数据审计中心</span>
                    </h3>
                    <span class="text-[10px] bg-emerald-50 text-emerald-600 px-2.5 py-1 rounded-full font-bold font-mono">已支付订单流</span>
                  </div>

                  <div class="grid grid-cols-2 sm:grid-cols-3 gap-2.5 xl:gap-3">
                    <div
                      v-for="item in revenueCards"
                      :key="item.label"
                      class="p-3.5 rounded-xl border flex flex-col justify-between min-h-[78px]"
                      :class="item.featured ? 'bg-emerald-50/25 border-emerald-500/10' : 'bg-slate-50/50 border-gray-100'"
                    >
                      <span class="text-[10.5px] font-medium block" :class="item.featured ? 'text-emerald-700 font-bold' : 'text-brand-secondary'">{{ item.label }}</span>
                      <div class="text-[18px] font-black font-mono mt-1" :class="item.tone">￥{{ item.value }}</div>
                    </div>
                  </div>
                </div>

                <div class="mt-5 border-t border-gray-100 pt-4 block">
                  <div class="flex items-center justify-between text-[11px] text-brand-secondary font-bold mb-2">
                    <span>系统最新支付单溯源</span>
                    <button class="text-brand-primary cursor-pointer hover:underline outline-none" @click="switchPrimary('orders')">全部流水 →</button>
                  </div>
                  <div class="space-y-1.5 font-mono text-[10.5px]">
                    <div
                      v-for="order in latestPaidOrders"
                      :key="order.order_id"
                      class="flex justify-between items-center bg-gray-50/60 hover:bg-gray-50 px-2.5 py-1.5 rounded-lg border border-gray-100"
                    >
                      <span class="text-brand-ink/80">{{ order.user_nickname || order.user_id }} ({{ order.channel || '未知渠道' }})</span>
                      <span class="text-emerald-600 font-bold">{{ formatAmount(order.amount_cents) }}</span>
                    </div>
                    <div v-if="latestPaidOrders.length === 0" class="text-center text-gray-400 py-1">暂无交易数据</div>
                  </div>
                </div>
              </div>

              <div class="bg-white/95 border border-[#E2E8F0]/80 rounded-2xl p-5 2xl:p-6 shadow-[0_12px_36px_rgba(15,23,42,0.045)] flex flex-col justify-between hover:shadow-[0_16px_44px_rgba(15,23,42,0.065)] transition-all text-left min-h-[330px]">
                <div>
                  <div class="flex items-center justify-between gap-3 mb-4 min-h-7">
                    <h3 class="font-bold text-xs text-brand-secondary font-mono tracking-wider uppercase flex items-center gap-1.5">
                      <span class="w-2.5 h-2.5 rounded-full bg-blue-500 animate-pulse"></span>
                      <span>区域二 · 用户状态与功能调用</span>
                    </h3>
                    <div class="flex items-center gap-1.5 bg-blue-50 text-blue-600 px-2.5 py-1 rounded-full text-[10px] font-bold">
                      <span>总注册数:</span>
                      <span class="font-mono">{{ userOverviewCards[0].value }}</span>
                    </div>
                  </div>

                  <div class="grid grid-cols-2 md:grid-cols-3 2xl:grid-cols-7 gap-2.5 xl:gap-3 mb-4">
                    <div
                      v-for="item in userOverviewCards"
                      :key="item.label"
                      class="bg-blue-50/30 p-3 rounded-xl border border-blue-100 min-h-[78px]"
                    >
                      <span class="text-[10px] text-brand-secondary block font-medium">{{ item.label }}</span>
                      <div class="text-xl font-bold text-brand-ink-strong font-mono mt-0.5">{{ item.value }} 人</div>
                      <span class="text-[9.5px] text-brand-secondary font-mono">{{ item.sub }}</span>
                    </div>
                  </div>

                  <div class="space-y-2.5">
                    <div class="flex flex-wrap items-center justify-between gap-2">
                      <span class="text-[11px] text-brand-secondary font-bold block">功能使用情况 (按周期 Top 5)</span>
                      <span class="text-[10px] text-brand-secondary font-mono">频次 / 周期内占比</span>
                    </div>
                    <div class="grid grid-cols-1 sm:grid-cols-2 2xl:grid-cols-4 gap-2 text-[11px] font-mono">
                      <div
                        v-for="item in featureUsageWindowCards"
                        :key="item.key"
                        class="bg-white border border-gray-100 rounded-xl p-2.5 min-h-[168px]"
                      >
                        <div class="flex items-start justify-between gap-2 border-b border-gray-100 pb-2 mb-2">
                          <div>
                            <span class="text-[10px] text-brand-secondary block">{{ item.label }}</span>
                            <span class="block text-[9px] text-brand-secondary">{{ item.sub }}</span>
                          </div>
                          <b class="text-base text-brand-ink-strong whitespace-nowrap">{{ item.total }} 次</b>
                        </div>
                        <div v-if="item.items.length" class="space-y-1.5">
                          <div
                            v-for="(feat, index) in item.items"
                            :key="`${item.key}-${feat.name}`"
                            class="space-y-1"
                          >
                            <div class="grid grid-cols-[minmax(0,1fr)_34px_40px] items-center gap-1.5">
                              <span class="text-brand-ink-strong truncate">#{{ index + 1 }} {{ feat.name }}</span>
                              <span class="text-right text-brand-primary font-bold">{{ feat.count }}次</span>
                              <span class="text-right text-blue-700 font-bold">{{ feat.percentage }}%</span>
                            </div>
                            <div class="w-full bg-blue-50 h-1.5 rounded-full overflow-hidden">
                              <div
                                class="bg-gradient-to-r from-blue-500 to-brand-primary h-full rounded-full transition-all"
                                :style="{width: `${Math.max(feat.percentage, feat.count > 0 ? 4 : 0)}%`}"
                              ></div>
                            </div>
                          </div>
                        </div>
                        <div v-else class="h-[96px] flex items-center justify-center text-[10px] text-brand-secondary">
                          暂无功能使用记录
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="text-[10px] border-t border-gray-100 pt-3 mt-3 text-brand-secondary leading-relaxed font-mono">
                  用户活跃度数据前台自动沉淀，记录用户点击解卦服务与评测交互事件。
                </div>
              </div>

              <div class="bg-white/95 border border-[#E2E8F0]/80 rounded-2xl p-5 2xl:p-6 shadow-[0_12px_36px_rgba(15,23,42,0.045)] flex flex-col justify-between hover:shadow-[0_16px_44px_rgba(15,23,42,0.065)] transition-all text-left min-h-[330px]">
                <div>
                  <div class="flex items-center justify-between gap-3 mb-4 min-h-7">
                    <h3 class="font-bold text-xs text-brand-secondary font-mono tracking-wider uppercase flex items-center gap-1.5">
                      <span class="w-2.5 h-2.5 rounded-full bg-amber-500 animate-pulse"></span>
                      <span>左下方 · 充值订单订单统计流</span>
                    </h3>
                    <span class="text-[10px] bg-amber-50 text-amber-700 px-2.5 py-1 rounded-full font-bold font-mono">总交易单: {{ orderCards[5].value }} 笔</span>
                  </div>

                  <div class="grid grid-cols-2 sm:grid-cols-3 gap-2.5 xl:gap-3">
                    <div
                      v-for="item in orderCards"
                      :key="item.label"
                      class="p-3.5 rounded-xl border transition-colors min-h-[88px]"
                      :class="item.featured ? 'bg-amber-500/5 border-amber-500/10' : 'bg-slate-50/50 border-gray-100'"
                    >
                      <span class="text-[10.5px] font-medium block" :class="item.featured ? 'text-amber-700 font-bold' : 'text-brand-secondary'">{{ item.label }}</span>
                      <div class="text-[20px] font-bold font-mono mt-1" :class="item.tone">{{ item.value }} 笔</div>
                      <span class="text-[9px] text-brand-secondary font-mono">{{ item.sub }}</span>
                    </div>
                  </div>
                </div>

                <div class="mt-4 border-t border-gray-100 pt-3 flex justify-between items-center text-[10.5px] font-mono text-brand-secondary">
                  <span>订单数据按后台流水实时刷新，包含未支付、已支付与退款纠纷状态。</span>
                  <button @click="switchPrimary('orders')" class="text-brand-primary font-bold hover:underline outline-none">前去订单管理 →</button>
                </div>
              </div>

              <div class="bg-white/95 border border-[#E2E8F0]/80 rounded-2xl p-5 2xl:p-6 shadow-[0_12px_36px_rgba(15,23,42,0.045)] flex flex-col justify-between hover:shadow-[0_16px_44px_rgba(15,23,42,0.065)] transition-all text-left min-h-[330px]">
                <div>
                  <div class="flex items-center justify-between gap-3 mb-4 min-h-7">
                    <h3 class="font-bold text-xs text-brand-secondary font-mono tracking-wider uppercase flex items-center gap-1.5">
                      <span class="w-2.5 h-2.5 rounded-full bg-violet-500 animate-pulse"></span>
                      <span>右下角 · 推广合作与分销体系</span>
                    </h3>
                    <span class="text-[10px] bg-violet-50 text-violet-600 px-2.5 py-1 rounded-full font-bold font-mono">合伙联运体系</span>
                  </div>

                  <div class="grid grid-cols-2 gap-2.5 xl:gap-3 mb-4">
                    <div v-for="item in promoCards" :key="item.label" class="bg-indigo-50/30 p-3.5 rounded-xl border border-gray-100 relative min-h-[92px]">
                      <span class="text-[10.5px] text-indigo-800 font-bold block">{{ item.label }}</span>
                      <div class="text-xl font-bold text-indigo-700 font-mono mt-1">{{ item.value }} 名</div>
                      <span class="text-[9px] text-brand-secondary font-mono">{{ item.sub }}</span>
                    </div>
                  </div>

                  <div class="bg-violet-50/30 border border-violet-100 hover:border-violet-300 p-4 rounded-xl space-y-2 transition-colors">
                    <span class="text-[11px] text-brand-primary-strong font-bold block">资金提现结算中心</span>
                    <div class="grid grid-cols-2 gap-2">
                      <div class="bg-white/80 p-2.5 rounded-lg border border-violet-50 flex flex-col justify-center">
                        <span class="text-[10px] text-brand-secondary">提现申请的数量</span>
                        <span class="text-base font-bold text-brand-ink-strong font-mono mt-0.5">0 笔</span>
                      </div>
                      <div class="bg-white/80 p-2.5 rounded-lg border border-violet-50 flex flex-col justify-center">
                        <span class="text-[10px] text-brand-secondary">待提现申请笔数</span>
                        <span class="text-base font-bold text-red-600 font-mono mt-0.5">0 笔待提</span>
                      </div>
                    </div>

                    <div class="flex items-center justify-between text-xs font-semibold pt-1 text-slate-700/80">
                      <span>待提现的金额 (待审核款额):</span>
                      <span class="text-emerald-600 font-black font-mono font-bold">￥0.00 元</span>
                    </div>
                  </div>
                </div>

                <div class="mt-4 border-t border-gray-100 pt-3 flex justify-between items-center text-[10.5px] font-mono text-brand-secondary">
                  <span>推广提现通过后台大使面板进行自动打款或线下财务结算归集。</span>
                  <button @click="selectPromotion('withdrawals')" class="text-brand-primary font-bold hover:underline outline-none">审核打款 →</button>
                </div>
              </div>
            </div>

            <div class="bg-brand-primary/5 border border-brand-primary/25 rounded-2xl p-5 flex items-center justify-between text-left">
              <div class="space-y-1 block">
                <h4 class="font-serif text-[15px] font-bold text-brand-primary-strong inline-flex items-center gap-1.5">
                  <AlertTriangle :size="16" />
                  <span>管理控制待办清单</span>
                </h4>
                <p class="text-[11.5px] text-brand-ink/90">
                  大盘保留收益、订单、用户与推广合作的统一运营视图；推广审核、提现和返佣记录在左侧推广合作子系统中继续处理。
                </p>
              </div>

              <div class="flex gap-2">
                <button
                  @click="switchPrimary('orders')"
                  class="bg-brand-primary text-white font-bold px-4 py-2 rounded-xl text-xs hover:bg-brand-primary-strong transition-colors select-none cursor-pointer outline-none shadow-sm shadow-brand-primary/10"
                >
                  去处理充值订单
                </button>
                <button
                  @click="selectPromotion('withdrawals')"
                  class="bg-white border border-gray-100 text-brand-primary font-bold px-4 py-2 rounded-xl text-xs hover:bg-gray-50 transition-colors select-none cursor-pointer outline-none shadow-sm"
                >
                  去审计分账提现
                </button>
              </div>
            </div>
          </div>

          <div v-else-if="activePrimary === 'orders'" class="space-y-4 text-left">
            <div class="bg-white border border-gray-100 rounded-2xl p-5 space-y-4 shadow-sm">
              <div
                v-if="activeOrderReturnContext"
                class="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-brand-primary/10 bg-brand-primary/5 px-4 py-3 text-xs"
              >
                <div class="min-w-0">
                  <p class="font-bold text-brand-ink-strong">正在查看用户「{{ activeOrderReturnContext.userLabel }}」的订单</p>
                  <p class="font-mono text-[10px] text-brand-secondary truncate">{{ activeOrderReturnContext.userId }}</p>
                </div>
                <div class="flex items-center gap-2">
                  <button @click="returnToUserFile" class="bg-brand-primary text-white px-3 py-1.5 rounded-lg text-[10.5px] font-bold shadow-sm shadow-brand-primary/10">
                    返回用户档案
                  </button>
                  <button @click="clearOrderUserScope" class="bg-white border border-gray-100 text-brand-secondary px-3 py-1.5 rounded-lg text-[10.5px] font-bold">
                    清除筛选
                  </button>
                </div>
              </div>

              <div class="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-gray-100">
                <div class="flex flex-wrap items-center gap-3">
                  <div class="relative w-72">
                    <Search class="absolute left-3 top-2.5 text-brand-secondary" :size="14" />
                    <input
                      v-model="orderSearchText"
                      placeholder="检索订单ID、用户ID、昵称或外部单号..."
                      class="w-full bg-gray-50 border border-gray-100 p-2.5 pl-9 rounded-xl text-xs text-brand-ink-strong placeholder-brand-secondary focus:border-brand-primary focus:bg-white outline-none"
                    />
                  </div>

                  <AdminSelect
                    v-model="orderFilters.status"
                    :options="orderStatusSelectOptions"
                    panel-width-class="w-56"
                  />

                  <input
                    v-model="orderFilters.channel"
                    placeholder="渠道"
                    class="bg-gray-50 border border-gray-100 text-brand-ink p-2.5 rounded-xl text-xs focus:border-brand-primary outline-none"
                  />
                </div>

                <button
                  @click="loadOrders"
                  class="bg-brand-primary text-white px-4 py-2 rounded-xl text-xs font-bold font-sans hover:bg-brand-primary-strong transition-colors cursor-pointer select-none outline-none inline-flex items-center gap-1.5 shadow-sm shadow-brand-primary/10"
                >
                  {{ orderLoading ? '查询中...' : '查询订单' }}
                </button>
              </div>

              <div v-if="orderError" class="text-xs text-red-600 bg-red-50 border border-red-100 rounded-xl px-3 py-2">
                {{ orderError }}
              </div>

              <div class="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-3">
                <div v-for="item in orderCards" :key="item.label" class="bg-brand-paper/70 border border-gray-100 rounded-xl p-3">
                  <div class="text-[10px] text-brand-secondary">{{ item.label }}</div>
                  <div class="text-lg font-bold font-mono text-brand-ink-strong mt-1">{{ item.value }}</div>
                  <div class="text-[10px] text-brand-secondary">{{ item.sub }}</div>
                </div>
              </div>

              <div class="overflow-x-auto">
                <table class="w-full text-xs font-sans text-left">
                  <thead>
                    <tr class="text-brand-secondary border-b border-gray-100 uppercase font-mono text-[10.5px]">
                      <th class="p-3">订单ID</th>
                      <th class="p-3">购买用户</th>
                      <th class="p-3">套餐</th>
                      <th class="p-3 text-right">金额</th>
                      <th class="p-3">状态</th>
                      <th class="p-3">渠道</th>
                      <th class="p-3">创建时间</th>
                      <th class="p-3 text-right">操作</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-100">
                    <tr v-for="order in visibleOrders" :key="order.order_id" class="hover:bg-brand-paper/50 transition-colors">
                      <td class="p-3 font-mono text-brand-ink-strong select-all">{{ order.order_id }}</td>
                      <td class="p-3 font-semibold text-brand-ink-strong">
                        <div>{{ order.user_nickname || order.user_id }}</div>
                        <div class="text-[10px] text-brand-secondary font-mono">{{ order.user_id }}</div>
                      </td>
                      <td class="p-3 text-brand-ink">{{ order.package_title }}</td>
                      <td class="p-3 text-right text-emerald-600 font-bold font-mono">{{ formatAmount(order.amount_cents) }}</td>
                      <td class="p-3">
                        <span class="px-2 py-0.5 rounded-full text-[9px] font-bold tracking-wider inline-block border" :class="orderStatusClass(order.status)">
                          {{ orderStatusLabel(order.status) }}
                        </span>
                      </td>
                      <td class="p-3 text-brand-secondary font-mono">{{ order.channel || '--' }}</td>
                      <td class="p-3 text-brand-secondary font-mono">{{ formatTime(order.created_at) }}</td>
                      <td class="p-3 text-right">
                        <button @click="openOrderDetail(order)" class="px-2 py-1 text-brand-primary hover:underline text-[10.5px] cursor-pointer">查看详情</button>
                      </td>
                    </tr>
                    <tr v-if="!orderLoading && visibleOrders.length === 0">
                      <td colspan="8" class="p-8 text-center text-brand-secondary font-mono">暂无订单数据</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <div v-else-if="activePrimary === 'users'" class="space-y-4 text-left">
            <div class="bg-white border border-gray-100 rounded-2xl p-5 space-y-4 shadow-sm">
              <div class="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-gray-100">
                <div class="flex flex-wrap items-center gap-3">
                  <div class="relative w-80">
                    <Search class="absolute left-3 top-2.5 text-brand-secondary" :size="14" />
                    <input
                      v-model="userQuery"
                      placeholder="按用户ID、昵称、手机号、UnionID 或 guest key 检索..."
                      @keyup.enter="loadUsers"
                      class="w-full bg-gray-50 border border-gray-100 p-2.5 pl-9 rounded-xl text-xs text-brand-ink-strong placeholder-brand-secondary focus:border-brand-primary focus:bg-white outline-none"
                    />
                  </div>
                  <AdminSelect
                    v-model="userFilters.status"
                    :options="userStatusSelectOptions"
                    panel-width-class="w-44"
                  />
                  <AdminSelect
                    v-model="userFilters.identity_level"
                    :options="userIdentitySelectOptions"
                    min-width-class="min-w-[150px]"
                    panel-width-class="w-52"
                  />
                  <input v-model="userFilters.channel" placeholder="渠道" class="bg-gray-50 border border-gray-100 text-brand-ink p-2.5 rounded-xl text-xs focus:border-brand-primary outline-none w-28" />
                </div>
                <div class="flex gap-2">
                  <button @click="resetUserFilters(); loadUsers()" class="bg-white border border-gray-100 text-brand-secondary px-4 py-2 rounded-xl text-xs font-bold hover:bg-gray-50 transition-colors outline-none cursor-pointer">
                    重置
                  </button>
                  <button @click="loadUsers" class="bg-brand-primary text-white px-4 py-2 rounded-xl text-xs font-bold hover:bg-brand-primary-strong transition-colors outline-none cursor-pointer">
                    {{ userLoading ? '搜索中...' : '搜索用户' }}
                  </button>
                </div>
              </div>

              <div v-if="userError" class="text-xs text-red-600 bg-red-50 border border-red-100 rounded-xl px-3 py-2">
                {{ userError }}
              </div>

              <div class="overflow-x-auto">
                <table class="w-full table-fixed text-xs font-sans text-left">
                  <thead>
                    <tr class="text-brand-secondary border-b border-gray-100 uppercase font-mono text-[10.5px]">
                      <th class="p-3 w-[14%]">用户昵称</th>
                      <th class="p-3 w-[15%] font-mono">用户ID / 状态</th>
                      <th class="p-3 w-[7%]">积分</th>
                      <th class="p-3 w-[10%]">可提现余额</th>
                      <th class="p-3 w-[10%]">冻结返佣</th>
                      <th class="p-3 w-[9%]">身份</th>
                      <th class="p-3 w-[12%]">主身份</th>
                      <th class="p-3 w-[9%]">注册时间</th>
                      <th class="p-3 w-[9%]">最近活跃</th>
                      <th class="p-3 w-[9%] text-right">后台档案</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-100">
                    <tr v-for="user in visibleUsers" :key="user.user_id" class="hover:bg-brand-paper/50 transition-colors">
                      <td class="p-3">
                        <div class="flex items-center gap-2 min-w-0">
                          <span class="w-7 h-7 shrink-0 bg-brand-primary/10 text-brand-primary font-serif font-bold flex items-center justify-center rounded-lg text-xs">
                            {{ (user.nickname || user.user_id).substring(0, 1) }}
                          </span>
                          <div class="min-w-0">
                            <div class="font-bold text-brand-ink-strong truncate">{{ user.nickname || '未命名用户' }}</div>
                            <div class="text-[10px] text-brand-secondary font-mono truncate">{{ user.registered_channel || '--' }}</div>
                          </div>
                        </div>
                      </td>
                      <td class="p-3 font-mono min-w-0">
                        <span class="text-brand-secondary block truncate" :title="user.user_id">{{ shortText(user.user_id, 10, 6) }}</span>
                        <span :class="user.status === 'active' ? 'text-emerald-600' : 'text-red-600'" class="text-[9.5px]/none font-bold block mt-1">
                          ● {{ userStatusLabel(user.status) }}
                        </span>
                      </td>
                      <td class="p-3 font-mono text-brand-primary font-bold text-sm">{{ user.points_balance }} pt</td>
                      <td class="p-3 font-mono text-emerald-600 font-bold text-sm">{{ formatAmount(user.withdrawable_balance_cents) }}</td>
                      <td class="p-3 font-mono text-amber-600 font-bold text-sm">{{ formatAmount(user.frozen_commission_cents) }}</td>
                      <td class="p-3 text-brand-secondary">{{ identityLabel(user.identity_level) }}</td>
                      <td class="p-3 text-brand-secondary min-w-0">
                        <div class="font-semibold text-brand-ink-strong">{{ identitySourceLabel(user.primary_identity_type) }}</div>
                        <div class="font-mono text-[10px] truncate" :title="userPrimaryIdentityLine(user)">{{ shortText(userPrimaryIdentityLine(user), 8, 4) }}</div>
                      </td>
                      <td class="p-3 text-brand-secondary font-mono">{{ formatTime(user.registered_at || user.created_at) }}</td>
                      <td class="p-3 text-brand-secondary font-mono">{{ formatTime(user.last_active_at) }}</td>
                      <td class="p-3 text-right">
                        <button
                          @click="openUserSummary(user.user_id)"
                          class="px-2.5 py-1.5 bg-brand-paper hover:bg-gray-100 text-brand-ink-strong text-xs font-bold rounded-lg cursor-pointer outline-none transition-colors border border-gray-100 shadow-xs"
                        >
                          调整及追踪档案
                        </button>
                      </td>
                    </tr>
                    <tr v-if="visibleUsers.length === 0">
                      <td colspan="10" class="p-8 text-center text-brand-secondary font-mono">暂无用户数据</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <div v-else-if="activePrimary === 'features' && activeFeature === 'almanac'" class="space-y-6 text-left animate-fade-in">
            <div class="bg-white border border-gray-100 rounded-2xl p-6 space-y-6 shadow-sm min-h-[420px]">
              <div class="flex justify-between items-center pb-4 border-b border-gray-100">
                <div class="space-y-0.5 block">
                  <h3 class="font-serif text-lg font-bold text-brand-primary flex items-center gap-2">
                    <Calendar :size="20" />
                    <span>黄历相关设置</span>
                  </h3>
                  <p class="text-xs text-brand-secondary">该页面按当前计划先留白作为占位，后续接入黄历配置任务。</p>
                </div>
              </div>
              <div class="h-72 rounded-2xl border border-dashed border-gray-200 bg-gray-50/50 flex items-center justify-center text-xs text-brand-secondary font-mono">
                黄历配置占位区 · 待后续开发
              </div>
            </div>
          </div>

          <div v-else-if="activePrimary === 'features'" class="space-y-6 text-left animate-fade-in">
            <div class="bg-white border border-gray-100 rounded-2xl p-6 space-y-6 shadow-sm">
              <div class="flex justify-between items-center pb-4 border-b border-gray-100">
                <div class="space-y-0.5 block">
                  <h3 class="font-serif text-lg font-bold text-brand-primary flex items-center gap-2">
                    <Smartphone :size="20" />
                    <span>手算五行 · 手机号数字测算规则策略</span>
                  </h3>
                  <p class="text-xs text-brand-secondary">设定手机号评测积分规则、维度解锁策略，并查看统一功能使用记录。</p>
                </div>
                <button
                  @click="loadUsageRecords"
                  class="bg-brand-primary hover:bg-brand-primary-strong text-white px-5 py-2 rounded-xl text-xs font-bold transition-all outline-none cursor-pointer shadow-sm shadow-brand-primary/10 flex items-center gap-1.5"
                >
                  {{ usageLoading ? '查询中...' : '查询使用记录' }}
                </button>
              </div>

              <div class="bg-red-50/20 p-5 rounded-2xl border border-red-100 space-y-4">
                <div class="flex items-start justify-between">
                  <div class="space-y-1 block">
                    <span class="text-xs bg-red-100/80 text-red-700 font-mono px-2 py-0.5 rounded border border-red-200 mr-1.5 uppercase font-bold">STAGE LAYER 1: GLOBAL COMPLIANCE</span>
                    <h4 class="font-serif text-base font-bold text-brand-ink-strong inline-block">渠道总开关与单功能开关配置区</h4>
                    <p class="text-[11.5px] text-brand-secondary leading-relaxed max-w-4xl">
                      页面保留设计稿的配置承载区。后续接入真实配置后，渠道总开关关闭时将同步隐藏玄学功能入口及历史使用记录。
                    </p>
                  </div>
                  <span class="text-[10px] bg-brand-paper border border-gray-100 text-brand-secondary px-2.5 py-1 rounded-full font-bold">待接入</span>
                </div>
              </div>

              <div class="bg-brand-paper/30 border border-gray-100 rounded-2xl p-5 space-y-4">
                <div class="flex items-center justify-between gap-3">
                  <div class="space-y-0.5">
                    <h4 class="font-serif text-base font-bold text-brand-ink-strong">功能管理配置</h4>
                    <p class="text-[11.5px] text-brand-secondary leading-relaxed">
                      这里承载功能开关、积分消耗、智能体玄学技能控制等后台配置，修改后会影响后续新记录。
                    </p>
                  </div>
                  <button
                    @click="saveRuntimeConfig"
                    class="bg-brand-primary hover:bg-brand-primary-strong text-white px-4 py-2 rounded-xl text-xs font-bold transition-all outline-none cursor-pointer shadow-sm shadow-brand-primary/10"
                  >
                    {{ runtimeConfigLoading ? '保存中...' : '保存功能配置' }}
                  </button>
                </div>

                <div v-if="featureConfigItems.length" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div v-for="item in featureConfigItems" :key="item.config_key" class="bg-white border border-gray-100 rounded-xl p-4 space-y-2">
                    <div class="flex items-center justify-between gap-2">
                      <div>
                        <div class="text-sm font-bold text-brand-ink-strong">{{ item.label }}</div>
                        <div class="text-[10px] text-brand-secondary font-mono">{{ item.config_key }}</div>
                      </div>
                      <span class="text-[10px] px-2 py-0.5 rounded-full border" :class="item.high_risk ? 'bg-red-50 text-red-600 border-red-100' : 'bg-emerald-50 text-emerald-600 border-emerald-100'">
                        {{ item.high_risk ? '高风险' : '常规' }}
                      </span>
                    </div>
                    <template v-if="item.value_type === 'bool'">
                      <AdminSelect
                        v-model="runtimeConfigDrafts[item.config_key]"
                        @change="runtimeConfigDirty = true"
                        :options="booleanToggleSelectOptions"
                        min-width-class="w-full"
                        panel-width-class="w-full"
                      />
                    </template>
                    <template v-else-if="item.value_type === 'json'">
                      <textarea
                        v-model="runtimeConfigDrafts[item.config_key]"
                        @input="runtimeConfigDirty = true"
                        class="w-full bg-gray-50 border border-gray-100 rounded-lg p-2 text-xs outline-none min-h-24 font-mono"
                      ></textarea>
                    </template>
                    <template v-else>
                      <input
                        v-model="runtimeConfigDrafts[item.config_key]"
                        @input="runtimeConfigDirty = true"
                        :type="item.value_type === 'int' || item.value_type === 'float' ? 'number' : 'text'"
                        class="w-full bg-gray-50 border border-gray-100 rounded-lg p-2 text-xs outline-none"
                      />
                    </template>
                    <div class="text-[11px] text-brand-secondary">默认值：{{ runtimeInputText(item) }}</div>
                  </div>
                </div>

                <div v-else class="h-32 rounded-xl border border-dashed border-gray-200 bg-white/70 flex items-center justify-center text-xs text-brand-secondary font-mono">
                  暂无功能管理配置项
                </div>
              </div>

              <div class="bg-gray-50/50 border border-gray-100 p-5 rounded-xl space-y-4 shadow-xs text-left">
                <div
                  v-if="activeUsageReturnContext"
                  class="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-brand-primary/10 bg-brand-primary/5 px-4 py-3 text-xs"
                >
                  <div class="min-w-0">
                    <p class="font-bold text-brand-ink-strong">正在查看用户「{{ activeUsageReturnContext.userLabel }}」的功能使用记录</p>
                    <p class="font-mono text-[10px] text-brand-secondary truncate">{{ activeUsageReturnContext.userId }}</p>
                  </div>
                  <div class="flex items-center gap-2">
                    <button @click="returnToUserFile" class="bg-brand-primary text-white px-3 py-1.5 rounded-lg text-[10.5px] font-bold shadow-sm shadow-brand-primary/10">
                      返回用户档案
                    </button>
                    <button @click="clearUsageUserScope" class="bg-white border border-gray-100 text-brand-secondary px-3 py-1.5 rounded-lg text-[10.5px] font-bold">
                      清除筛选
                    </button>
                  </div>
                </div>

                <div class="flex flex-wrap gap-3">
                  <input v-model="usageFilters.keyword" class="bg-white border border-gray-200 p-2.5 rounded-lg text-xs text-brand-ink-strong outline-none focus:border-brand-primary w-64" placeholder="用户 / 昵称 / 手机号 / 业务 ID" />
                  <AdminSelect
                    v-model="usageFilters.scene"
                    :options="usageSceneSelectOptions"
                    min-width-class="min-w-[160px]"
                    panel-width-class="w-56"
                  />
                  <input v-model="usageFilters.channel" class="bg-white border border-gray-200 p-2.5 rounded-lg text-xs text-brand-ink-strong outline-none focus:border-brand-primary" placeholder="渠道" />
                  <input v-model="usageFilters.status" class="bg-white border border-gray-200 p-2.5 rounded-lg text-xs text-brand-ink-strong outline-none focus:border-brand-primary" placeholder="状态" />
                </div>

                <div v-if="usageError" class="text-xs text-red-600 bg-red-50 border border-red-100 rounded-xl px-3 py-2">
                  {{ usageError }}
                </div>

                <div class="overflow-x-auto border border-gray-100 rounded-xl bg-white">
                  <table class="w-full text-xs font-sans text-left">
                    <thead>
                      <tr class="bg-gray-50 border-b border-gray-100 text-brand-secondary uppercase font-mono text-[10px] tracking-wider">
                        <th class="p-3">记录ID</th>
                        <th class="p-3">功能名称</th>
                        <th class="p-3">用户标识</th>
                        <th class="p-3">渠道</th>
                        <th class="p-3">状态</th>
                        <th class="p-3 text-right">消耗积分</th>
                        <th class="p-3">业务ID</th>
                        <th class="p-3 text-right">操作</th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100 font-medium">
                      <tr v-for="record in usageRecords" :key="record.usage_record_id" class="hover:bg-brand-paper/50">
                        <td class="p-3 font-mono text-brand-ink-strong select-all">{{ record.usage_record_id }}</td>
                        <td class="p-3 font-bold text-brand-ink-strong">{{ record.feature_name || record.feature_key }}</td>
                        <td class="p-3 text-brand-secondary">{{ record.user_nickname || record.user_phone || record.user_id }}</td>
                        <td class="p-3 font-mono text-brand-secondary">{{ record.channel || '--' }}</td>
                        <td class="p-3"><span class="px-2 py-0.5 rounded text-[9px] font-bold inline-block border" :class="usageStatusClass(record.status)">{{ record.status }}</span></td>
                        <td class="p-3 text-right font-mono text-brand-primary font-bold">{{ record.normal_points_cost }}</td>
                        <td class="p-3 font-mono text-brand-secondary">{{ record.target_id || '--' }}</td>
                        <td class="p-3 text-right">
                          <button @click="openUsageDetail(record)" class="text-brand-primary font-bold hover:underline outline-none cursor-pointer">详情</button>
                        </td>
                      </tr>
                      <tr v-if="!usageLoading && usageRecords.length === 0">
                        <td colspan="8" class="p-8 text-center text-brand-secondary font-mono">暂无使用记录</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>

          <div v-else-if="activePrimary === 'promotion' && activePromotion === 'review'" class="space-y-6 text-left animate-fade-in">
            <div class="bg-white border border-gray-100 rounded-2xl p-6 space-y-6 shadow-sm min-h-[420px]">
              <div class="flex justify-between items-center pb-3 border-b border-gray-100">
                <div class="space-y-0.5">
                  <h3 class="font-bold text-brand-ink-strong text-base flex items-center gap-1.5 text-brand-primary">
                    <Award :size="16" />
                    <span>推广审核</span>
                  </h3>
                  <p class="text-xs text-brand-secondary">审核用户申请成为推广大使或高级推广大使。</p>
                </div>
              </div>
              <div v-if="promotionApplicationError" class="text-xs text-red-600 bg-red-50 border border-red-100 rounded-xl px-3 py-2">
                {{ promotionApplicationError }}
              </div>
              <div class="border border-gray-100 rounded-xl overflow-hidden bg-white">
                <table class="w-full text-xs font-sans text-left">
                  <thead>
                    <tr class="bg-gray-50 border-b border-gray-100 text-brand-secondary uppercase font-mono text-[10px] tracking-wider">
                      <th class="p-3">业务编号</th>
                      <th class="p-3">申请用户</th>
                      <th class="p-3">申请等级</th>
                      <th class="p-3">状态</th>
                      <th class="p-3">提交时间</th>
                      <th class="p-3 text-right">执行动作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in promotionApplications" :key="item.application_id" class="hover:bg-brand-paper/50">
                      <td class="p-3 font-mono text-brand-ink-strong">{{ item.application_id }}</td>
                      <td class="p-3">{{ item.user_nickname || item.user_id }}</td>
                      <td class="p-3 text-brand-secondary">{{ identityLabel(item.requested_level) }}</td>
                      <td class="p-3"><span class="px-2 py-0.5 rounded text-[9px] font-bold inline-block border" :class="promotionStatusClass(item.status)">{{ promotionStatusLabel(item.status) }}</span></td>
                      <td class="p-3 font-mono text-brand-secondary">{{ formatTime(item.created_at) }}</td>
                      <td class="p-3 text-right">
                        <button @click="openPromotionApplication(item.application_id)" class="text-brand-primary font-bold hover:underline text-[10.5px] cursor-pointer">查看详情</button>
                      </td>
                    </tr>
                    <tr v-if="!promotionApplicationLoading && promotionApplications.length === 0">
                      <td colspan="6" class="p-8 text-center text-brand-secondary font-mono">暂无推广申请</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <div v-else-if="activePrimary === 'promotion' && activePromotion === 'withdrawals'" class="space-y-6 text-left animate-fade-in">
            <div class="bg-white border border-gray-100 rounded-2xl p-6 space-y-6 shadow-sm min-h-[420px]">
              <div class="flex justify-between items-center pb-3 border-b border-gray-100">
                <div class="space-y-0.5">
                  <h3 class="font-bold text-brand-ink-strong text-base flex items-center gap-1.5 text-brand-primary">
                    <Coins :size="16" />
                    <span>提现申请审核</span>
                  </h3>
                  <p class="text-xs text-brand-secondary">可审核、重试打款和手动标记已打款。</p>
                </div>
              </div>
              <div v-if="promotionWithdrawalError" class="text-xs text-red-600 bg-red-50 border border-red-100 rounded-xl px-3 py-2">
                {{ promotionWithdrawalError }}
              </div>
              <div class="border border-gray-100 rounded-xl overflow-hidden bg-white">
                <table class="w-full text-xs font-sans text-left">
                  <thead>
                    <tr class="bg-gray-50 border-b border-gray-100 text-brand-secondary uppercase font-mono text-[10px] tracking-wider">
                      <th class="p-3">提现编号</th>
                      <th class="p-3">用户</th>
                      <th class="p-3">状态</th>
                      <th class="p-3">金额</th>
                      <th class="p-3">提交时间</th>
                      <th class="p-3 text-right">执行动作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in promotionWithdrawals" :key="item.withdrawal_id" class="hover:bg-brand-paper/50">
                      <td class="p-3 font-mono text-brand-ink-strong">{{ item.withdrawal_id }}</td>
                      <td class="p-3">{{ item.user_nickname || item.user_id }}</td>
                      <td class="p-3"><span class="px-2 py-0.5 rounded text-[9px] font-bold inline-block border" :class="promotionStatusClass(item.status)">{{ promotionStatusLabel(item.status) }}</span></td>
                      <td class="p-3 text-emerald-600 font-mono font-bold">{{ formatAmount(item.amount_cents) }}</td>
                      <td class="p-3 font-mono text-brand-secondary">{{ formatTime(item.created_at) }}</td>
                      <td class="p-3 text-right">
                        <button @click="openPromotionWithdrawal(item.withdrawal_id)" class="text-brand-primary font-bold hover:underline text-[10.5px] cursor-pointer">查看详情</button>
                      </td>
                    </tr>
                    <tr v-if="!promotionWithdrawalLoading && promotionWithdrawals.length === 0">
                      <td colspan="6" class="p-8 text-center text-brand-secondary font-mono">暂无提现申请</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <div v-else-if="activePrimary === 'promotion' && activePromotion === 'commissions'" class="space-y-6 text-left animate-fade-in">
            <div class="bg-white border border-gray-100 rounded-2xl p-6 space-y-6 shadow-sm min-h-[420px]">
              <div class="flex justify-between items-center pb-3 border-b border-gray-100">
                <div class="space-y-0.5">
                  <h3 class="font-bold text-brand-ink-strong text-base flex items-center gap-1.5 text-brand-primary">
                    <Search :size="16" />
                    <span>返佣记录</span>
                  </h3>
                  <p class="text-xs text-brand-secondary">用于追踪每笔返佣的产生、结算与撤回。</p>
                </div>
              </div>
              <div v-if="promotionCommissionError" class="text-xs text-red-600 bg-red-50 border border-red-100 rounded-xl px-3 py-2">
                {{ promotionCommissionError }}
              </div>
              <div class="border border-gray-100 rounded-xl overflow-hidden bg-white">
                <table class="w-full text-xs font-sans text-left">
                  <thead>
                    <tr class="bg-gray-50 border-b border-gray-100 text-brand-secondary uppercase font-mono text-[10px] tracking-wider">
                      <th class="p-3">佣金编号</th>
                      <th class="p-3">推广用户</th>
                      <th class="p-3">关联用户</th>
                      <th class="p-3">订单</th>
                      <th class="p-3">状态</th>
                      <th class="p-3 text-right">操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in promotionCommissions" :key="item.commission_id" class="hover:bg-brand-paper/50">
                      <td class="p-3 font-mono text-brand-ink-strong">{{ item.commission_id }}</td>
                      <td class="p-3">{{ item.promoter_nickname || item.promoter_user_id }}</td>
                      <td class="p-3">{{ item.invited_user_nickname || item.invited_user_id || '--' }}</td>
                      <td class="p-3 font-mono text-brand-secondary">{{ item.order_id || '--' }}</td>
                      <td class="p-3"><span class="px-2 py-0.5 rounded text-[9px] font-bold inline-block border" :class="promotionStatusClass(item.status)">{{ promotionStatusLabel(item.status) }}</span></td>
                      <td class="p-3 text-right">
                        <button @click="openPromotionCommission(item.commission_id)" class="text-brand-primary font-bold hover:underline text-[10.5px] cursor-pointer">查看详情</button>
                      </td>
                    </tr>
                    <tr v-if="!promotionCommissionLoading && promotionCommissions.length === 0">
                      <td colspan="6" class="p-8 text-center text-brand-secondary font-mono">暂无返佣记录</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <div v-else-if="activePrimary === 'promotion' && activePromotion === 'rules'" class="space-y-6 text-left animate-fade-in">
            <div class="bg-white border border-gray-100 rounded-2xl p-6 space-y-6 shadow-sm min-h-[420px]">
              <div class="flex justify-between items-center pb-3 border-b border-gray-100">
                <div class="space-y-0.5">
                  <h3 class="font-bold text-brand-ink-strong text-base flex items-center gap-1.5 text-brand-primary">
                    <Settings :size="16" />
                    <span>规则配置</span>
                  </h3>
                  <p class="text-xs text-brand-secondary">门槛、返佣比例、最低提现和完成判定都在此维护。</p>
                </div>
                <button @click="savePromotionRules" class="bg-brand-primary hover:bg-brand-primary-strong text-white px-5 py-2 rounded-xl text-xs font-bold">
                  {{ promotionRulesSaving ? '保存中...' : '保存规则' }}
                </button>
              </div>
              <div v-if="promotionRulesError" class="text-xs text-red-600 bg-red-50 border border-red-100 rounded-xl px-3 py-2">
                {{ promotionRulesError }}
              </div>
              <div v-if="promotionRulesDraft" class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                <label class="space-y-1 block">
                  <span class="text-brand-secondary">普通大使门槛</span>
                  <input v-model.number="promotionRulesDraft.normal_threshold_cents" type="number" class="w-full bg-gray-50 border border-gray-100 rounded-xl p-2.5 outline-none" />
                </label>
                <label class="space-y-1 block">
                  <span class="text-brand-secondary">高级大使门槛</span>
                  <input v-model.number="promotionRulesDraft.senior_threshold_cents" type="number" class="w-full bg-gray-50 border border-gray-100 rounded-xl p-2.5 outline-none" />
                </label>
                <label class="space-y-1 block">
                  <span class="text-brand-secondary">普通返佣比例</span>
                  <input v-model.number="promotionRulesDraft.normal_commission_rate" type="number" step="0.01" class="w-full bg-gray-50 border border-gray-100 rounded-xl p-2.5 outline-none" />
                </label>
                <label class="space-y-1 block">
                  <span class="text-brand-secondary">高级返佣比例</span>
                  <input v-model.number="promotionRulesDraft.senior_commission_rate" type="number" step="0.01" class="w-full bg-gray-50 border border-gray-100 rounded-xl p-2.5 outline-none" />
                </label>
                <label class="space-y-1 block">
                  <span class="text-brand-secondary">最低提现门槛</span>
                  <input v-model.number="promotionRulesDraft.min_withdraw_cents" type="number" class="w-full bg-gray-50 border border-gray-100 rounded-xl p-2.5 outline-none" />
                </label>
                <label class="space-y-1 block">
                  <span class="text-brand-secondary">订单完成判定天数</span>
                  <input v-model.number="promotionRulesDraft.order_completion_days" type="number" class="w-full bg-gray-50 border border-gray-100 rounded-xl p-2.5 outline-none" />
                </label>
              </div>
            </div>
          </div>

          <div v-else-if="activePrimary === 'settings'" class="space-y-6 text-left">
            <div class="bg-white border border-gray-100 rounded-2xl p-6 space-y-6 shadow-sm">
              <div class="flex justify-between items-center pb-3 border-b border-gray-100">
                <div class="space-y-0.5">
                  <h3 class="font-bold text-brand-ink-strong">易如反掌系统参数与运营设置</h3>
                  <p class="text-xs text-brand-secondary">套餐、积分规则、大模型密钥管理与客服联系方式配置。</p>
                </div>
                <div class="flex gap-2">
                  <button @click="loadRuntimeConfig" class="bg-white border border-gray-100 text-brand-secondary px-5 py-2.5 rounded-xl text-xs font-bold hover:bg-gray-50">
                    {{ runtimeConfigLoading ? '刷新中...' : '刷新配置' }}
                  </button>
                  <button @click="loadLlmKeys" class="bg-brand-primary hover:bg-brand-primary-strong text-white px-5 py-2.5 rounded-xl text-xs font-bold transition-all outline-none cursor-pointer shadow-sm shadow-brand-primary/10">
                    刷新密钥
                  </button>
                </div>
              </div>

              <div v-if="runtimeConfigError" class="text-xs text-red-600 bg-red-50 border border-red-100 rounded-xl px-3 py-2">
                {{ runtimeConfigError }}
              </div>

              <div class="space-y-4">
                <h4 class="text-xs font-bold text-brand-secondary font-mono uppercase pb-2 border-b border-gray-100">1. 系统配置</h4>
                <div v-if="systemConfigItems.length" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div v-for="item in systemConfigItems" :key="item.config_key" class="bg-brand-paper/40 border border-gray-100 rounded-xl p-4 space-y-2">
                    <div class="flex items-center justify-between gap-2">
                      <div>
                        <div class="text-sm font-bold text-brand-ink-strong">{{ item.label }}</div>
                        <div class="text-[10px] text-brand-secondary font-mono">{{ item.config_key }}</div>
                      </div>
                      <span class="text-[10px] px-2 py-0.5 rounded-full border" :class="item.high_risk ? 'bg-red-50 text-red-600 border-red-100' : 'bg-emerald-50 text-emerald-600 border-emerald-100'">
                        {{ item.high_risk ? '高风险' : '常规' }}
                      </span>
                    </div>
                    <template v-if="item.value_type === 'bool'">
                      <AdminSelect
                        v-model="runtimeConfigDrafts[item.config_key]"
                        @change="runtimeConfigDirty = true"
                        :options="booleanToggleSelectOptions"
                        min-width-class="w-full"
                        panel-width-class="w-full"
                      />
                    </template>
                    <template v-else-if="item.value_type === 'json'">
                      <textarea v-model="runtimeConfigDrafts[item.config_key]" class="w-full bg-white border border-gray-100 rounded-lg p-2 text-xs outline-none min-h-24 font-mono"></textarea>
                    </template>
                    <template v-else>
                      <input v-model="runtimeConfigDrafts[item.config_key]" :type="item.value_type === 'int' || item.value_type === 'float' ? 'number' : 'text'" class="w-full bg-white border border-gray-100 rounded-lg p-2 text-xs outline-none" />
                    </template>
                    <div class="text-[11px] text-brand-secondary">默认值：{{ runtimeInputText(item) }}</div>
                  </div>
                </div>

                <button @click="saveRuntimeConfig" class="bg-brand-primary hover:bg-brand-primary-strong text-white px-5 py-2.5 rounded-xl text-xs font-bold transition-all outline-none cursor-pointer shadow-sm shadow-brand-primary/10">
                  {{ runtimeConfigLoading ? '保存中...' : '保存系统配置' }}
                </button>
              </div>

              <div class="space-y-4">
                <h4 class="text-xs font-bold text-brand-secondary font-mono uppercase pb-2 border-b border-gray-100">2. 大模型密钥管理</h4>
                <div class="bg-amber-50/40 border border-amber-100 rounded-xl p-4 text-xs text-amber-700 leading-relaxed">
                  当前为占位配置，不影响线上 DeepSeek 调用。页面不会展示真实 <span class="font-mono font-bold">DEEPSEEK_API_KEY</span>。
                </div>
                <div v-if="llmError" class="text-xs text-red-600 bg-red-50 border border-red-100 rounded-xl px-3 py-2">
                  {{ llmError }}
                </div>
                <div class="flex justify-end">
                  <button @click="beginCreateLlmKey" class="bg-brand-primary text-white px-4 py-2 rounded-xl text-xs font-bold">新增密钥</button>
                </div>
                <div v-if="llmKeyFormMode" class="border border-gray-100 rounded-xl p-4 space-y-3 bg-gray-50/60">
                  <div class="text-xs font-bold text-brand-ink-strong">{{ llmKeyFormMode === 'edit' ? '编辑密钥' : '新增密钥' }}</div>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <input v-model="llmKeyForm.display_name" class="bg-white border border-gray-100 rounded-lg p-2 text-xs outline-none" placeholder="密钥名称" />
                    <input v-model="llmKeyForm.provider" class="bg-white border border-gray-100 rounded-lg p-2 text-xs outline-none" placeholder="供应商" />
                    <input v-model="llmKeyForm.model" class="bg-white border border-gray-100 rounded-lg p-2 text-xs outline-none" placeholder="模型名称" />
                    <input v-model="llmKeyForm.masked_key" class="bg-white border border-gray-100 rounded-lg p-2 text-xs outline-none" placeholder="脱敏 key" />
                    <input v-model="llmKeyForm.secret_ref" class="bg-white border border-gray-100 rounded-lg p-2 text-xs outline-none" placeholder="secret_ref" />
                    <input v-model.number="llmKeyForm.priority" type="number" class="bg-white border border-gray-100 rounded-lg p-2 text-xs outline-none" placeholder="优先级" />
                    <input v-model="llmKeyForm.last_operator" class="bg-white border border-gray-100 rounded-lg p-2 text-xs outline-none" placeholder="最后操作人" />
                    <input v-model="llmKeyForm.remark" class="bg-white border border-gray-100 rounded-lg p-2 text-xs outline-none" placeholder="备注" />
                  </div>
                  <label class="inline-flex items-center gap-2 text-xs text-brand-secondary">
                    <input v-model="llmKeyForm.enabled" type="checkbox" />
                    启用
                  </label>
                  <div class="flex gap-2">
                    <button @click="submitLlmKeyForm" class="bg-brand-primary text-white px-4 py-2 rounded-lg text-xs font-bold">保存</button>
                    <button @click="llmKeyFormMode = null" class="bg-white border border-gray-100 text-brand-secondary px-4 py-2 rounded-lg text-xs font-bold">取消</button>
                  </div>
                </div>
                <div class="overflow-x-auto border border-gray-100 rounded-xl bg-white">
                  <table class="w-full text-xs font-sans text-left">
                    <thead>
                      <tr class="bg-gray-50 border-b border-gray-100 text-brand-secondary uppercase font-mono text-[10px] tracking-wider">
                        <th class="p-3">密钥名称</th>
                        <th class="p-3">供应商</th>
                        <th class="p-3">模型</th>
                        <th class="p-3">脱敏值</th>
                        <th class="p-3">启用状态</th>
                        <th class="p-3">备注</th>
                        <th class="p-3 text-right">操作</th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100">
                      <tr v-for="item in llmKeys" :key="item.key_id" class="hover:bg-brand-paper/50">
                        <td class="p-3 font-bold text-brand-ink-strong">{{ item.display_name }}</td>
                        <td class="p-3 font-mono text-brand-secondary">{{ item.provider }}</td>
                        <td class="p-3 font-mono text-brand-secondary">{{ item.model }}</td>
                        <td class="p-3 font-mono text-brand-ink-strong">{{ item.masked_key }}</td>
                        <td class="p-3">{{ item.enabled ? '启用' : '停用' }}</td>
                        <td class="p-3 text-brand-secondary">{{ item.remark || '--' }}</td>
                        <td class="p-3 text-right">
                          <div class="flex justify-end gap-2">
                            <button @click="beginEditLlmKey(item)" class="text-brand-primary font-bold">编辑</button>
                            <button @click="removeLlmKey(item.key_id)" class="text-red-500 font-bold">删除</button>
                          </div>
                        </td>
                      </tr>
                      <tr v-if="!llmLoading && llmKeys.length === 0">
                        <td colspan="7" class="p-8 text-center text-brand-secondary font-mono">暂无密钥占位配置。真实 DeepSeek 调用仍读取环境变量。</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      <div v-if="selectedUser" class="fixed inset-0 z-50 bg-slate-950/35 backdrop-blur-sm px-4 py-6 flex items-center justify-center">
        <div class="w-full max-w-6xl max-h-[92vh] bg-white border border-gray-100 rounded-3xl shadow-2xl overflow-hidden flex flex-col text-left">
          <div class="px-6 py-5 border-b border-gray-100 flex flex-wrap items-start justify-between gap-5 bg-white">
            <div class="min-w-0 shrink-0 lg:w-[34%]">
              <p class="text-[10px] font-mono text-brand-secondary uppercase font-bold">User Operation File</p>
              <h2 class="font-serif text-xl font-bold text-brand-ink-strong truncate">{{ selectedUser.user.nickname || '未命名用户' }}</h2>
              <p class="font-mono text-[11px] text-brand-secondary select-all break-all">{{ selectedUser.user.user_id }}</p>
            </div>
            <div class="hidden lg:grid flex-1 grid-cols-5 gap-2 text-[10.5px]">
              <button
                v-for="item in selectedUserInfoCards"
                :key="item.key"
                type="button"
                @click="toggleUserInfoCard(item.key)"
                class="bg-brand-paper/60 border rounded-xl px-3 py-2 h-[62px] min-w-0 overflow-hidden text-left transition-colors"
                :title="`${item.label}: ${item.value}`"
                :class="expandedUserInfoKey === item.key ? 'border-brand-primary/30 bg-brand-primary/5' : 'border-gray-100 hover:bg-brand-paper'"
              >
                <span class="block text-brand-secondary">{{ item.label }}</span>
                <b class="block font-mono text-brand-ink-strong truncate leading-snug">{{ compactUserInfoValue(item) }}</b>
                <span class="block font-mono text-[9px] text-brand-secondary truncate">{{ compactUserInfoSub(item) }}</span>
              </button>
            </div>
            <button @click="closeUserSummary" class="bg-brand-paper hover:bg-gray-100 text-brand-ink-strong text-xs px-3 py-1.5 rounded-lg border border-gray-100 shrink-0">
              关闭
            </button>
            <div v-if="expandedUserInfoCard" class="basis-full bg-brand-primary/5 border border-brand-primary/10 rounded-2xl p-3 text-xs">
              <div class="flex items-center justify-between gap-3 mb-1">
                <span class="font-bold text-brand-ink-strong">{{ expandedUserInfoCard.label }}完整信息</span>
                <span class="text-[10px] text-brand-secondary font-mono">点击卡片可收起</span>
              </div>
              <p class="font-mono text-brand-ink-strong break-all select-all leading-relaxed">{{ expandedUserInfoCard.value }}</p>
              <p class="font-mono text-[10px] text-brand-secondary break-all mt-1">{{ expandedUserInfoCard.sub }}</p>
            </div>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-[minmax(0,1.15fr)_minmax(320px,0.85fr)] flex-1 overflow-hidden">
            <section class="p-6 overflow-y-auto space-y-5">
              <div class="grid grid-cols-2 gap-2 text-[10.5px] lg:hidden">
                <button
                  v-for="item in selectedUserInfoCards"
                  :key="item.key"
                  type="button"
                  @click="toggleUserInfoCard(item.key)"
                  class="bg-brand-paper/60 border rounded-xl px-3 py-2 h-[62px] text-left min-w-0 overflow-hidden transition-colors"
                  :title="`${item.label}: ${item.value}`"
                  :class="expandedUserInfoKey === item.key ? 'border-brand-primary/30 bg-brand-primary/5' : 'border-gray-100'"
                >
                  <span class="block text-brand-secondary">{{ item.label }}</span>
                  <b class="block font-mono text-brand-ink-strong truncate leading-snug">{{ compactUserInfoValue(item) }}</b>
                  <span class="block font-mono text-[9px] text-brand-secondary truncate">{{ compactUserInfoSub(item) }}</span>
                </button>
              </div>

              <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-[11px]">
                <div class="bg-brand-paper/50 rounded-xl border border-gray-100 p-3">
                  <span class="text-brand-secondary block">积分</span>
                  <b class="font-mono text-brand-primary text-base">{{ selectedUser.user.points_balance }}</b>
                </div>
                <div class="bg-emerald-50/40 rounded-xl border border-emerald-100 p-3">
                  <span class="text-brand-secondary block">可提现余额</span>
                  <b class="font-mono text-emerald-600 text-base">{{ formatAmount(selectedUser.user.withdrawable_balance_cents) }}</b>
                </div>
                <div class="bg-amber-50/40 rounded-xl border border-amber-100 p-3">
                  <span class="text-brand-secondary block">冻结返佣</span>
                  <b class="font-mono text-amber-600 text-base">{{ formatAmount(selectedUser.user.frozen_commission_cents) }}</b>
                </div>
                <div class="bg-white rounded-xl border border-gray-100 p-3">
                  <span class="text-brand-secondary block">身份等级</span>
                  <b class="font-mono text-brand-ink-strong text-base">{{ identityLabel(selectedUser.identity_level) }}</b>
                </div>
              </div>

              <div class="border border-gray-100 rounded-xl p-4 bg-white">
                <div class="flex items-center justify-between gap-3 mb-3">
                  <h3 class="font-bold text-brand-ink-strong text-sm">经营摘要</h3>
                  <span class="text-[10px] text-brand-secondary font-mono">Business Snapshot</span>
                </div>
                <div class="grid grid-cols-2 md:grid-cols-3 gap-3 text-xs">
                  <p class="text-brand-secondary">近期订单：<b class="text-brand-ink-strong font-mono">{{ selectedUser.recent_order_count }}</b></p>
                  <p class="text-brand-secondary">近期充值额：<b class="text-emerald-600 font-mono">{{ formatAmount(selectedUser.recent_recharge_amount_cents) }}</b></p>
                  <p class="text-brand-secondary">累计充值额：<b class="text-emerald-600 font-mono">{{ formatAmount(selectedUser.total_recharge_amount_cents) }}</b></p>
                  <p class="text-brand-secondary">累计提现额：<b class="text-brand-ink-strong font-mono">{{ formatAmount(selectedUser.total_withdraw_amount_cents) }}</b></p>
                  <p class="text-brand-secondary truncate" :title="selectedUser.promoter_parent_user_id || '--'">上级归属：<b class="text-brand-ink-strong font-mono">{{ shortText(selectedUser.promoter_parent_user_id, 8, 4) }}</b></p>
                  <p class="text-brand-secondary">最近订单状态：<b class="text-brand-ink-strong">{{ selectedUser.latest_order_status || '--' }}</b></p>
                </div>
              </div>

              <div class="border border-gray-100 rounded-xl overflow-hidden bg-white">
                <div class="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
                  <h3 class="font-bold text-brand-ink-strong text-sm">最近订单</h3>
                  <button @click="jumpToOrders(selectedUser.user.user_id)" class="text-brand-primary text-[11px] font-bold hover:underline">查看全部订单</button>
                </div>
                <div class="max-h-[300px] overflow-y-auto">
                  <table class="w-full text-xs">
                    <thead class="sticky top-0 z-10 bg-gray-50 text-brand-secondary font-mono text-[10px] uppercase">
                      <tr>
                        <th class="p-3 text-left">订单</th>
                        <th class="p-3 text-left">套餐</th>
                        <th class="p-3 text-right">金额</th>
                        <th class="p-3 text-left">状态</th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100">
                      <tr v-for="order in selectedUser.recent_orders" :key="order.order_id">
                        <td class="p-3 font-mono text-brand-secondary" :title="order.order_id">{{ shortText(order.order_id, 8, 4) }}</td>
                        <td class="p-3 text-brand-ink-strong">{{ order.package_title }}</td>
                        <td class="p-3 text-right font-mono text-emerald-600 font-bold">{{ formatAmount(order.amount_cents) }}</td>
                        <td class="p-3 text-brand-secondary">{{ order.status }}</td>
                      </tr>
                      <tr v-if="!selectedUser.recent_orders.length">
                        <td colspan="4" class="p-6 text-center text-brand-secondary font-mono">暂无订单摘要</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </section>

            <section class="border-t lg:border-t-0 lg:border-l border-gray-100 bg-gray-50/50 p-6 overflow-y-auto space-y-4">
              <div class="space-y-2">
                <h3 class="font-serif text-base font-bold text-brand-primary">调整及追踪档案</h3>
                <p class="text-xs text-brand-secondary leading-relaxed">这里集中处理积分、状态、身份和上级归属。长 ID 不再占用列表宽度，完整信息保留在弹窗内。</p>
              </div>

              <div class="grid grid-cols-2 gap-2">
                <button @click="jumpToUsageForUser(selectedUser.user.user_id)" class="bg-brand-primary text-white px-3 py-2 rounded-xl text-[10.5px] font-bold">查看功能使用记录</button>
                <button @click="jumpToOrders(selectedUser.user.user_id)" class="bg-white border border-gray-100 text-brand-primary px-3 py-2 rounded-xl text-[10.5px] font-bold">查看订单</button>
                <button @click="openUserEditor('points')" class="bg-white border border-gray-100 text-brand-ink-strong px-3 py-2 rounded-xl text-[10.5px] font-bold">调整积分</button>
                <button @click="openUserEditor('status')" class="bg-white border border-gray-100 text-brand-ink-strong px-3 py-2 rounded-xl text-[10.5px] font-bold">状态管理</button>
                <button @click="openUserEditor('identity')" class="bg-white border border-gray-100 text-brand-ink-strong px-3 py-2 rounded-xl text-[10.5px] font-bold">身份设置</button>
                <button @click="openUserEditor('parent')" class="bg-white border border-gray-100 text-brand-ink-strong px-3 py-2 rounded-xl text-[10.5px] font-bold">上级归属</button>
              </div>

              <div v-if="userEditOpen" class="border border-gray-100 rounded-2xl bg-white p-4 space-y-3 shadow-sm">
                <div class="text-xs font-bold text-brand-ink-strong">执行管理操作</div>
                <template v-if="userEditMode === 'status'">
                  <AdminSelect
                    v-model="userEditValue"
                    :options="userEditStatusSelectOptions"
                    min-width-class="w-full"
                    panel-width-class="w-full"
                  />
                </template>
                <template v-else-if="userEditMode === 'identity'">
                  <AdminSelect
                    v-model="userEditValue"
                    :options="userEditIdentitySelectOptions"
                    min-width-class="w-full"
                    panel-width-class="w-full"
                  />
                </template>
                <template v-else-if="userEditMode === 'points'">
                  <div class="grid grid-cols-3 gap-2">
                    <button
                      v-for="item in userPointOperationOptions"
                      :key="item.value"
                      type="button"
                      @click="userPointOperation = item.value"
                      class="rounded-xl border px-3 py-2 text-left transition-colors"
                      :class="userPointOperation === item.value ? 'bg-brand-primary text-white border-brand-primary shadow-sm shadow-brand-primary/10' : 'bg-gray-50 text-brand-ink-strong border-gray-100 hover:bg-white'"
                    >
                      <span class="block text-[11px] font-bold">{{ item.label }}</span>
                      <span class="block text-[9px] opacity-70">{{ item.desc }}</span>
                    </button>
                  </div>
                  <input
                    v-model="userEditValue"
                    type="number"
                    min="0"
                    step="1"
                    class="w-full bg-gray-50 border border-gray-100 p-2.5 rounded-xl text-xs outline-none"
                    :placeholder="userPointInputPlaceholder"
                  />
                  <p class="text-[10.5px] text-brand-secondary">
                    当前积分：<b class="font-mono text-brand-ink-strong">{{ selectedUser.user.points_balance }}</b> · {{ userPointDeltaPreview }}
                  </p>
                </template>
                <template v-else>
                  <input v-model="userEditValue" type="text" class="w-full bg-gray-50 border border-gray-100 p-2.5 rounded-xl text-xs outline-none" placeholder="上级推广大使用户ID，留空为解绑" />
                </template>
                <input v-model="userEditReason" class="w-full bg-gray-50 border border-gray-100 p-2.5 rounded-xl text-xs outline-none" placeholder="操作原因" />
                <input v-model="userEditNote" class="w-full bg-gray-50 border border-gray-100 p-2.5 rounded-xl text-xs outline-none" placeholder="内部备注" />
                <div class="flex gap-2">
                  <button @click="submitUserEdit" class="flex-1 bg-brand-primary text-white px-3 py-2 rounded-xl text-[10.5px] font-bold">
                    {{ userLoading ? '提交中...' : '确认提交' }}
                  </button>
                  <button @click="userEditOpen = false" class="bg-brand-paper text-brand-secondary px-3 py-2 rounded-xl text-[10.5px] font-bold">取消</button>
                </div>
              </div>
            </section>
          </div>
        </div>
      </div>

      <aside v-if="selectedUsage" class="fixed top-0 right-0 w-full max-w-lg bg-white border-l border-gray-100 h-full flex flex-col p-6 shadow-2xl text-left overflow-y-auto z-50">
        <div class="flex items-start justify-between pb-4 border-b border-gray-100">
          <div>
            <p class="text-[10px] font-mono text-brand-secondary uppercase font-bold">Usage Detail</p>
            <h2 class="font-serif text-lg font-bold text-brand-ink-strong">{{ selectedUsage.record.feature_name || selectedUsage.record.feature_key }}</h2>
            <p class="font-mono text-[11px] text-brand-secondary select-all">{{ selectedUsage.record.usage_record_id }}</p>
          </div>
          <button @click="selectedUsage = null" class="bg-brand-paper hover:bg-gray-100 text-brand-ink-strong text-xs px-3 py-1.5 rounded-lg border border-gray-100">关闭</button>
        </div>

        <div class="space-y-5 py-5 text-xs text-brand-secondary">
          <section class="space-y-2">
            <h3 class="font-bold text-brand-ink-strong">记录信息</h3>
            <p>状态：{{ selectedUsage.record.status }}</p>
            <p>渠道：{{ selectedUsage.record.channel || '--' }}</p>
            <p>业务 ID：{{ selectedUsage.record.target_id || '--' }}</p>
            <p>积分消耗：{{ selectedUsage.record.normal_points_cost }}</p>
          </section>

          <section class="space-y-2 border-t border-gray-100 pt-4">
            <h3 class="font-bold text-brand-ink-strong">查看用户</h3>
            <p>{{ selectedUsage.user.nickname || selectedUsage.user.user_id }}</p>
            <p>状态：{{ selectedUsage.user.status }}</p>
            <p>积分余额：{{ selectedUsage.user.points_balance }}</p>
            <button class="bg-brand-primary text-white px-3 py-1.5 rounded-lg text-[10.5px] font-bold" @click="jumpToUser(selectedUsage.user.user_id)">打开用户管理</button>
          </section>

          <section class="space-y-2 border-t border-gray-100 pt-4">
            <h3 class="font-bold text-brand-ink-strong">最近订单</h3>
            <p v-for="order in selectedUsage.recent_orders" :key="order.order_id" class="border-b border-gray-100 py-2">
              {{ order.package_title }} · {{ formatAmount(order.amount_cents) }} · {{ order.status }}
            </p>
            <p v-if="!selectedUsage.recent_orders.length">暂无订单摘要</p>
            <button class="bg-white border border-gray-100 text-brand-primary px-3 py-1.5 rounded-lg text-[10.5px] font-bold" @click="jumpToOrders(selectedUsage.user.user_id)">打开订单管理</button>
          </section>
        </div>
      </aside>

      <aside v-if="selectedOrder" class="fixed top-0 right-0 w-full max-w-2xl bg-white border-l border-gray-100 h-full flex flex-col p-6 shadow-2xl text-left overflow-y-auto z-50">
        <div class="flex items-start justify-between pb-4 border-b border-gray-100">
          <div>
            <p class="text-[10px] font-mono text-brand-secondary uppercase font-bold">Order Detail</p>
            <h2 class="font-serif text-lg font-bold text-brand-ink-strong">{{ selectedOrder.package_title }}</h2>
            <p class="font-mono text-[11px] text-brand-secondary select-all">{{ selectedOrder.order_id }}</p>
          </div>
          <button @click="selectedOrder = null" class="bg-brand-paper hover:bg-gray-100 text-brand-ink-strong text-xs px-3 py-1.5 rounded-lg border border-gray-100">关闭</button>
        </div>

        <div class="space-y-5 py-5 text-xs text-brand-secondary">
          <section class="grid grid-cols-2 gap-3">
            <div class="bg-gray-50 rounded-xl border border-gray-100 p-3">
              <span class="block text-[10px] uppercase font-bold">状态</span>
              <span class="font-semibold text-brand-ink-strong">{{ orderStatusLabel(selectedOrder.status) }}</span>
            </div>
            <div class="bg-gray-50 rounded-xl border border-gray-100 p-3">
              <span class="block text-[10px] uppercase font-bold">金额</span>
              <span class="font-semibold text-emerald-600 font-mono">{{ formatAmount(selectedOrder.amount_cents) }}</span>
            </div>
            <div class="bg-gray-50 rounded-xl border border-gray-100 p-3">
              <span class="block text-[10px] uppercase font-bold">购买用户</span>
              <span class="font-semibold text-brand-ink-strong">{{ selectedOrder.user_nickname || selectedOrder.user_id }}</span>
            </div>
            <div class="bg-gray-50 rounded-xl border border-gray-100 p-3">
              <span class="block text-[10px] uppercase font-bold">渠道</span>
              <span class="font-semibold text-brand-ink-strong">{{ selectedOrder.channel || '--' }}</span>
            </div>
            <div class="bg-gray-50 rounded-xl border border-gray-100 p-3">
              <span class="block text-[10px] uppercase font-bold">支付时间</span>
              <span class="font-semibold text-brand-ink-strong">{{ formatTime(selectedOrder.paid_at) }}</span>
            </div>
            <div class="bg-gray-50 rounded-xl border border-gray-100 p-3">
              <span class="block text-[10px] uppercase font-bold">完成时间</span>
              <span class="font-semibold text-brand-ink-strong">{{ formatTime(selectedOrder.completed_at) }}</span>
            </div>
          </section>

          <section class="space-y-2 border-t border-gray-100 pt-4">
            <h3 class="font-bold text-brand-ink-strong">订单摘要</h3>
            <p>套餐：{{ selectedOrder.package_title }}（{{ selectedOrder.package_key }}）</p>
            <p>基础积分：{{ selectedOrder.points_amount }}，赠送积分：{{ selectedOrder.bonus_points }}，合计：{{ selectedOrder.total_points }}</p>
            <p>外部单号：{{ selectedOrder.external_order_id || '--' }}</p>
            <p>支付来源：{{ selectedOrder.source }}</p>
            <p>审核备注：{{ selectedOrder.review_note || '--' }}</p>
            <p>证明材料：{{ selectedOrder.proof_url || '--' }}</p>
          </section>

          <section class="space-y-3 border-t border-gray-100 pt-4">
            <h3 class="font-bold text-brand-ink-strong">订单操作</h3>
            <textarea v-model="orderReviewNote" class="w-full bg-gray-50 border border-gray-100 rounded-xl p-3 text-xs outline-none min-h-20" placeholder="审核备注 / 操作说明"></textarea>
            <input v-model="orderRefundReason" class="w-full bg-gray-50 border border-gray-100 rounded-xl p-2.5 text-xs outline-none" placeholder="退款原因（创建退款请求时使用）" />
            <div class="flex flex-wrap gap-2">
              <button @click="reviewSelectedOrder('approve')" class="bg-brand-primary text-white px-3 py-1.5 rounded-lg text-[10.5px] font-bold">通过订单</button>
              <button @click="reviewSelectedOrder('reject')" class="bg-white border border-gray-100 text-brand-secondary px-3 py-1.5 rounded-lg text-[10.5px] font-bold">拒绝订单</button>
              <button @click="createRefundFromSelectedOrder" class="bg-amber-50 border border-amber-100 text-amber-700 px-3 py-1.5 rounded-lg text-[10.5px] font-bold">发起退款</button>
            </div>
            <p v-if="orderActionMessage" class="text-[11px] text-brand-secondary">{{ orderActionMessage }}</p>
          </section>

          <section class="space-y-2 border-t border-gray-100 pt-4">
            <h3 class="font-bold text-brand-ink-strong">退款请求</h3>
            <div v-if="selectedOrder.refund_requests.length" class="space-y-2">
              <div v-for="refund in selectedOrder.refund_requests" :key="refund.refund_id" class="bg-gray-50 border border-gray-100 rounded-xl p-3 space-y-1">
                <div class="flex items-center justify-between gap-2">
                  <span class="font-mono text-brand-ink-strong text-[11px]">{{ refund.refund_id }}</span>
                  <span class="px-2 py-0.5 rounded text-[9px] font-bold inline-block border" :class="orderStatusClass(refund.status)">
                    {{ orderStatusLabel(refund.status) }}
                  </span>
                </div>
                <p>原因：{{ refund.reason || '--' }}</p>
                <p>失败原因：{{ refund.failure_reason || '--' }}</p>
                <p>拒绝原因：{{ refund.reject_reason || '--' }}</p>
                <p>重试次数：{{ refund.retry_count }}</p>
                <p>创建时间：{{ formatTime(refund.created_at) }}</p>
              </div>
            </div>
            <p v-else>暂无退款请求</p>
          </section>

          <section class="space-y-2 border-t border-gray-100 pt-4">
            <h3 class="font-bold text-brand-ink-strong">返佣记录</h3>
            <div v-if="selectedOrder.commission_records.length" class="space-y-2">
              <div v-for="commission in selectedOrder.commission_records" :key="commission.commission_id" class="bg-gray-50 border border-gray-100 rounded-xl p-3 space-y-1">
                <div class="flex items-center justify-between gap-2">
                  <span class="font-mono text-brand-ink-strong text-[11px]">{{ commission.commission_id }}</span>
                  <span class="px-2 py-0.5 rounded text-[9px] font-bold inline-block border" :class="promotionStatusClass(commission.status)">
                    {{ promotionStatusLabel(commission.status) }}
                  </span>
                </div>
                <p>推广用户：{{ commission.promoter_nickname || commission.promoter_user_id }}</p>
                <p>关联用户：{{ commission.invited_user_nickname || commission.invited_user_id || '--' }}</p>
                <p>返佣比例：{{ formatRate(commission.commission_rate) }}，返佣金额：{{ formatAmount(commission.commission_amount_cents) }}</p>
              </div>
            </div>
            <p v-else>暂无返佣记录</p>
          </section>
        </div>
      </aside>

      <aside v-if="selectedPromotionApplication" class="fixed top-0 right-0 w-full max-w-xl bg-white border-l border-gray-100 h-full flex flex-col p-6 shadow-2xl text-left overflow-y-auto z-50">
        <div class="flex items-start justify-between pb-4 border-b border-gray-100">
          <div>
            <p class="text-[10px] font-mono text-brand-secondary uppercase font-bold">Promotion Application</p>
            <h2 class="font-serif text-lg font-bold text-brand-ink-strong">{{ selectedPromotionApplication.user_nickname || selectedPromotionApplication.user_id }}</h2>
            <p class="font-mono text-[11px] text-brand-secondary select-all">{{ selectedPromotionApplication.application_id }}</p>
          </div>
          <button @click="selectedPromotionApplication = null" class="bg-brand-paper hover:bg-gray-100 text-brand-ink-strong text-xs px-3 py-1.5 rounded-lg border border-gray-100">关闭</button>
        </div>

        <div class="space-y-5 py-5 text-xs text-brand-secondary">
          <section class="grid grid-cols-2 gap-3">
            <div class="bg-gray-50 rounded-xl border border-gray-100 p-3">
              <span class="block text-[10px] uppercase font-bold">申请等级</span>
              <span class="font-semibold text-brand-ink-strong">{{ identityLabel(selectedPromotionApplication.requested_level) }}</span>
            </div>
            <div class="bg-gray-50 rounded-xl border border-gray-100 p-3">
              <span class="block text-[10px] uppercase font-bold">当前身份</span>
              <span class="font-semibold text-brand-ink-strong">{{ identityLabel(selectedPromotionApplication.current_identity_level) }}</span>
            </div>
            <div class="bg-gray-50 rounded-xl border border-gray-100 p-3">
              <span class="block text-[10px] uppercase font-bold">姓名</span>
              <span class="font-semibold text-brand-ink-strong">{{ selectedPromotionApplication.applicant_name || '--' }}</span>
            </div>
            <div class="bg-gray-50 rounded-xl border border-gray-100 p-3">
              <span class="block text-[10px] uppercase font-bold">手机号</span>
              <span class="font-semibold text-brand-ink-strong">{{ selectedPromotionApplication.applicant_phone || '--' }}</span>
            </div>
            <div class="bg-gray-50 rounded-xl border border-gray-100 p-3 col-span-2">
              <span class="block text-[10px] uppercase font-bold">状态</span>
              <span class="font-semibold text-brand-ink-strong">{{ promotionStatusLabel(selectedPromotionApplication.status) }}</span>
            </div>
          </section>

          <section class="space-y-2 border-t border-gray-100 pt-4">
            <h3 class="font-bold text-brand-ink-strong">审核操作</h3>
            <textarea v-model="promotionReviewNote" class="w-full bg-gray-50 border border-gray-100 rounded-xl p-3 text-xs outline-none min-h-20" placeholder="审核备注"></textarea>
            <input v-model="promotionRejectReason" class="w-full bg-gray-50 border border-gray-100 rounded-xl p-2.5 text-xs outline-none" placeholder="拒绝原因（仅拒绝时必填）" />
            <div class="flex flex-wrap gap-2">
              <button @click="reviewPromotionApplication('approve')" class="bg-brand-primary text-white px-3 py-1.5 rounded-lg text-[10.5px] font-bold">通过</button>
              <button @click="reviewPromotionApplication('reject')" class="bg-white border border-gray-100 text-brand-secondary px-3 py-1.5 rounded-lg text-[10.5px] font-bold">拒绝</button>
            </div>
          </section>

          <section class="space-y-2 border-t border-gray-100 pt-4">
            <h3 class="font-bold text-brand-ink-strong">申请说明</h3>
            <p>提交时间：{{ formatTime(selectedPromotionApplication.created_at) }}</p>
            <p>审核时间：{{ formatTime(selectedPromotionApplication.reviewed_at) }}</p>
            <p>审核人：{{ selectedPromotionApplication.reviewed_by || '--' }}</p>
            <p>拒绝原因：{{ selectedPromotionApplication.reject_reason || '--' }}</p>
            <p>审核备注：{{ selectedPromotionApplication.review_note || '--' }}</p>
          </section>
        </div>
      </aside>

      <aside v-if="selectedPromotionWithdrawal" class="fixed top-0 right-0 w-full max-w-xl bg-white border-l border-gray-100 h-full flex flex-col p-6 shadow-2xl text-left overflow-y-auto z-50">
        <div class="flex items-start justify-between pb-4 border-b border-gray-100">
          <div>
            <p class="text-[10px] font-mono text-brand-secondary uppercase font-bold">Withdrawal Detail</p>
            <h2 class="font-serif text-lg font-bold text-brand-ink-strong">{{ selectedPromotionWithdrawal.user_nickname || selectedPromotionWithdrawal.user_id }}</h2>
            <p class="font-mono text-[11px] text-brand-secondary select-all">{{ selectedPromotionWithdrawal.withdrawal_id }}</p>
          </div>
          <button @click="selectedPromotionWithdrawal = null" class="bg-brand-paper hover:bg-gray-100 text-brand-ink-strong text-xs px-3 py-1.5 rounded-lg border border-gray-100">关闭</button>
        </div>

        <div class="space-y-5 py-5 text-xs text-brand-secondary">
          <section class="grid grid-cols-2 gap-3">
            <div class="bg-gray-50 rounded-xl border border-gray-100 p-3">
              <span class="block text-[10px] uppercase font-bold">状态</span>
              <span class="font-semibold text-brand-ink-strong">{{ promotionStatusLabel(selectedPromotionWithdrawal.status) }}</span>
            </div>
            <div class="bg-gray-50 rounded-xl border border-gray-100 p-3">
              <span class="block text-[10px] uppercase font-bold">提现金额</span>
              <span class="font-semibold text-emerald-600 font-mono">{{ formatAmount(selectedPromotionWithdrawal.amount_cents) }}</span>
            </div>
            <div class="bg-gray-50 rounded-xl border border-gray-100 p-3">
              <span class="block text-[10px] uppercase font-bold">可提现快照</span>
              <span class="font-semibold text-brand-ink-strong">{{ formatAmount(selectedPromotionWithdrawal.withdrawable_balance_snapshot_cents) }}</span>
            </div>
            <div class="bg-gray-50 rounded-xl border border-gray-100 p-3">
              <span class="block text-[10px] uppercase font-bold">冻结返佣快照</span>
              <span class="font-semibold text-brand-ink-strong">{{ formatAmount(selectedPromotionWithdrawal.frozen_commission_snapshot_cents) }}</span>
            </div>
          </section>

          <section class="space-y-2 border-t border-gray-100 pt-4">
            <h3 class="font-bold text-brand-ink-strong">打款与审核信息</h3>
            <p>可提现余额快照：{{ formatAmount(selectedPromotionWithdrawal.withdrawable_balance_snapshot_cents) }}</p>
            <p>冻结中返佣快照：{{ formatAmount(selectedPromotionWithdrawal.frozen_commission_snapshot_cents) }}</p>
            <p>拒绝原因：{{ selectedPromotionWithdrawal.reject_reason || '--' }}</p>
            <p>审核备注：{{ selectedPromotionWithdrawal.review_note || '--' }}</p>
            <p>打款方式：{{ selectedPromotionWithdrawal.payout_method || '--' }}</p>
            <p>打款凭证：{{ selectedPromotionWithdrawal.payout_proof || '--' }}</p>
            <p>失败原因：{{ selectedPromotionWithdrawal.payout_failure_reason || '--' }}</p>
            <p>审核人：{{ selectedPromotionWithdrawal.reviewed_by || '--' }}</p>
            <p>审核时间：{{ formatTime(selectedPromotionWithdrawal.reviewed_at) }}</p>
            <p>打款时间：{{ formatTime(selectedPromotionWithdrawal.paid_at) }}</p>
          </section>

          <section class="space-y-3 border-t border-gray-100 pt-4">
            <h3 class="font-bold text-brand-ink-strong">提现审核</h3>
            <textarea v-model="withdrawalReviewNote" class="w-full bg-gray-50 border border-gray-100 rounded-xl p-3 text-xs outline-none min-h-20" placeholder="审核备注"></textarea>
            <input v-model="withdrawalRejectReason" class="w-full bg-gray-50 border border-gray-100 rounded-xl p-2.5 text-xs outline-none" placeholder="拒绝原因（仅拒绝时必填）" />
            <div class="flex flex-wrap gap-2">
              <button @click="reviewPromotionWithdrawal('approve')" class="bg-brand-primary text-white px-3 py-1.5 rounded-lg text-[10.5px] font-bold">通过</button>
              <button @click="reviewPromotionWithdrawal('reject')" class="bg-white border border-gray-100 text-brand-secondary px-3 py-1.5 rounded-lg text-[10.5px] font-bold">拒绝</button>
              <button @click="retryPromotionWithdrawal" class="bg-amber-50 border border-amber-100 text-amber-700 px-3 py-1.5 rounded-lg text-[10.5px] font-bold">重试分账</button>
            </div>
          </section>

          <section class="space-y-3 border-t border-gray-100 pt-4">
            <h3 class="font-bold text-brand-ink-strong">手动打款</h3>
            <input v-model="withdrawalPayoutMethod" class="w-full bg-gray-50 border border-gray-100 rounded-xl p-2.5 text-xs outline-none" placeholder="打款方式，如银行卡 / 分账系统" />
            <textarea v-model="withdrawalPayoutProof" class="w-full bg-gray-50 border border-gray-100 rounded-xl p-3 text-xs outline-none min-h-20" placeholder="打款凭证 / 流水单号"></textarea>
            <button @click="markPromotionWithdrawalPaid" class="bg-brand-primary text-white px-3 py-1.5 rounded-lg text-[10.5px] font-bold">标记已打款</button>
          </section>
        </div>
      </aside>

      <aside v-if="selectedPromotionCommission" class="fixed top-0 right-0 w-full max-w-lg bg-white border-l border-gray-100 h-full flex flex-col p-6 shadow-2xl text-left overflow-y-auto z-50">
        <div class="flex items-start justify-between pb-4 border-b border-gray-100">
          <div>
            <p class="text-[10px] font-mono text-brand-secondary uppercase font-bold">Commission Detail</p>
            <h2 class="font-serif text-lg font-bold text-brand-ink-strong">{{ selectedPromotionCommission.promoter_nickname || selectedPromotionCommission.promoter_user_id }}</h2>
            <p class="font-mono text-[11px] text-brand-secondary select-all">{{ selectedPromotionCommission.commission_id }}</p>
          </div>
          <button @click="selectedPromotionCommission = null" class="bg-brand-paper hover:bg-gray-100 text-brand-ink-strong text-xs px-3 py-1.5 rounded-lg border border-gray-100">关闭</button>
        </div>

        <div class="space-y-5 py-5 text-xs text-brand-secondary">
          <section class="grid grid-cols-2 gap-3">
            <div class="bg-gray-50 rounded-xl border border-gray-100 p-3">
              <span class="block text-[10px] uppercase font-bold">状态</span>
              <span class="font-semibold text-brand-ink-strong">{{ promotionStatusLabel(selectedPromotionCommission.status) }}</span>
            </div>
            <div class="bg-gray-50 rounded-xl border border-gray-100 p-3">
              <span class="block text-[10px] uppercase font-bold">返佣金额</span>
              <span class="font-semibold text-emerald-600">{{ formatAmount(selectedPromotionCommission.commission_amount_cents) }}</span>
            </div>
            <div class="bg-gray-50 rounded-xl border border-gray-100 p-3">
              <span class="block text-[10px] uppercase font-bold">返佣比例</span>
              <span class="font-semibold text-brand-ink-strong">{{ formatRate(selectedPromotionCommission.commission_rate) }}</span>
            </div>
            <div class="bg-gray-50 rounded-xl border border-gray-100 p-3">
              <span class="block text-[10px] uppercase font-bold">订单金额</span>
              <span class="font-semibold text-brand-ink-strong">{{ formatAmount(selectedPromotionCommission.order_amount_cents) }}</span>
            </div>
          </section>

          <section class="space-y-2 border-t border-gray-100 pt-4">
            <h3 class="font-bold text-brand-ink-strong">关联信息</h3>
            <p>推广用户：{{ selectedPromotionCommission.promoter_nickname || selectedPromotionCommission.promoter_user_id }}</p>
            <p>邀请用户：{{ selectedPromotionCommission.invited_user_nickname || selectedPromotionCommission.invited_user_id || '--' }}</p>
            <p>订单编号：{{ selectedPromotionCommission.order_id || '--' }}</p>
            <p>返佣类型：{{ selectedPromotionCommission.commission_type }}</p>
            <p>备注：{{ selectedPromotionCommission.remark || '--' }}</p>
            <p>结算时间：{{ formatTime(selectedPromotionCommission.settled_at) }}</p>
            <p>撤回时间：{{ formatTime(selectedPromotionCommission.revoked_at) }}</p>
            <p>创建时间：{{ formatTime(selectedPromotionCommission.created_at) }}</p>
          </section>

          <section class="space-y-2 border-t border-gray-100 pt-4">
            <button v-if="selectedPromotionCommission.promoter_user_id" @click="jumpToUser(selectedPromotionCommission.promoter_user_id)" class="bg-brand-primary text-white px-3 py-1.5 rounded-lg text-[10.5px] font-bold">查看推广用户</button>
            <button v-if="selectedPromotionCommission.invited_user_id" @click="jumpToUser(selectedPromotionCommission.invited_user_id)" class="bg-white border border-gray-100 text-brand-primary px-3 py-1.5 rounded-lg text-[10.5px] font-bold">查看关联用户</button>
          </section>
        </div>
      </aside>
    </div>
  </div>
</template>
