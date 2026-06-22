<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, type Component } from 'vue';
import {
  AlertTriangle,
  ArrowDown,
  ArrowUp,
  Award,
  Calendar,
  CheckCircle2,
  Coins,
  Copy,
  ExternalLink,
  Gift,
  LogOut,
  MessageSquare,
  RotateCcw,
  Search,
  Settings,
  ShoppingBag,
  Sliders,
  Smartphone,
  TrendingUp,
  Users,
  X,
  XCircle,
} from 'lucide-vue-next';
import {
  ApiError,
  adjustInternalUserPoints,
  createInternalPointsClaimLink,
  createInternalLlmApiKey,
  createInternalRechargeOrderRefund,
  deleteInternalCustomerServiceQrCode,
  deleteInternalLlmApiKey,
  disableInternalPointsClaimLink,
  getInternalDashboard,
  getInternalLlmConcurrency,
  getInternalPhoneQimenReview,
  getInternalPhoneQimenSummary,
  getInternalPointsClaimLink,
  getInternalPromotionApplication,
  getInternalPromotionCommission,
  getInternalPromotionRules,
  getInternalPromotionWithdrawal,
  getInternalRechargeOrder,
  getInternalUsageRecord,
  getInternalUserAdminSummary,
  getInternalRuntimeConfigSchema,
  listInternalLlmApiKeys,
  listInternalPhoneQimenReviews,
  listInternalPointsClaimLinks,
  listInternalPointsClaimRecords,
  listInternalPromotionApplications,
  listInternalPromotionCommissions,
  listInternalPromotionWithdrawals,
  listInternalRechargeOrders,
  listInternalRuntimeConfig,
  listInternalUsageRecords,
  listInternalUsers,
  manualCompleteInternalRechargeOrder,
  markInternalPromotionWithdrawalPaid,
  reviewInternalPromotionApplication,
  reviewInternalPromotionWithdrawal,
  reviewInternalRechargeOrder,
  retryInternalPromotionWithdrawalPayout,
  uploadInternalCustomerServiceQrCode,
  updateInternalInitialPointsConfig,
  updateInternalLlmApiKey,
  updateInternalPromotionRules,
  updateInternalRuntimeConfig,
  updateInternalUserIdentity,
  updateInternalUserPromoterParent,
  updateInternalUserStatus,
  resolveApiAssetUrl,
  type InternalLlmApiKeyPayload,
} from '../../lib/api';
import AdminSelect from './AdminSelect.vue';
import type {
  DashboardResponse,
  InternalPhoneQimenReviewDetailResponse,
  InternalPhoneQimenReviewItemResponse,
  InternalPhoneQimenSummaryResponse,
  InternalUserAdminSummaryResponse,
  InternalUserResponse,
  LlmApiKeyResponse,
  LlmConcurrencyStatusResponse,
  PointsClaimLinkResponse,
  PointsClaimRecordResponse,
  PromotionApplicationResponse,
  PromotionCommissionResponse,
  PromotionRulesResponse,
  PromotionWithdrawalResponse,
  RechargeOrderResponse,
  RuntimeConfigEntryResponse,
  RuntimeConfigEntryUpsertRequest,
  RuntimeInitialPointsUpdateResponse,
  RuntimeConfigSchemaItemResponse,
  UsageRecordDetailResponse,
  UsageRecordResponse,
} from '../../types/api';

const ADMIN_TOKEN_KEY = 'easewise_internal_admin_token';

type PrimaryNavKey = 'dashboard' | 'orders' | 'users' | 'features' | 'promotion' | 'settings';
type FeatureNavKey = 'almanac' | 'phone-review' | 'four-pillars' | 'points-claim';
type PromotionNavKey = 'review' | 'withdrawals' | 'commissions' | 'rules';
type SettingsNavKey = 'basic-config' | 'customer-service' | 'voice' | 'safety' | 'llm-concurrency' | 'service-keys';
type DashboardMetric = DashboardResponse['sections'][number]['metrics'][number];
type UserLinkedDestination = 'orders' | 'usage';
type UserPointOperation = 'increase' | 'decrease' | 'set';
type FeatureUsageWindowKey = 'today' | 'yesterday' | 'week' | 'month';
type PhoneReviewAspectConfigModal = 'free' | 'order';
type PointsClaimExpiryUnit = 'hours' | 'days';
type SelectedUserInfoCard = {
  key: 'uid' | 'identity' | 'channel' | 'registered_at' | 'phone' | 'unionid';
  label: string;
  value: string;
  sub: string;
};
type FeatureUsageRankItem = {
  name: string;
  count: number;
  percentage: number;
};
type ServiceKeyPreset = {
  value: string;
  label: string;
  dotClass: string;
  defaultName: string;
};
type RechargePackageDraft = {
  package_key: string;
  price_yuan: number;
  points_amount: number;
  enabled: boolean;
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
  settings?: SettingsNavKey;
  modal?: 'user';
  user_id?: string;
  return?: 'user';
};

const INITIAL_POINTS_CONFIG_KEY = 'points.initial_grant';
const RECHARGE_PACKAGES_CONFIG_KEY = 'recharge.packages';
const PHONE_REVIEW_BASE_POINTS_CONFIG_KEY = 'phone_review.base_points_cost';
const PHONE_REVIEW_ASPECT_UNLOCK_POINTS_CONFIG_KEY = 'phone_review.aspect_unlock_points_cost';
const PHONE_REVIEW_FREE_ASPECTS_CONFIG_KEY = 'phone_review.free_aspect_keys';
const PHONE_REVIEW_ASPECT_ORDER_CONFIG_KEY = 'phone_review.aspect_order';
const PHONE_REVIEW_UNLOCK_ENFORCEMENT_CONFIG_KEY = 'phone_review.unlock_enforcement_enabled';
const FOUR_PILLARS_UNLOCK_ENFORCEMENT_CONFIG_KEY = 'four_pillars.unlock_enforcement_enabled';
const CUSTOMER_SERVICE_WECHAT_ID_CONFIG_KEY = 'customer_service.wechat_id';
const CUSTOMER_SERVICE_CONTACT_URL_CONFIG_KEY = 'customer_service.contact_url';
const CUSTOMER_SERVICE_QR_CODE_URL_CONFIG_KEY = 'customer_service.qr_code_url';
const CUSTOMER_SERVICE_GUIDANCE_TEXT_CONFIG_KEY = 'customer_service.guidance_text';
const CUSTOMER_SERVICE_QR_GUIDANCE_TEXT_CONFIG_KEY = 'customer_service.qr_guidance_text';
const CUSTOMER_SERVICE_COPY_BUTTON_TEXT_CONFIG_KEY = 'customer_service.copy_button_text';
const CUSTOMER_SERVICE_UNCONFIGURED_TEXT_CONFIG_KEY = 'customer_service.unconfigured_text';
const CUSTOMER_SERVICE_COPY_CONFIGS = [
  {key: 'customer_service.copy.default', label: '默认客服文案', scene: '未指定场景', placeholder: '请添加客服微信，客服会协助你处理相关问题。'},
  {key: 'customer_service.copy.recharge_help', label: '充值协助文案', scene: '充值身份协助 / 充值页底部客服', placeholder: '充值订单与手机号、微信 ID 绑定，可跨平台使用。如需协助，请添加客服。'},
  {key: 'customer_service.copy.payment_issue', label: '支付异常文案', scene: '支付处理中 / 支付异常 / 扣款疑问', placeholder: '如果已经扣款或支付状态异常，请添加客服协助核查订单。'},
  {key: 'customer_service.copy.points_insufficient', label: '积分不足文案', scene: '评测积分不足 / 专项解锁积分不足', placeholder: '当前积分不足时，可添加客服协助确认充值或套餐配置。'},
  {key: 'customer_service.copy.account_security', label: '账号安全文案', scene: '忘记密码 / 修改密码人工核验', placeholder: '账号密码相关问题需要人工核验，请添加客服协助处理。'},
  {key: 'customer_service.copy.promotion_consulting', label: '推广咨询文案', scene: '推广合作咨询', placeholder: '推广合作申请、身份开通和规则咨询，可添加客服进一步确认。'},
  {key: 'customer_service.copy.review_support', label: '评测后续支持文案', scene: '评测结果页后续支持', placeholder: '评测后的后续支持、报告疑问和服务说明，可添加客服咨询。'},
];
const CUSTOMER_SERVICE_CONFIG_KEYS = new Set([
  CUSTOMER_SERVICE_WECHAT_ID_CONFIG_KEY,
  CUSTOMER_SERVICE_CONTACT_URL_CONFIG_KEY,
  CUSTOMER_SERVICE_QR_CODE_URL_CONFIG_KEY,
  CUSTOMER_SERVICE_GUIDANCE_TEXT_CONFIG_KEY,
  CUSTOMER_SERVICE_QR_GUIDANCE_TEXT_CONFIG_KEY,
  CUSTOMER_SERVICE_COPY_BUTTON_TEXT_CONFIG_KEY,
  CUSTOMER_SERVICE_UNCONFIGURED_TEXT_CONFIG_KEY,
  ...CUSTOMER_SERVICE_COPY_CONFIGS.map((item) => item.key),
]);
const MAX_RECHARGE_PACKAGE_COUNT = 6;
const PHONE_REVIEW_ASPECT_OPTIONS = [
  {key: 'career', label: '事业'},
  {key: 'wealth', label: '财富'},
  {key: 'love', label: '感情'},
  {key: 'health', label: '健康'},
  {key: 'acad', label: '学业'},
  {key: 'fortune', label: '运势'},
  {key: 'investment', label: '投资'},
  {key: 'travel', label: '出行'},
  {key: 'social', label: '社交'},
  {key: 'family', label: '家庭'},
  {key: 'personality', label: '性格'},
  {key: 'fengshui', label: '风水'},
];

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
  {key: 'four-pillars', label: '四柱八字评测'},
  {key: 'points-claim', label: '积分领取'},
];

const promotionNavItems: Array<{key: PromotionNavKey; label: string}> = [
  {key: 'review', label: '推广审核'},
  {key: 'withdrawals', label: '提现申请审核'},
  {key: 'commissions', label: '返佣记录'},
  {key: 'rules', label: '规则配置'},
];

const settingsNavItems: Array<{key: SettingsNavKey; label: string}> = [
  {key: 'basic-config', label: '基础配置'},
  {key: 'customer-service', label: '客服配置'},
  {key: 'voice', label: '语音播报'},
  {key: 'safety', label: '安全与合规'},
  {key: 'llm-concurrency', label: 'DeepSeek 并发'},
  {key: 'service-keys', label: '服务密钥'},
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
  'four-pillars': Calendar,
  'points-claim': Gift,
};
const promotionNavIcons: Record<PromotionNavKey, Component> = {
  review: Users,
  withdrawals: Coins,
  commissions: Search,
  rules: Settings,
};
const settingsNavIcons: Record<SettingsNavKey, Component> = {
  'basic-config': Sliders,
  'customer-service': MessageSquare,
  voice: Smartphone,
  safety: AlertTriangle,
  'llm-concurrency': Sliders,
  'service-keys': Settings,
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
  {value: 'disabled', label: '禁用', dotClass: 'bg-red-500'},
];

const userEditStatusSelectOptions = [
  {value: 'active', label: '正常', dotClass: 'bg-emerald-500'},
  {value: 'disabled', label: '禁用', dotClass: 'bg-red-500'},
];

const userIdentitySelectOptions = [
  {value: '', label: '全身份', dotClass: 'bg-indigo-500'},
  {value: 'normal_user', label: '普通会员', dotClass: 'bg-gray-400'},
  {value: 'promoter', label: '推广大使', dotClass: 'bg-emerald-500'},
  {value: 'vip_promoter', label: 'VIP 推广大使', dotClass: 'bg-amber-500'},
  {value: 'svip_promoter', label: 'SVIP 推广大使', dotClass: 'bg-purple-500'},
];

const userEditIdentitySelectOptions = userIdentitySelectOptions.filter((option) => option.value !== '');

const usageSceneSelectOptions = [
  {value: '', label: '全部功能', dotClass: 'bg-indigo-500'},
  {value: 'phone_review_base', label: '手机号评测', dotClass: 'bg-blue-500'},
  {value: 'phone_review_aspect_unlock', label: '维度解锁', dotClass: 'bg-emerald-500'},
  {value: 'four_pillars_review_base', label: '四柱八字', dotClass: 'bg-indigo-500'},
  {value: 'four_pillars_aspect_unlock', label: '四柱专项解锁', dotClass: 'bg-teal-500'},
  {value: 'four_pillars_luck_cycle_render', label: '四柱大运综评', dotClass: 'bg-violet-500'},
  {value: 'four_pillars_luck_year_render', label: '四柱流年单年', dotClass: 'bg-fuchsia-500'},
  {value: 'agent_reply', label: '智能体对话', dotClass: 'bg-purple-500'},
  {value: 'almanac_query', label: '黄历查询', dotClass: 'bg-amber-500'},
  {value: 'five_elements_query', label: '五行属性查询', dotClass: 'bg-cyan-500'},
];

const reviewStatusSelectOptions = [
  {value: '', label: '全部状态', dotClass: 'bg-indigo-500'},
  {value: 'processing', label: '生成中', dotClass: 'bg-amber-500'},
  {value: 'completed', label: '已完成', dotClass: 'bg-emerald-500'},
  {value: 'failed', label: '生成失败', dotClass: 'bg-red-500'},
];

const genderSelectOptions = [
  {value: '', label: '全部性别', dotClass: 'bg-indigo-500'},
  {value: 'male', label: '男', dotClass: 'bg-blue-500'},
  {value: 'female', label: '女', dotClass: 'bg-pink-500'},
];

const pointsClaimStatusSelectOptions = [
  {value: '', label: '全部链接', dotClass: 'bg-indigo-500'},
  {value: 'active', label: '有效', dotClass: 'bg-emerald-500'},
  {value: 'expired', label: '已过期', dotClass: 'bg-gray-400'},
  {value: 'disabled', label: '停用', dotClass: 'bg-red-500'},
];

const pointsClaimRecordStatusSelectOptions = [
  {value: '', label: '全部动作', dotClass: 'bg-indigo-500'},
  {value: 'granted', label: '成功领取', dotClass: 'bg-emerald-500'},
  {value: 'already_claimed_this_week', label: '本周重复', dotClass: 'bg-amber-500'},
  {value: 'expired', label: '链接过期', dotClass: 'bg-gray-400'},
  {value: 'disabled', label: '链接停用', dotClass: 'bg-red-500'},
  {value: 'not_started', label: '未开始', dotClass: 'bg-blue-500'},
];

const booleanToggleSelectOptions = [
  {value: true, label: '开启', dotClass: 'bg-emerald-500'},
  {value: false, label: '关闭', dotClass: 'bg-gray-400'},
];

const serviceKeyProviderSelectOptions = [
  {value: 'deepseek', label: 'DeepSeek', dotClass: 'bg-indigo-500'},
  {value: 'aliyun', label: '阿里云', dotClass: 'bg-orange-500'},
];

const serviceKeyPresetMap: Record<string, ServiceKeyPreset[]> = {
  deepseek: [
    {value: 'deepseek-v4-pro', label: 'DeepSeek V4 Pro', dotClass: 'bg-indigo-500', defaultName: 'DeepSeek 主模型 Key'},
    {value: 'deepseek-chat', label: 'DeepSeek Chat', dotClass: 'bg-blue-500', defaultName: 'DeepSeek Chat Key'},
    {value: 'deepseek-reasoner', label: 'DeepSeek Reasoner', dotClass: 'bg-purple-500', defaultName: 'DeepSeek Reasoner Key'},
  ],
  aliyun: [
    {value: 'bailian_api_key', label: '百炼 API Key（推荐）', dotClass: 'bg-orange-500', defaultName: '阿里云百炼 API Key'},
    {value: 'tts_app_key', label: 'NLS TTS AppKey（旧）', dotClass: 'bg-amber-500', defaultName: '阿里云 NLS TTS AppKey'},
    {value: 'nls_access_key_id', label: 'NLS AccessKey ID（自动取 Token）', dotClass: 'bg-cyan-500', defaultName: '阿里云 NLS AccessKey ID'},
    {value: 'nls_access_key_secret', label: 'NLS AccessKey Secret（自动取 Token）', dotClass: 'bg-red-500', defaultName: '阿里云 NLS AccessKey Secret'},
    {value: 'tts_token', label: 'NLS TTS Token（手动兜底）', dotClass: 'bg-yellow-500', defaultName: '阿里云 NLS TTS Token'},
    {value: 'sms_access_key_id', label: '短信 AccessKey ID（预留）', dotClass: 'bg-cyan-500', defaultName: '阿里云短信 AccessKey ID'},
    {value: 'sms_access_key_secret', label: '短信 AccessKey Secret（预留）', dotClass: 'bg-red-500', defaultName: '阿里云短信 AccessKey Secret'},
  ],
};

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
const activeSettings = ref<SettingsNavKey>('basic-config');
const isFeaturesMenuOpen = ref(true);
const isPromoMenuOpen = ref(true);
const isSettingsMenuOpen = ref(true);
const globalMessage = ref('');

const dashboard = ref<DashboardResponse | null>(null);
const dashboardLoading = ref(false);
const dashboardError = ref('');

const llmKeys = ref<LlmApiKeyResponse[]>([]);
const llmConcurrency = ref<LlmConcurrencyStatusResponse | null>(null);
const llmLoading = ref(false);
const llmConcurrencyLoading = ref(false);
const llmError = ref('');
const llmSchema = ref<RuntimeConfigSchemaItemResponse[]>([]);
const llmKeyFormMode = ref<'create' | 'edit' | null>(null);
const llmEditingKeyId = ref('');
const llmKeyForm = ref<InternalLlmApiKeyPayload>({
  provider: 'deepseek',
  model: 'deepseek-v4-pro',
  display_name: '',
  secret_value: '',
  enabled: true,
  priority: 100,
  max_concurrency: 450,
  cooldown_seconds: 60,
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

const phoneQimenSummaryLoading = ref(false);
const phoneQimenSummaryError = ref('');
const phoneQimenSummary = ref<InternalPhoneQimenSummaryResponse | null>(null);
const phoneReviewLoading = ref(false);
const phoneReviewError = ref('');
const phoneReviewRecords = ref<InternalPhoneQimenReviewItemResponse[]>([]);
const phoneReviewTotal = ref(0);
const phoneReviewPageSize = ref(20);
const phoneReviewOffset = ref(0);
const phoneReviewFilters = ref({
  keyword: '',
  status: '',
  gender: '',
  channel: '',
  date_from: '',
  date_to: '',
  user_id: '',
});
const selectedPhoneReview = ref<InternalPhoneQimenReviewDetailResponse | null>(null);
const phoneReviewDetailLoading = ref(false);

const pointsClaimLoading = ref(false);
const pointsClaimError = ref('');
const pointsClaimLinks = ref<PointsClaimLinkResponse[]>([]);
const pointsClaimTotal = ref(0);
const pointsClaimPageSize = ref(20);
const pointsClaimOffset = ref(0);
const pointsClaimFilters = ref({status: '', keyword: ''});
const pointsClaimRecordsFilters = ref({status: '', user_id: ''});
const pointsClaimRecordsTotal = ref(0);
const pointsClaimRecordsPageSize = ref(20);
const pointsClaimRecordsOffset = ref(0);
const pointsClaimCreating = ref(false);
const pointsClaimForm = ref({
  title: '',
  points_amount: 500,
  display_value_yuan: 0,
  expires_value: 1,
  expires_unit: 'days' as PointsClaimExpiryUnit,
  operator_note: '',
});
const latestCreatedPointsClaimLink = ref<PointsClaimLinkResponse | null>(null);
const selectedPointsClaimLink = ref<PointsClaimLinkResponse | null>(null);
const selectedPointsClaimRecords = ref<PointsClaimRecordResponse[]>([]);
const pointsClaimRecordsLoading = ref(false);
const pointsClaimRecordsError = ref('');

const userLoading = ref(false);
const userError = ref('');
const userQuery = ref('');
const userFilters = ref({
  status: '',
  identity_level: '',
  channel: '',
});
const users = ref<InternalUserResponse[]>([]);
const userTotal = ref(0);
const userPageSize = ref(20);
const userOffset = ref(0);
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
  adminReturnContext.value?.destination === 'usage' && phoneReviewFilters.value.user_id
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
    {key: 'uid', label: 'UID', value: user.uid || '--', sub: '客服检索编号'},
    {key: 'identity', label: '主身份', value: identitySourceLabel(user.primary_identity_type), sub: '身份来源'},
    {key: 'channel', label: '注册渠道', value: user.registered_channel || '--', sub: '来源渠道'},
    {key: 'registered_at', label: '注册时间', value: registeredAt, sub: `首次 ${firstLoginAt}`},
    {key: 'phone', label: '手机号', value: user.primary_phone || '--', sub: user.phone_verified_at ? `验证 ${formatTime(user.phone_verified_at)}` : '待绑定'},
    {key: 'unionid', label: 'UnionID', value: identityValue, sub: identityValue === '--' ? '待绑定' : '点击查看全文'},
  ];
});
const expandedUserInfoCard = computed(() => selectedUserInfoCards.value.find((item) => item.key === expandedUserInfoKey.value) || null);
const activeCode = computed(() => {
  if (activePrimary.value === 'features') {
    if (activeFeature.value === 'almanac') return 'features_almanac';
    if (activeFeature.value === 'four-pillars') return 'features_four_pillars';
    if (activeFeature.value === 'points-claim') return 'features_points_claim';
    return 'features_phone';
  }
  if (activePrimary.value === 'promotion') {
    return `promo_${activePromotion.value}`;
  }
  if (activePrimary.value === 'settings') {
    return `settings_${activeSettings.value.replace('-', '_')}`;
  }
  return activePrimary.value;
});
const activeSettingsTitle = computed(() => {
  const titleMap: Record<SettingsNavKey, string> = {
    'basic-config': '基础配置',
    'customer-service': '客服配置',
    voice: '语音播报',
    safety: '安全与合规',
    'llm-concurrency': 'DeepSeek 并发治理',
    'service-keys': '服务密钥管理',
  };
  return titleMap[activeSettings.value];
});
const activeSettingsDescription = computed(() => {
  const descriptionMap: Record<SettingsNavKey, string> = {
    'basic-config': '维护平台充值总开关等基础项，客服、语音、安全和密钥已拆分为独立子项。',
    'customer-service': '统一维护前台“联系客服”弹窗的二维码、微信号和各业务场景文案。',
    voice: '维护语音播报模式、自动播报、供应商、音色和缓存策略。',
    safety: '维护安全模式、允许功能和强制隐藏功能。',
    'llm-concurrency': '查看 DeepSeek key 池、等待队列、429 冷却和前后台调度状态。',
    'service-keys': '配置 DeepSeek、阿里云 NLS / 百炼等第三方服务密钥。',
  };
  return descriptionMap[activeSettings.value];
});
const activeHeaderTitle = computed(() => {
  if (activePrimary.value === 'dashboard') return '经营决策中心';
  if (activePrimary.value === 'orders') return '会员充值订单审计部';
  if (activePrimary.value === 'users') return '测算用户流水分账部';
  if (activePrimary.value === 'features' && activeFeature.value === 'almanac') return '日常黄历万年历日课定制';
  if (activePrimary.value === 'features' && activeFeature.value === 'four-pillars') return '四柱八字评测配置';
  if (activePrimary.value === 'features' && activeFeature.value === 'points-claim') return '运营积分领取链接中心';
  if (activePrimary.value === 'features') return '手算五行手机号评测算法';
  if (activePrimary.value === 'promotion' && activePromotion.value === 'review') return '合伙人入驻资质审批中心';
  if (activePrimary.value === 'promotion' && activePromotion.value === 'withdrawals') return '合伙佣金提现风险审计部';
  if (activePrimary.value === 'promotion' && activePromotion.value === 'commissions') return '大众代理推广返佣流水';
  if (activePrimary.value === 'promotion') return '推广合作规则维护';
  if (activePrimary.value === 'settings' && activeSettings.value === 'basic-config') return '全局系统基础配置';
  if (activePrimary.value === 'settings' && activeSettings.value === 'customer-service') return '客服配置中心';
  if (activePrimary.value === 'settings' && activeSettings.value === 'voice') return '语音播报配置中心';
  if (activePrimary.value === 'settings' && activeSettings.value === 'safety') return '安全与合规配置';
  if (activePrimary.value === 'settings' && activeSettings.value === 'llm-concurrency') return 'DeepSeek 并发治理中心';
  if (activePrimary.value === 'settings' && activeSettings.value === 'service-keys') return 'DeepSeek 与阿里云服务密钥库';
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
  four_pillars_review_base: '四柱八字',
  four_pillars_aspect_unlock: '四柱专项解锁',
  four_pillars_luck_cycle_render: '四柱大运综评',
  four_pillars_luck_year_render: '四柱流年单年',
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

const pointsClaimCards = computed(() => {
  const now = Date.now();
  const activeCount = pointsClaimLinks.value.filter((item) => item.effective_status === 'active').length;
  const claimedTotal = pointsClaimLinks.value.reduce((total, item) => total + item.claimed_user_count, 0);
  const duplicateTotal = pointsClaimLinks.value.reduce((total, item) => total + item.duplicate_attempt_count, 0);
  const expiringSoon = pointsClaimLinks.value.filter((item) => {
    if (item.effective_status !== 'active') return false;
    const expiresAt = Date.parse(item.expires_at);
    return Number.isFinite(expiresAt) && expiresAt - now <= 24 * 60 * 60 * 1000;
  }).length;
  return [
    {label: '当前有效链接', value: String(activeCount), sub: `列表共 ${pointsClaimTotal.value || pointsClaimLinks.value.length} 条`},
    {label: '累计成功领取', value: String(claimedTotal), sub: '成功领取人数累计'},
    {label: '重复领取动作', value: String(duplicateTotal), sub: '本周已领取后的访问'},
    {label: '24h 内过期', value: String(expiringSoon), sub: '当前有效链接口径'},
  ];
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
  {label: '推广大使人数', value: metricText('推广合作', ['推广用户', '推广大使'], '0'), sub: '返佣比例可配置'},
  {label: 'VIP 推广大使人数', value: metricText('推广合作', ['VIP 推广大使', 'VIP 推广'], '0'), sub: 'VIP 返佣比例可配置'},
  {label: 'SVIP 推广大使人数', value: metricText('推广合作', ['SVIP 推广大使', 'SVIP 推广'], '0'), sub: 'SVIP 返佣比例可配置'},
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
const initialPointsDraft = ref(10000);
const initialPointsScope = ref<'future_users' | 'all_users'>('future_users');
const initialPointsReason = ref('');
const initialPointsSaving = ref(false);
const initialPointsResult = ref<RuntimeInitialPointsUpdateResponse | null>(null);
const rechargePackageDrafts = ref<RechargePackageDraft[]>([]);
const rechargePackagesDirty = ref(false);
const rechargePackagesSaving = ref(false);
const rechargePackageDragIndex = ref<number | null>(null);
const rechargePackageEditIndex = ref<number | null>(null);
const customerServiceQrInputRef = ref<HTMLInputElement | null>(null);
const customerServiceQrUploading = ref(false);
const customerServiceQrDeleting = ref(false);
const customerServiceQrError = ref('');
const phoneReviewAspectConfigModal = ref<PhoneReviewAspectConfigModal | null>(null);

const featureConfigItems = computed(() => sortRuntimeConfigItems(runtimeConfigSchema.value.filter((item) => (
  !item.admin_hidden
  && item.group === '功能管理'
  && item.config_key.startsWith(activeFeatureConfigPrefix.value)
  && item.config_key !== activeFeatureUnlockEnforcementConfigKey.value
))));
const activeFeatureConfigPrefix = computed(() => (activeFeature.value === 'four-pillars' ? 'four_pillars.' : 'phone_review.'));
const activeFeatureUnlockEnforcementConfigKey = computed(() => (activeFeature.value === 'four-pillars' ? FOUR_PILLARS_UNLOCK_ENFORCEMENT_CONFIG_KEY : PHONE_REVIEW_UNLOCK_ENFORCEMENT_CONFIG_KEY));
const activeFeatureDisplayName = computed(() => (activeFeature.value === 'four-pillars' ? '四柱八字评测' : '手机号评测'));
const activeFeatureDescriptionText = computed(() => (
  activeFeature.value === 'four-pillars'
    ? '维护四柱八字基础消耗、专项消耗、免费专项和展示顺序。'
    : '基础消耗、专项消耗、免费专项和专项展示顺序。'
));
const phoneReviewBaseCostItem = computed(() => featureConfigItems.value.find((item) => item.config_key.endsWith('.base_points_cost')));
const phoneReviewAspectUnlockCostItem = computed(() => featureConfigItems.value.find((item) => item.config_key.endsWith('.aspect_unlock_points_cost')));
const phoneReviewFreeAspectsItem = computed(() => featureConfigItems.value.find((item) => item.config_key === PHONE_REVIEW_FREE_ASPECTS_CONFIG_KEY));
const phoneReviewAspectOrderItem = computed(() => featureConfigItems.value.find((item) => item.config_key === PHONE_REVIEW_ASPECT_ORDER_CONFIG_KEY));
const featureExtraConfigItems = computed(() => featureConfigItems.value.filter((item) => (
  !item.config_key.endsWith('.base_points_cost')
  && !item.config_key.endsWith('.aspect_unlock_points_cost')
)));
const basicSystemConfigItems = computed(() => sortRuntimeConfigItems(runtimeConfigSchema.value.filter((item) => (
  !item.admin_hidden
  && item.group === '系统配置'
  && item.config_key !== INITIAL_POINTS_CONFIG_KEY
  && item.config_key !== RECHARGE_PACKAGES_CONFIG_KEY
  && !CUSTOMER_SERVICE_CONFIG_KEYS.has(item.config_key)
  && item.admin_section !== '语音播报'
  && item.admin_section !== '安全与合规'
  && item.admin_section !== 'DeepSeek 并发治理'
))));
const voiceSystemConfigItems = computed(() => sortRuntimeConfigItems(runtimeConfigSchema.value.filter((item) => !item.admin_hidden && item.admin_section === '语音播报')));
const safetySystemConfigItems = computed(() => sortRuntimeConfigItems(runtimeConfigSchema.value.filter((item) => !item.admin_hidden && item.admin_section === '安全与合规')));
const llmConcurrencyConfigItems = computed(() => sortRuntimeConfigItems(runtimeConfigSchema.value.filter((item) => !item.admin_hidden && item.admin_section === 'DeepSeek 并发治理')));
const llmConcurrencyCards = computed(() => {
  const status = llmConcurrency.value;
  return [
    {label: '当前并发', value: `${status?.global_inflight ?? 0} / ${status?.total_capacity ?? 0}`, sub: `前台 ${status?.foreground_inflight ?? 0} · 后台 ${status?.background_inflight ?? 0}`},
    {label: '等待队列', value: `${status?.foreground_waiting ?? 0} / ${status?.background_waiting ?? 0}`, sub: '前台 / 后台'},
    {label: '启用 Key', value: `${status?.enabled_key_count ?? 0}`, sub: `backend ${status?.backend || 'memory'}`},
    {label: '近1小时 429', value: `${status?.recent_429_count ?? 0}`, sub: `超时 ${status?.recent_timeout_count ?? 0}`},
    {label: '平均等待', value: `${status?.avg_wait_ms ?? 0} ms`, sub: `平均响应 ${status?.avg_duration_ms ?? 0} ms`},
    {label: 'Redis', value: status?.redis_configured ? '已配置' : '未配置', sub: status?.backend_available ? 'backend 可用' : (status?.backend_error || 'backend 不可用')},
  ];
});
const customerServiceBaseConfigItems = computed(() => [
  runtimeConfigSchemaItemForKey(CUSTOMER_SERVICE_WECHAT_ID_CONFIG_KEY, '客服微信号'),
  runtimeConfigSchemaItemForKey(CUSTOMER_SERVICE_QR_GUIDANCE_TEXT_CONFIG_KEY, '二维码提示文案'),
  runtimeConfigSchemaItemForKey(CUSTOMER_SERVICE_COPY_BUTTON_TEXT_CONFIG_KEY, '复制按钮文案'),
  runtimeConfigSchemaItemForKey(CUSTOMER_SERVICE_UNCONFIGURED_TEXT_CONFIG_KEY, '未配置提示'),
]);
const customerServiceCopyConfigItems = computed(() => CUSTOMER_SERVICE_COPY_CONFIGS.map((item) => runtimeConfigSchemaItemForKey(item.key, item.label)));
const customerServiceQrPreviewUrl = computed(() => resolveApiAssetUrl(String(runtimeConfigDrafts.value[CUSTOMER_SERVICE_QR_CODE_URL_CONFIG_KEY] || '')));
const canAddRechargePackage = computed(() => rechargePackageDrafts.value.length < MAX_RECHARGE_PACKAGE_COUNT);
const selectedRechargePackageDraft = computed(() => (
  rechargePackageEditIndex.value === null ? null : rechargePackageDrafts.value[rechargePackageEditIndex.value] || null
));
const rechargePackageGridClass = computed(() => {
  const count = rechargePackageDrafts.value.length;
  if (count <= 1) return 'grid grid-cols-1 gap-2 flex-1 min-h-[176px] auto-rows-fr';
  if (count === 2) return 'grid grid-cols-2 gap-2 flex-1 min-h-[176px] auto-rows-fr';
  if (count === 3) return 'grid grid-cols-3 gap-2 flex-1 min-h-[176px] auto-rows-fr';
  if (count === 4) return 'grid grid-cols-2 gap-2 flex-1 min-h-[176px] auto-rows-fr';
  if (count === 5) return 'grid grid-cols-6 gap-2 flex-1 min-h-[176px] auto-rows-fr';
  return 'grid grid-cols-3 gap-2 flex-1 min-h-[176px] auto-rows-fr';
});
const activeServiceKeyPresetOptions = computed(() => serviceKeyPresetMap[llmKeyForm.value.provider] || serviceKeyPresetMap.deepseek);

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

const visibleUsers = computed(() => users.value);
const userTotalPages = computed(() => Math.max(1, Math.ceil(userTotal.value / userPageSize.value)));
const userCurrentPage = computed(() => Math.floor(userOffset.value / userPageSize.value) + 1);
const userPageStart = computed(() => (userTotal.value === 0 ? 0 : userOffset.value + 1));
const userPageEnd = computed(() => Math.min(userOffset.value + users.value.length, userTotal.value));
const canGoPrevUserPage = computed(() => userOffset.value > 0 && !userLoading.value);
const canGoNextUserPage = computed(() => userOffset.value + userPageSize.value < userTotal.value && !userLoading.value);
const phoneReviewTotalPages = computed(() => Math.max(1, Math.ceil(phoneReviewTotal.value / phoneReviewPageSize.value)));
const phoneReviewCurrentPage = computed(() => Math.floor(phoneReviewOffset.value / phoneReviewPageSize.value) + 1);
const phoneReviewPageStart = computed(() => (phoneReviewTotal.value === 0 ? 0 : phoneReviewOffset.value + 1));
const phoneReviewPageEnd = computed(() => Math.min(phoneReviewOffset.value + phoneReviewRecords.value.length, phoneReviewTotal.value));
const canGoPrevPhoneReviewPage = computed(() => phoneReviewOffset.value > 0 && !phoneReviewLoading.value);
const canGoNextPhoneReviewPage = computed(() => phoneReviewOffset.value + phoneReviewPageSize.value < phoneReviewTotal.value && !phoneReviewLoading.value);
const pointsClaimTotalPages = computed(() => Math.max(1, Math.ceil(pointsClaimTotal.value / pointsClaimPageSize.value)));
const pointsClaimCurrentPage = computed(() => Math.floor(pointsClaimOffset.value / pointsClaimPageSize.value) + 1);
const pointsClaimPageStart = computed(() => (pointsClaimTotal.value === 0 ? 0 : pointsClaimOffset.value + 1));
const pointsClaimPageEnd = computed(() => Math.min(pointsClaimOffset.value + pointsClaimLinks.value.length, pointsClaimTotal.value));
const canGoPrevPointsClaimPage = computed(() => pointsClaimOffset.value > 0 && !pointsClaimLoading.value);
const canGoNextPointsClaimPage = computed(() => pointsClaimOffset.value + pointsClaimPageSize.value < pointsClaimTotal.value && !pointsClaimLoading.value);
const pointsClaimRecordsTotalPages = computed(() => Math.max(1, Math.ceil(pointsClaimRecordsTotal.value / pointsClaimRecordsPageSize.value)));
const pointsClaimRecordsCurrentPage = computed(() => Math.floor(pointsClaimRecordsOffset.value / pointsClaimRecordsPageSize.value) + 1);
const pointsClaimRecordsPageStart = computed(() => (pointsClaimRecordsTotal.value === 0 ? 0 : pointsClaimRecordsOffset.value + 1));
const pointsClaimRecordsPageEnd = computed(() => Math.min(pointsClaimRecordsOffset.value + selectedPointsClaimRecords.value.length, pointsClaimRecordsTotal.value));
const canGoPrevPointsClaimRecordsPage = computed(() => pointsClaimRecordsOffset.value > 0 && !pointsClaimRecordsLoading.value);
const canGoNextPointsClaimRecordsPage = computed(() => pointsClaimRecordsOffset.value + pointsClaimRecordsPageSize.value < pointsClaimRecordsTotal.value && !pointsClaimRecordsLoading.value);
const phoneReviewFreeAspectSummary = computed(() => {
  const keys = runtimeConfigStringList(PHONE_REVIEW_FREE_ASPECTS_CONFIG_KEY).filter(isKnownPhoneReviewAspectKey);
  return keys.length ? keys.map(aspectLabel).join('、') : '未设置免费专项';
});
const phoneReviewOrderedAspectOptions = computed(() => phoneReviewOrderedAspectKeys().map((key, index) => ({
  key,
  label: aspectLabel(key),
  index,
  is_free: isPhoneReviewFreeAspect(key),
})));
const phoneReviewAspectOrderSummary = computed(() => {
  const labels = phoneReviewOrderedAspectOptions.value.map((item) => item.label);
  return labels.length > 4 ? `${labels.slice(0, 4).join('、')} 等 ${labels.length} 项` : labels.join('、');
});
const phoneQimenSummaryCards = computed(() => {
  const summary = phoneQimenSummary.value;
  return [
    {label: '今日评测', value: String(summary?.today_review_count ?? 0), sub: 'UTC+8 今日', tone: 'text-brand-primary'},
    {label: '本周评测', value: String(summary?.week_review_count ?? 0), sub: '自然周累计', tone: 'text-slate-700'},
    {label: '总评测数', value: String(summary?.total_review_count ?? 0), sub: `成功率 ${formatPercent(summary?.success_rate)}`, tone: 'text-emerald-700'},
    {label: '失败记录', value: String(summary?.failed_review_count ?? 0), sub: '可进入详情查看原因', tone: 'text-red-600'},
    {label: '平均生成耗时', value: formatDuration(summary?.average_generation_seconds), sub: '已完成/失败记录', tone: 'text-amber-700'},
    {label: '专项解锁', value: String(summary?.aspect_unlock_count ?? 0), sub: `解锁率 ${formatPercent(summary?.aspect_unlock_rate)}`, tone: 'text-emerald-600'},
    {label: '评测积分消耗', value: String(summary?.review_points_cost ?? 0), sub: '手机号评测基础消耗', tone: 'text-brand-primary-strong'},
    {label: '语音请求', value: String(summary?.voice_request_count ?? 0), sub: '后端 TTS 请求记录', tone: 'text-slate-700'},
  ];
});

function isPrimaryNavKey(value: string | null): value is PrimaryNavKey {
  return ['dashboard', 'orders', 'users', 'features', 'promotion', 'settings'].includes(value || '');
}

function isFeatureNavKey(value: string | null): value is FeatureNavKey {
  return ['almanac', 'phone-review', 'four-pillars', 'points-claim'].includes(value || '');
}

function isPromotionNavKey(value: string | null): value is PromotionNavKey {
  return ['review', 'withdrawals', 'commissions', 'rules'].includes(value || '');
}

function isSettingsNavKey(value: string | null): value is SettingsNavKey {
  return ['basic-config', 'customer-service', 'voice', 'safety', 'llm-concurrency', 'service-keys'].includes(value || '');
}

function userDisplayLabel(userId: string) {
  if (selectedUser.value?.user.user_id === userId) {
    return selectedUser.value.user.nickname || selectedUser.value.user.primary_phone || selectedUser.value.user.uid || shortText(userId, 8, 4);
  }
  const user = users.value.find((item) => item.user_id === userId);
  return user?.nickname || user?.primary_phone || user?.uid || shortText(userId, 8, 4);
}

function userAvatarUrl(user: InternalUserResponse): string {
  return resolveApiAssetUrl(user.avatar_url);
}

function userAvatarInitial(user: InternalUserResponse): string {
  return (user.nickname || user.uid || user.user_id || '?').substring(0, 1);
}

function handleUserAvatarError(event: Event): void {
  const image = event.currentTarget as HTMLImageElement | null;
  if (image) {
    image.style.display = 'none';
  }
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
  phoneReviewFilters.value.user_id = '';
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
  selectedPhoneReview.value = null;
  selectedPointsClaimLink.value = null;
  selectedPointsClaimRecords.value = [];
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
  if (view === 'settings') {
    const settingsParam = params.get('settings');
    activeSettings.value = isSettingsNavKey(settingsParam) ? settingsParam : 'basic-config';
    isSettingsMenuOpen.value = true;
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
    phoneReviewFilters.value.user_id = userId;
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
  if (key === 'settings') {
    isSettingsMenuOpen.value = true;
  }
  writeAdminHistory({
    view: key,
    feature: key === 'features' ? activeFeature.value : undefined,
    promotion: key === 'promotion' ? activePromotion.value : undefined,
    settings: key === 'settings' ? activeSettings.value : undefined,
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

function toggleSettingsPrimary() {
  clearLinkedUserFilters();
  isSettingsMenuOpen.value = !isSettingsMenuOpen.value;
  activePrimary.value = 'settings';
  clearOverlayState();
  writeAdminHistory({view: 'settings', settings: activeSettings.value});
  void loadActivePage();
}

async function loadActivePage() {
  if (!adminToken.value) {
    return;
  }
  if (activePrimary.value === 'dashboard') {
    await Promise.allSettled([loadDashboard(), loadOrders(), loadUsers(), loadUsageRecords(), loadLlmKeys()]);
  }
  if (activePrimary.value === 'features') {
    if (activeFeature.value === 'points-claim') {
      await loadPointsClaimLinks();
    } else {
      await Promise.allSettled([loadRuntimeSchema(), loadRuntimeConfig()]);
    }
  }
  if (activePrimary.value === 'settings') {
    if (activeSettings.value === 'service-keys') {
      await loadLlmKeys();
    } else if (activeSettings.value === 'llm-concurrency') {
      await Promise.allSettled([loadRuntimeSchema(), loadRuntimeConfig(), loadLlmConcurrency(), loadLlmKeys()]);
    } else {
      await Promise.allSettled([loadRuntimeSchema(), loadRuntimeConfig()]);
    }
  }
  if (activePrimary.value === 'features' && activeFeature.value === 'phone-review') {
    await Promise.allSettled([loadPhoneQimenSummary(), loadPhoneReviewRecords()]);
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

async function loadLlmConcurrency() {
  llmConcurrencyLoading.value = true;
  llmError.value = '';
  try {
    llmConcurrency.value = await getInternalLlmConcurrency(adminToken.value);
    globalMessage.value = '';
  } catch (error) {
    const message = resolveError(error);
    llmError.value = message;
    globalMessage.value = message;
  } finally {
    llmConcurrencyLoading.value = false;
  }
}

function runtimeConfigDraftValueFromRaw(value: unknown) {
  return value !== null && typeof value === 'object'
    ? JSON.stringify(value, null, 2)
    : value;
}

function runtimeConfigDraftValue(entry: RuntimeConfigEntryResponse) {
  return runtimeConfigDraftValueFromRaw(entry.value);
}

function runtimeConfigDefaultDraftValue(item: RuntimeConfigSchemaItemResponse) {
  return runtimeConfigDraftValueFromRaw(item.default_value ?? '');
}

function ensureRuntimeConfigDraftDefaults() {
  for (const item of runtimeConfigSchema.value) {
    if (runtimeConfigDrafts.value[item.config_key] === undefined) {
      runtimeConfigDrafts.value[item.config_key] = runtimeConfigDefaultDraftValue(item);
    }
  }
}

function mergeRuntimeConfigEntries(entries: RuntimeConfigEntryResponse[]) {
  const nextEntries = [...runtimeConfigEntries.value];
  for (const entry of entries) {
    const index = nextEntries.findIndex((item) => (
      item.scope_type === entry.scope_type
      && item.scope_key === entry.scope_key
      && item.config_key === entry.config_key
    ));
    if (index >= 0) {
      nextEntries[index] = entry;
    } else {
      nextEntries.push(entry);
    }
    runtimeConfigDrafts.value[entry.config_key] = runtimeConfigDraftValue(entry);
  }
  runtimeConfigEntries.value = nextEntries;
}

function resolveRuntimeConfigValue(configKey: string) {
  const entry = runtimeConfigEntries.value.find((item) => item.config_key === configKey);
  if (entry) return entry.value;
  const schemaItem = runtimeConfigSchema.value.find((item) => item.config_key === configKey);
  return schemaItem?.default_value;
}

function parsePackageDrafts(rawValue: unknown): RechargePackageDraft[] {
  let parsed = rawValue;
  if (typeof parsed === 'string') {
    try {
      parsed = JSON.parse(parsed);
    } catch {
      parsed = [];
    }
  }
  if (!Array.isArray(parsed)) return [];
  return parsed
    .map((item, index) => {
      const record = item && typeof item === 'object' ? item as Record<string, unknown> : {};
      const priceCents = Number(record.price_cents ?? 0);
      const pointsAmount = Number(record.points_amount ?? 0);
      const sortOrder = Number(record.sort_order ?? index);
      return {
        package_key: typeof record.package_key === 'string' ? record.package_key : '',
        price_yuan: Number.isFinite(priceCents) ? Math.max(0, priceCents / 100) : 0,
        points_amount: Number.isFinite(pointsAmount) ? Math.max(0, Math.trunc(pointsAmount)) : 0,
        enabled: record.enabled !== false,
        sort_order: Number.isFinite(sortOrder) ? sortOrder : index,
      };
    })
    .sort((left, right) => left.sort_order - right.sort_order)
    .slice(0, MAX_RECHARGE_PACKAGE_COUNT)
    .map(({package_key, price_yuan, points_amount, enabled}) => ({
      package_key,
      price_yuan,
      points_amount,
      enabled,
    }));
}

function syncSettingsDraftsFromRuntime() {
  ensureRuntimeConfigDraftDefaults();
  const initialValue = Number(resolveRuntimeConfigValue(INITIAL_POINTS_CONFIG_KEY) ?? 10000);
  initialPointsDraft.value = Number.isFinite(initialValue) ? Math.max(0, Math.trunc(initialValue)) : 10000;
  rechargePackageDrafts.value = parsePackageDrafts(resolveRuntimeConfigValue(RECHARGE_PACKAGES_CONFIG_KEY));
  rechargePackagesDirty.value = false;
}

async function loadRuntimeSchema() {
  runtimeConfigSchemaLoading.value = true;
  runtimeConfigError.value = '';
  try {
    runtimeConfigSchema.value = (await getInternalRuntimeConfigSchema(adminToken.value)).items;
    syncSettingsDraftsFromRuntime();
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
    const entries = (await listInternalRuntimeConfig(adminToken.value)).items;
    runtimeConfigEntries.value = entries;
    runtimeConfigDrafts.value = {};
    for (const entry of entries) {
      runtimeConfigDrafts.value[entry.config_key] = runtimeConfigDraftValue(entry);
    }
    syncSettingsDraftsFromRuntime();
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

async function loadPhoneQimenSummary() {
  phoneQimenSummaryLoading.value = true;
  phoneQimenSummaryError.value = '';
  try {
    phoneQimenSummary.value = await getInternalPhoneQimenSummary(adminToken.value);
    globalMessage.value = '';
  } catch (error) {
    const message = resolveError(error);
    phoneQimenSummaryError.value = message;
    globalMessage.value = message;
  } finally {
    phoneQimenSummaryLoading.value = false;
  }
}

async function loadPhoneReviewRecords(options: {resetPage?: boolean} = {}) {
  if (options.resetPage) {
    phoneReviewOffset.value = 0;
  }
  phoneReviewLoading.value = true;
  phoneReviewError.value = '';
  try {
    const response = await listInternalPhoneQimenReviews(adminToken.value, {
      ...phoneReviewFilters.value,
      limit: phoneReviewPageSize.value,
      offset: phoneReviewOffset.value,
    });
    phoneReviewRecords.value = response.items;
    phoneReviewTotal.value = response.total;
    phoneReviewPageSize.value = response.limit;
    phoneReviewOffset.value = response.offset;
    globalMessage.value = '';
  } catch (error) {
    const message = resolveError(error);
    phoneReviewError.value = message;
    globalMessage.value = message;
  } finally {
    phoneReviewLoading.value = false;
  }
}

async function loadPointsClaimLinks(options: {resetPage?: boolean} = {}) {
  if (options.resetPage) {
    pointsClaimOffset.value = 0;
  }
  pointsClaimLoading.value = true;
  pointsClaimError.value = '';
  try {
    const response = await listInternalPointsClaimLinks(adminToken.value, {
      ...pointsClaimFilters.value,
      limit: pointsClaimPageSize.value,
      offset: pointsClaimOffset.value,
    });
    pointsClaimLinks.value = response.items;
    pointsClaimTotal.value = response.total;
    pointsClaimPageSize.value = response.limit;
    pointsClaimOffset.value = response.offset;
    globalMessage.value = '';
  } catch (error) {
    const message = resolveError(error);
    pointsClaimError.value = message;
    globalMessage.value = message;
  } finally {
    pointsClaimLoading.value = false;
  }
}

async function searchPointsClaimLinks() {
  await loadPointsClaimLinks({resetPage: true});
}

function resetPointsClaimFilters() {
  pointsClaimFilters.value = {status: '', keyword: ''};
  pointsClaimOffset.value = 0;
}

async function changePointsClaimPage(direction: number) {
  const maxOffset = Math.max(0, (pointsClaimTotalPages.value - 1) * pointsClaimPageSize.value);
  const nextOffset = Math.min(maxOffset, Math.max(0, pointsClaimOffset.value + direction * pointsClaimPageSize.value));
  if (nextOffset === pointsClaimOffset.value) {
    return;
  }
  pointsClaimOffset.value = nextOffset;
  await loadPointsClaimLinks();
}

function validatePointsClaimForm(): string | null {
  const title = pointsClaimForm.value.title.trim();
  const pointsAmount = Math.trunc(Number(pointsClaimForm.value.points_amount));
  const displayValueYuan = Number(pointsClaimForm.value.display_value_yuan);
  const expiresInHours = resolvePointsClaimExpiresInHours();
  if (!title) {
    return '请填写链接名称，方便客服识别活动。';
  }
  if (!Number.isFinite(pointsAmount) || pointsAmount <= 0) {
    return '领取积分必须是大于 0 的整数。';
  }
  if (!Number.isFinite(displayValueYuan) || displayValueYuan < 0) {
    return '展示人民币价值不能小于 0。';
  }
  if (!expiresInHours) {
    return pointsClaimForm.value.expires_unit === 'days'
      ? '有效期必须是 1 到 30 天之间的整数。'
      : '有效期必须是 1 到 720 小时之间的整数。';
  }
  if (expiresInHours > 24 * 30) {
    return '有效期最多可配置 30 天。';
  }
  return null;
}

function resolvePointsClaimExpiresInHours(): number | null {
  const rawValue = Math.trunc(Number(pointsClaimForm.value.expires_value));
  if (!Number.isFinite(rawValue) || rawValue <= 0) {
    return null;
  }
  const multiplier = pointsClaimForm.value.expires_unit === 'days' ? 24 : 1;
  return rawValue * multiplier;
}

async function createPointsClaimLink() {
  const validationMessage = validatePointsClaimForm();
  if (validationMessage) {
    pointsClaimError.value = validationMessage;
    globalMessage.value = validationMessage;
    return;
  }
  pointsClaimCreating.value = true;
  pointsClaimError.value = '';
  try {
    const created = await createInternalPointsClaimLink(adminToken.value, {
      title: pointsClaimForm.value.title.trim(),
      points_amount: Math.trunc(Number(pointsClaimForm.value.points_amount)),
      display_value_cents: Math.round(Number(pointsClaimForm.value.display_value_yuan || 0) * 100),
      expires_in_hours: resolvePointsClaimExpiresInHours(),
      operator_note: pointsClaimForm.value.operator_note.trim() || null,
    });
    latestCreatedPointsClaimLink.value = created;
    pointsClaimForm.value = {
      title: '',
      points_amount: created.points_amount,
      display_value_yuan: Number((created.display_value_cents / 100).toFixed(2)),
      expires_value: 1,
      expires_unit: 'days',
      operator_note: '',
    };
    globalMessage.value = '积分领取链接已生成';
    await loadPointsClaimLinks({resetPage: true});
  } catch (error) {
    const message = resolveError(error);
    pointsClaimError.value = message;
    globalMessage.value = message;
  } finally {
    pointsClaimCreating.value = false;
  }
}

async function openPointsClaimLink(link: PointsClaimLinkResponse) {
  selectedPointsClaimLink.value = link;
  selectedPointsClaimRecords.value = [];
  pointsClaimRecordsFilters.value = {status: '', user_id: ''};
  pointsClaimRecordsOffset.value = 0;
  try {
    selectedPointsClaimLink.value = await getInternalPointsClaimLink(adminToken.value, link.claim_link_id);
  } catch (error) {
    globalMessage.value = resolveError(error);
  }
  await loadPointsClaimRecords({resetPage: true});
}

async function disablePointsClaimLink(link: PointsClaimLinkResponse) {
  if (
    typeof window !== 'undefined'
    && !window.confirm(`确认停用「${link.title}」？停用后用户访问会被记录但不再发放积分。`)
  ) {
    return;
  }
  pointsClaimLoading.value = true;
  try {
    const updated = await disableInternalPointsClaimLink(adminToken.value, link.claim_link_id, {
      operator_note: 'internal_admin_disabled',
    });
    latestCreatedPointsClaimLink.value = latestCreatedPointsClaimLink.value?.claim_link_id === updated.claim_link_id
      ? updated
      : latestCreatedPointsClaimLink.value;
    if (selectedPointsClaimLink.value?.claim_link_id === updated.claim_link_id) {
      selectedPointsClaimLink.value = updated;
    }
    globalMessage.value = '积分领取链接已停用';
    await loadPointsClaimLinks();
  } catch (error) {
    globalMessage.value = resolveError(error);
  } finally {
    pointsClaimLoading.value = false;
  }
}

async function loadPointsClaimRecords(options: {resetPage?: boolean} = {}) {
  if (!selectedPointsClaimLink.value) {
    return;
  }
  if (options.resetPage) {
    pointsClaimRecordsOffset.value = 0;
  }
  pointsClaimRecordsLoading.value = true;
  pointsClaimRecordsError.value = '';
  try {
    const response = await listInternalPointsClaimRecords(adminToken.value, selectedPointsClaimLink.value.claim_link_id, {
      ...pointsClaimRecordsFilters.value,
      limit: pointsClaimRecordsPageSize.value,
      offset: pointsClaimRecordsOffset.value,
    });
    selectedPointsClaimRecords.value = response.items;
    pointsClaimRecordsTotal.value = response.total;
    pointsClaimRecordsPageSize.value = response.limit;
    pointsClaimRecordsOffset.value = response.offset;
  } catch (error) {
    pointsClaimRecordsError.value = resolveError(error);
  } finally {
    pointsClaimRecordsLoading.value = false;
  }
}

async function searchPointsClaimRecords() {
  await loadPointsClaimRecords({resetPage: true});
}

function resetPointsClaimRecordsFilters() {
  pointsClaimRecordsFilters.value = {status: '', user_id: ''};
  pointsClaimRecordsOffset.value = 0;
}

async function changePointsClaimRecordsPage(direction: number) {
  const maxOffset = Math.max(0, (pointsClaimRecordsTotalPages.value - 1) * pointsClaimRecordsPageSize.value);
  const nextOffset = Math.min(maxOffset, Math.max(0, pointsClaimRecordsOffset.value + direction * pointsClaimRecordsPageSize.value));
  if (nextOffset === pointsClaimRecordsOffset.value) {
    return;
  }
  pointsClaimRecordsOffset.value = nextOffset;
  await loadPointsClaimRecords();
}

async function searchPhoneReviewRecords() {
  await loadPhoneReviewRecords({resetPage: true});
}

async function refreshPhoneQimenPage() {
  await Promise.allSettled([loadPhoneQimenSummary(), loadPhoneReviewRecords()]);
}

function resetPhoneReviewFilters() {
  phoneReviewFilters.value = {
    keyword: '',
    status: '',
    gender: '',
    channel: '',
    date_from: '',
    date_to: '',
    user_id: phoneReviewFilters.value.user_id,
  };
  phoneReviewOffset.value = 0;
}

async function changePhoneReviewPage(direction: number) {
  const maxOffset = Math.max(0, (phoneReviewTotalPages.value - 1) * phoneReviewPageSize.value);
  const nextOffset = Math.min(maxOffset, Math.max(0, phoneReviewOffset.value + direction * phoneReviewPageSize.value));
  if (nextOffset === phoneReviewOffset.value) {
    return;
  }
  phoneReviewOffset.value = nextOffset;
  await loadPhoneReviewRecords();
}

async function openPhoneReviewDetail(record: InternalPhoneQimenReviewItemResponse) {
  phoneReviewDetailLoading.value = true;
  selectedPhoneReview.value = null;
  try {
    selectedPhoneReview.value = await getInternalPhoneQimenReview(adminToken.value, record.review_id);
    globalMessage.value = '';
  } catch (error) {
    globalMessage.value = resolveError(error);
  } finally {
    phoneReviewDetailLoading.value = false;
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

async function loadUsers(options: {resetPage?: boolean} = {}) {
  if (options.resetPage) {
    userOffset.value = 0;
  }
  userLoading.value = true;
  userError.value = '';
  try {
    const response = await listInternalUsers(adminToken.value, {
      keyword: userQuery.value,
      ...userFilters.value,
      limit: userPageSize.value,
      offset: userOffset.value,
    });
    users.value = response.items;
    userTotal.value = response.total;
    userPageSize.value = response.limit;
    userOffset.value = response.offset;
    globalMessage.value = '';
  } catch (error) {
    const message = resolveError(error);
    userError.value = message;
    globalMessage.value = message;
  } finally {
    userLoading.value = false;
  }
}

async function searchUsers() {
  await loadUsers({resetPage: true});
}

function resetUserFilters() {
  userQuery.value = '';
  userFilters.value = {status: '', identity_level: '', channel: ''};
  userOffset.value = 0;
}

async function changeUserPage(direction: number) {
  const maxOffset = Math.max(0, (userTotalPages.value - 1) * userPageSize.value);
  const nextOffset = Math.min(maxOffset, Math.max(0, userOffset.value + direction * userPageSize.value));
  if (nextOffset === userOffset.value) {
    return;
  }
  userOffset.value = nextOffset;
  await loadUsers();
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

async function manualCompleteSelectedOrder() {
  if (!selectedOrder.value) return;
  if (!canManualCompleteOrder(selectedOrder.value)) {
    orderActionMessage.value = '当前订单状态不可手动完成';
    return;
  }
  orderActionMessage.value = '';
  try {
    const result = await manualCompleteInternalRechargeOrder(adminToken.value, selectedOrder.value.order_id, {
      payment_method: 'offline_customer_service',
      payment_reference: null,
      operator_note: orderReviewNote.value || null,
    });
    selectedOrder.value = result.order;
    orderActionMessage.value = `已确认线下收款，已发放 ${result.ledger?.delta ?? result.order.total_points} 积分`;
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

function jumpToNullableUser(userId: string | null | undefined) {
  if (!userId) return;
  jumpToUser(userId);
}

function jumpToUsageForUser(userId: string) {
  activePrimary.value = 'features';
  activeFeature.value = 'phone-review';
  isFeaturesMenuOpen.value = true;
  phoneReviewFilters.value.user_id = userId;
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
  phoneReviewFilters.value.user_id = '';
  clearLinkedUserContext();
  selectedUsage.value = null;
  selectedPhoneReview.value = null;
  writeAdminHistory({view: 'features', feature: activeFeature.value}, 'replace');
  void Promise.allSettled([loadPhoneQimenSummary(), loadPhoneReviewRecords({resetPage: true})]);
}

function selectFeature(key: FeatureNavKey) {
  clearLinkedUserFilters();
  isFeaturesMenuOpen.value = true;
  activeFeature.value = key;
  activePrimary.value = 'features';
  clearOverlayState();
  writeAdminHistory({view: 'features', feature: key});
  if (key === 'phone-review') {
    void Promise.allSettled([loadPhoneQimenSummary(), loadPhoneReviewRecords()]);
  }
  if (key === 'points-claim') {
    void loadPointsClaimLinks();
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

function selectSettings(key: SettingsNavKey) {
  clearLinkedUserFilters();
  isSettingsMenuOpen.value = true;
  activeSettings.value = key;
  activePrimary.value = 'settings';
  clearOverlayState();
  writeAdminHistory({view: 'settings', settings: key});
  void loadActivePage();
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
  const value = rawValue === undefined ? item.default_value : rawValue;
  if (item.value_type === 'bool') {
    return Boolean(value);
  }
  if (item.value_type === 'int') {
    const parsed = Number.parseInt(String(value), 10);
    return Number.isFinite(parsed) ? parsed : item.default_value;
  }
  if (item.value_type === 'float') {
    const parsed = Number.parseFloat(String(value));
    return Number.isFinite(parsed) ? parsed : item.default_value;
  }
  if (item.value_type === 'json') {
    if (value === undefined || value === null || value === '') {
      return item.default_value ?? null;
    }
    if (typeof value === 'string') {
      try {
        return JSON.parse(value);
      } catch {
        return item.default_value ?? null;
      }
    }
    return value;
  }
  return value === undefined ? null : value;
}

function sortRuntimeConfigItems(items: RuntimeConfigSchemaItemResponse[]) {
  return [...items].sort((left, right) => (left.sort_order ?? 100) - (right.sort_order ?? 100));
}

function runtimeConfigStringList(configKey: string): string[] {
  const value = runtimeConfigDrafts.value[configKey];
  if (Array.isArray(value)) {
    return value.map((item) => String(item));
  }
  if (typeof value === 'string') {
    try {
      const parsed = JSON.parse(value);
      if (Array.isArray(parsed)) {
        return parsed.map((item) => String(item));
      }
    } catch {
      return value.split(',').map((item) => item.trim()).filter(Boolean);
    }
  }
  return [];
}

function toggleRuntimeConfigStringListValue(configKey: string, optionValue: string) {
  const currentValues = new Set(runtimeConfigStringList(configKey));
  if (currentValues.has(optionValue)) {
    currentValues.delete(optionValue);
  } else {
    currentValues.add(optionValue);
  }
  runtimeConfigDrafts.value[configKey] = [...currentValues];
  runtimeConfigDirty.value = true;
}

function setRuntimeConfigStringList(configKey: string, values: string[]) {
  runtimeConfigDrafts.value[configKey] = [...values];
  runtimeConfigDirty.value = true;
}

function isKnownPhoneReviewAspectKey(aspectKey: string | null | undefined) {
  return PHONE_REVIEW_ASPECT_OPTIONS.some((item) => item.key === aspectKey);
}

function isPhoneReviewFreeAspect(aspectKey: string) {
  return runtimeConfigStringList(PHONE_REVIEW_FREE_ASPECTS_CONFIG_KEY).includes(aspectKey);
}

function togglePhoneReviewFreeAspect(aspectKey: string) {
  const currentValues = new Set(runtimeConfigStringList(PHONE_REVIEW_FREE_ASPECTS_CONFIG_KEY).filter(isKnownPhoneReviewAspectKey));
  if (currentValues.has(aspectKey)) {
    currentValues.delete(aspectKey);
  } else {
    currentValues.add(aspectKey);
  }
  const orderedValues = PHONE_REVIEW_ASPECT_OPTIONS.map((item) => item.key).filter((key) => currentValues.has(key));
  setRuntimeConfigStringList(PHONE_REVIEW_FREE_ASPECTS_CONFIG_KEY, orderedValues);
}

function resetPhoneReviewFreeAspects() {
  setRuntimeConfigStringList(PHONE_REVIEW_FREE_ASPECTS_CONFIG_KEY, []);
}

function phoneReviewOrderedAspectKeys() {
  const seenKeys = new Set<string>();
  const configuredKeys = runtimeConfigStringList(PHONE_REVIEW_ASPECT_ORDER_CONFIG_KEY)
    .filter(isKnownPhoneReviewAspectKey)
    .filter((key) => {
      if (seenKeys.has(key)) return false;
      seenKeys.add(key);
      return true;
    });
  const fallbackKeys = PHONE_REVIEW_ASPECT_OPTIONS.map((item) => item.key).filter((key) => !seenKeys.has(key));
  return [...configuredKeys, ...fallbackKeys];
}

function movePhoneReviewAspectOrder(aspectKey: string, direction: -1 | 1) {
  const orderedKeys = phoneReviewOrderedAspectKeys();
  const currentIndex = orderedKeys.indexOf(aspectKey);
  const nextIndex = currentIndex + direction;
  if (currentIndex < 0 || nextIndex < 0 || nextIndex >= orderedKeys.length) {
    return;
  }
  const [item] = orderedKeys.splice(currentIndex, 1);
  orderedKeys.splice(nextIndex, 0, item);
  setRuntimeConfigStringList(PHONE_REVIEW_ASPECT_ORDER_CONFIG_KEY, orderedKeys);
}

function resetPhoneReviewAspectOrder() {
  setRuntimeConfigStringList(PHONE_REVIEW_ASPECT_ORDER_CONFIG_KEY, PHONE_REVIEW_ASPECT_OPTIONS.map((item) => item.key));
}

function openPhoneReviewAspectConfigModal(mode: PhoneReviewAspectConfigModal) {
  phoneReviewAspectConfigModal.value = mode;
}

function closePhoneReviewAspectConfigModal() {
  phoneReviewAspectConfigModal.value = null;
}

function runtimeConfigDisplayValue(item: RuntimeConfigSchemaItemResponse) {
  const value = runtimeConfigDrafts.value[item.config_key];
  if (value === undefined || value === null || value === '') {
    return item.default_value;
  }
  return value;
}

async function saveRuntimeConfig(items: RuntimeConfigSchemaItemResponse[] = runtimeConfigSchema.value, successMessage = '系统配置已保存') {
  if (!items.length) return;
  const entries: RuntimeConfigEntryUpsertRequest[] = items.map((item) => {
    const value = normalizeRuntimeConfigValue(item, runtimeConfigDrafts.value[item.config_key]);
    return {
      scope_type: item.scope_type,
      scope_key: item.scope_key,
      config_key: item.config_key,
      value: value === undefined ? null : value,
    };
  });
  const backendEntry = entries.find((item) => item.config_key === 'llm.concurrency.backend');
  if (backendEntry?.value === 'redis' && !llmConcurrency.value?.redis_configured) {
    globalMessage.value = 'Redis URL 未在服务端环境变量中配置，不能切换到 redis backend。';
    return;
  }
  const defaultConcurrencyEntry = entries.find((item) => item.config_key === 'llm.deepseek.default_key_max_concurrency');
  if (Number(defaultConcurrencyEntry?.value || 0) > 450 && typeof window !== 'undefined') {
    const confirmed = window.confirm('默认单 Key 并发超过 450，请确认 DeepSeek 侧已扩容。继续保存？');
    if (!confirmed) return;
  }
  const backgroundRatioEntry = entries.find((item) => item.config_key === 'llm.deepseek.background_max_concurrency_ratio');
  if (Number(backgroundRatioEntry?.value || 0) > 0.8) {
    globalMessage.value = '后台预热最大并发占比不能超过 80%。';
    return;
  }
  runtimeConfigLoading.value = true;
  try {
    const result = await updateInternalRuntimeConfig(adminToken.value, entries);
    mergeRuntimeConfigEntries(result.items);
    runtimeConfigDirty.value = false;
    globalMessage.value = successMessage;
    if (entries.some((item) => item.config_key.startsWith('llm.'))) {
      await Promise.allSettled([loadLlmConcurrency(), loadLlmKeys()]);
    }
  } catch (error) {
    globalMessage.value = resolveError(error);
  } finally {
    runtimeConfigLoading.value = false;
  }
}

async function saveInitialPointsSettings() {
  const nextInitialGrant = Math.trunc(Number(initialPointsDraft.value));
  if (!Number.isFinite(nextInitialGrant) || nextInitialGrant < 0) {
    globalMessage.value = '初始积分必须是大于等于 0 的整数';
    return;
  }
  if (
    initialPointsScope.value === 'all_users'
    && typeof window !== 'undefined'
    && !window.confirm('确认按差额调整全部正式用户积分？该操作会写入积分流水。')
  ) {
    return;
  }

  initialPointsSaving.value = true;
  initialPointsResult.value = null;
  try {
    const result = await updateInternalInitialPointsConfig(adminToken.value, {
      initial_grant: nextInitialGrant,
      apply_scope: initialPointsScope.value,
      reason: initialPointsReason.value || null,
    });
    mergeRuntimeConfigEntries([result.entry]);
    initialPointsDraft.value = result.initial_grant;
    initialPointsResult.value = result;
    initialPointsReason.value = '';
    globalMessage.value = result.apply_scope === 'all_users'
      ? `初始积分已保存，并调整 ${result.affected_user_count} 个正式用户`
      : '初始积分已保存，仅影响今后注册用户';
  } catch (error) {
    globalMessage.value = resolveError(error);
  } finally {
    initialPointsSaving.value = false;
  }
}

function addRechargePackageDraft() {
  if (!canAddRechargePackage.value) {
    globalMessage.value = `充值套餐最多只能配置 ${MAX_RECHARGE_PACKAGE_COUNT} 个`;
    return;
  }
  rechargePackageDrafts.value.push({
    package_key: '',
    price_yuan: 9.9,
    points_amount: 1000,
    enabled: true,
  });
  rechargePackagesDirty.value = true;
  rechargePackageEditIndex.value = rechargePackageDrafts.value.length - 1;
}

function removeRechargePackageDraft(index: number) {
  if (typeof window !== 'undefined' && !window.confirm('确认删除这个充值套餐？保存后才会正式生效。')) {
    return;
  }
  rechargePackageDrafts.value.splice(index, 1);
  if (rechargePackageEditIndex.value === index) {
    rechargePackageEditIndex.value = null;
  } else if (rechargePackageEditIndex.value !== null && rechargePackageEditIndex.value > index) {
    rechargePackageEditIndex.value -= 1;
  }
  rechargePackagesDirty.value = true;
}

function moveRechargePackageDraft(fromIndex: number, toIndex: number) {
  if (toIndex < 0 || toIndex >= rechargePackageDrafts.value.length || fromIndex === toIndex) return;
  const [item] = rechargePackageDrafts.value.splice(fromIndex, 1);
  rechargePackageDrafts.value.splice(toIndex, 0, item);
  if (rechargePackageEditIndex.value === fromIndex) {
    rechargePackageEditIndex.value = toIndex;
  } else if (
    rechargePackageEditIndex.value !== null
    && fromIndex < rechargePackageEditIndex.value
    && rechargePackageEditIndex.value <= toIndex
  ) {
    rechargePackageEditIndex.value -= 1;
  } else if (
    rechargePackageEditIndex.value !== null
    && toIndex <= rechargePackageEditIndex.value
    && rechargePackageEditIndex.value < fromIndex
  ) {
    rechargePackageEditIndex.value += 1;
  }
  rechargePackagesDirty.value = true;
}

function openRechargePackageEditor(index: number) {
  rechargePackageEditIndex.value = index;
}

function closeRechargePackageEditor() {
  rechargePackageEditIndex.value = null;
}

function rechargePackageCardLayoutClass(index: number) {
  const count = rechargePackageDrafts.value.length;
  const rowHeightClass = count <= 3 ? 'min-h-[176px]' : 'min-h-[82px]';
  if (count === 5) {
    return `${rowHeightClass} col-span-2 ${index === 3 ? 'col-start-2' : ''}`;
  }
  return rowHeightClass;
}

function rechargePackageAmountClass() {
  return rechargePackageDrafts.value.length <= 3 ? 'text-xl' : 'text-base';
}

function rechargePackagePointsClass() {
  return rechargePackageDrafts.value.length <= 3 ? 'text-base' : 'text-sm';
}

function startRechargePackageDrag(index: number) {
  rechargePackageDragIndex.value = index;
}

function dropRechargePackage(index: number) {
  if (rechargePackageDragIndex.value === null) return;
  moveRechargePackageDraft(rechargePackageDragIndex.value, index);
  rechargePackageDragIndex.value = null;
}

function generatedPackageKey(packageDraft: RechargePackageDraft, index: number, priceCents: number, pointsAmount: number) {
  if (packageDraft.package_key.trim()) return packageDraft.package_key.trim();
  return `pkg_${priceCents}_${pointsAmount}_${index + 1}_${Date.now().toString(36)}`;
}

function buildRechargePackagePayload() {
  if (rechargePackageDrafts.value.length > MAX_RECHARGE_PACKAGE_COUNT) {
    throw new Error(`充值套餐最多只能配置 ${MAX_RECHARGE_PACKAGE_COUNT} 个`);
  }
  return rechargePackageDrafts.value.map((packageDraft, index) => {
    const priceCents = Math.round(Number(packageDraft.price_yuan || 0) * 100);
    const pointsAmount = Math.trunc(Number(packageDraft.points_amount || 0));
    if (!Number.isFinite(priceCents) || priceCents <= 0) {
      throw new Error(`第 ${index + 1} 个套餐的人民币金额必须大于 0`);
    }
    if (!Number.isFinite(pointsAmount) || pointsAmount <= 0) {
      throw new Error(`第 ${index + 1} 个套餐的积分数量必须大于 0`);
    }
    const priceText = (priceCents / 100).toFixed(priceCents % 100 === 0 ? 0 : 2);
    return {
      package_key: generatedPackageKey(packageDraft, index, priceCents, pointsAmount),
      title: `${pointsAmount} 积分`,
      description: `￥${priceText} / ${pointsAmount} 积分`,
      price_cents: priceCents,
      points_amount: pointsAmount,
      bonus_points: 0,
      enabled: packageDraft.enabled,
      sort_order: index,
    };
  });
}

async function saveRechargePackages() {
  let packagesPayload: ReturnType<typeof buildRechargePackagePayload>;
  try {
    packagesPayload = buildRechargePackagePayload();
  } catch (error) {
    globalMessage.value = error instanceof Error ? error.message : '充值套餐配置不合法';
    return;
  }

  const schemaItem = runtimeConfigSchema.value.find((item) => item.config_key === RECHARGE_PACKAGES_CONFIG_KEY);
  const entry: RuntimeConfigEntryUpsertRequest = {
    scope_type: schemaItem?.scope_type || 'global',
    scope_key: schemaItem?.scope_key || 'default',
    config_key: RECHARGE_PACKAGES_CONFIG_KEY,
    value: packagesPayload,
  };

  rechargePackagesSaving.value = true;
  try {
    const result = await updateInternalRuntimeConfig(adminToken.value, [entry]);
    mergeRuntimeConfigEntries(result.items);
    rechargePackageDrafts.value = parsePackageDrafts(packagesPayload);
    rechargePackagesDirty.value = false;
    globalMessage.value = '充值套餐已保存';
  } catch (error) {
    globalMessage.value = resolveError(error);
  } finally {
    rechargePackagesSaving.value = false;
  }
}

function runtimeConfigSchemaItemForKey(configKey: string, fallbackLabel: string): RuntimeConfigSchemaItemResponse {
  const existing = runtimeConfigSchema.value.find((item) => item.config_key === configKey);
  if (existing) return existing;
  return {
    config_key: configKey,
    label: fallbackLabel,
    value_type: 'string',
    default_value: null,
    scope_type: 'global',
    scope_key: 'default',
    group: '系统配置',
    high_risk: false,
    description: null,
  };
}

async function saveCustomerServiceConfig() {
  const editableItems = [
    ...customerServiceBaseConfigItems.value,
    ...customerServiceCopyConfigItems.value,
  ];
  await saveRuntimeConfig(editableItems, '客服配置已保存');
}

function openCustomerServiceQrUploader() {
  customerServiceQrError.value = '';
  customerServiceQrInputRef.value?.click();
}

async function handleCustomerServiceQrFileChange(event: Event) {
  if (customerServiceQrUploading.value) return;
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  input.value = '';
  if (!file) return;
  if (!/^image\/(jpeg|png|webp)$/u.test(file.type)) {
    customerServiceQrError.value = '请上传 JPG、PNG 或 WebP 格式的客服二维码。';
    return;
  }
  if (file.size > 1_500_000) {
    customerServiceQrError.value = '客服二维码文件请控制在 1.5MB 以内。';
    return;
  }

  customerServiceQrUploading.value = true;
  customerServiceQrError.value = '';
  try {
    const imageDataUrl = await readFileAsDataUrl(file);
    const entry = await uploadInternalCustomerServiceQrCode(adminToken.value, {image_data_url: imageDataUrl});
    mergeRuntimeConfigEntries([entry]);
    globalMessage.value = '客服二维码已上传';
  } catch (error) {
    customerServiceQrError.value = resolveError(error);
  } finally {
    customerServiceQrUploading.value = false;
  }
}

async function deleteCustomerServiceQrCode() {
  if (
    customerServiceQrPreviewUrl.value
    && typeof window !== 'undefined'
    && !window.confirm('确认删除当前客服二维码？删除后前台将展示未配置占位。')
  ) {
    return;
  }
  customerServiceQrDeleting.value = true;
  customerServiceQrError.value = '';
  try {
    const entry = await deleteInternalCustomerServiceQrCode(adminToken.value);
    mergeRuntimeConfigEntries([entry]);
    globalMessage.value = '客服二维码已删除';
  } catch (error) {
    customerServiceQrError.value = resolveError(error);
  } finally {
    customerServiceQrDeleting.value = false;
  }
}

function readFileAsDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = () => reject(new Error('图片读取失败，请重新选择文件。'));
    reader.onload = () => resolve(String(reader.result || ''));
    reader.readAsDataURL(file);
  });
}

function beginCreateLlmKey() {
  llmKeyFormMode.value = 'create';
  llmEditingKeyId.value = '';
  llmKeyForm.value = {
    provider: 'deepseek',
    model: 'deepseek-v4-pro',
    display_name: 'DeepSeek 主模型 Key',
    secret_value: '',
    enabled: true,
    priority: 100,
    max_concurrency: 450,
    cooldown_seconds: 60,
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
    secret_value: '',
    enabled: item.enabled,
    priority: item.priority,
    max_concurrency: item.max_concurrency || 450,
    cooldown_seconds: item.cooldown_seconds || 60,
    remark: item.remark || '',
    last_operator: item.last_operator || 'internal_admin',
  };
}

function handleServiceKeyProviderChange(value: string | number | boolean | null) {
  const provider = String(value || 'deepseek');
  const presets = serviceKeyPresetMap[provider] || serviceKeyPresetMap.deepseek;
  const firstPreset = presets[0];
  llmKeyForm.value.provider = provider;
  llmKeyForm.value.model = firstPreset.value;
  llmKeyForm.value.display_name = firstPreset.defaultName;
}

function handleServiceKeyModelChange(value: string | number | boolean | null) {
  const model = String(value || '');
  const preset = activeServiceKeyPresetOptions.value.find((item) => item.value === model);
  llmKeyForm.value.model = model;
  if (preset && (!llmKeyForm.value.display_name || llmKeyFormMode.value === 'create')) {
    llmKeyForm.value.display_name = preset.defaultName;
  }
}

function serviceKeyProviderLabel(provider: string) {
  return serviceKeyProviderSelectOptions.find((item) => item.value === provider)?.label || provider;
}

function serviceKeyModelLabel(provider: string, model: string) {
  return (serviceKeyPresetMap[provider] || []).find((item) => item.value === model)?.label || model;
}

function llmKeyRuntimeLabel(item: LlmApiKeyResponse) {
  if (!item.enabled) return '停用';
  if (item.cooldown_until) return '冷却中';
  if (item.current_inflight >= item.max_concurrency) return '已满';
  if (item.last_error_message) return '有错误';
  return item.priority <= 100 ? '主 Key' : '备用 Key';
}

function llmKeyRuntimeClass(item: LlmApiKeyResponse) {
  if (!item.enabled) return 'bg-gray-50 text-gray-500 border-gray-100';
  if (item.cooldown_until) return 'bg-amber-50 text-amber-700 border-amber-100';
  if (item.current_inflight >= item.max_concurrency) return 'bg-red-50 text-red-600 border-red-100';
  if (item.last_error_message) return 'bg-orange-50 text-orange-700 border-orange-100';
  return item.priority <= 100 ? 'bg-emerald-50 text-emerald-600 border-emerald-100' : 'bg-blue-50 text-blue-600 border-blue-100';
}

async function submitLlmKeyForm() {
  if (llmKeyFormMode.value === 'create' && !String(llmKeyForm.value.secret_value || '').trim()) {
    globalMessage.value = '请填写真实 Key，保存后系统只展示脱敏值';
    return;
  }
  if (Number(llmKeyForm.value.max_concurrency || 0) > 450 && typeof window !== 'undefined') {
    const confirmed = window.confirm('该 Key 并发上限超过 450，请确认 DeepSeek 侧已扩容。继续保存？');
    if (!confirmed) return;
  }
  llmLoading.value = true;
  try {
    if (llmKeyFormMode.value === 'edit' && llmEditingKeyId.value) {
      await updateInternalLlmApiKey(adminToken.value, llmEditingKeyId.value, llmKeyForm.value);
    } else {
      await createInternalLlmApiKey(adminToken.value, llmKeyForm.value);
    }
    llmKeyFormMode.value = null;
    llmEditingKeyId.value = '';
    await Promise.allSettled([loadLlmKeys(), loadLlmConcurrency()]);
  } catch (error) {
    globalMessage.value = resolveError(error);
  } finally {
    llmLoading.value = false;
  }
}

async function removeLlmKey(keyId: string) {
  if (typeof window !== 'undefined' && !window.confirm('确认删除该服务密钥配置？')) return;
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

function canManualCompleteOrder(order: RechargeOrderResponse) {
  return order.status === 'unpaid' || order.raw_status === 'pending';
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

function formatPercent(value: number | null | undefined) {
  if (value === null || value === undefined || !Number.isFinite(Number(value))) {
    return '0%';
  }
  return `${Number(value).toFixed(1)}%`;
}

function formatDuration(seconds: number | null | undefined) {
  if (seconds === null || seconds === undefined || !Number.isFinite(Number(seconds))) {
    return '--';
  }
  const normalizedSeconds = Math.max(0, Math.round(Number(seconds)));
  if (normalizedSeconds < 60) {
    return `${normalizedSeconds}s`;
  }
  const minutes = Math.floor(normalizedSeconds / 60);
  const restSeconds = normalizedSeconds % 60;
  return `${minutes}m ${restSeconds}s`;
}

function genderLabel(gender: string | null | undefined) {
  if (gender === 'male') return '男';
  if (gender === 'female') return '女';
  return gender || '--';
}

function reviewStatusLabel(status: string) {
  const map: Record<string, string> = {
    processing: '生成中',
    completed: '已完成',
    failed: '生成失败',
  };
  return map[status] || status;
}

function voiceSceneLabel(record: UsageRecordResponse) {
  const result = record.result_summary || {};
  const request = record.request_payload_summary || {};
  const scene = String(result.scene || request.scene || '');
  const aspectKey = String(result.aspect_key || request.aspect_key || '');
  if (scene === 'phone_summary') return '听综评';
  if (scene === 'phone_stability') return '听建议';
  if (scene === 'phone_aspect') return `听${aspectLabel(aspectKey)}`;
  return record.feature_name || '语音播报';
}

function usageSummaryValue(record: UsageRecordResponse, key: string) {
  const result = record.result_summary || {};
  const request = record.request_payload_summary || {};
  return result[key] ?? request[key];
}

function displayUnknownValue(value: unknown) {
  if (value === null || value === undefined || value === '') return '--';
  if (typeof value === 'boolean') return value ? '是' : '否';
  if (typeof value === 'string' || typeof value === 'number') return String(value);
  return JSON.stringify(value);
}

function voiceRecordField(record: UsageRecordResponse, key: string) {
  return displayUnknownValue(usageSummaryValue(record, key));
}

function voiceCachedLabel(record: UsageRecordResponse) {
  const value = usageSummaryValue(record, 'cached');
  if (value === true || value === 'true') return '命中缓存';
  if (value === false || value === 'false') return '未命中';
  return '--';
}

function voiceFailureText(record: UsageRecordResponse) {
  const keys = ['failure_reason', 'error_message', 'error', 'detail'];
  for (const key of keys) {
    const value = usageSummaryValue(record, key);
    if (value) return displayUnknownValue(value);
  }
  return '--';
}

function aspectLabel(aspectKey: string | null | undefined) {
  const map: Record<string, string> = {
    career: '事业',
    wealth: '财富',
    love: '感情',
    health: '健康',
    acad: '学业',
    fortune: '运势',
    investment: '投资',
    travel: '出行',
    social: '社交',
    family: '家庭',
    personality: '性格',
    fengshui: '风水',
  };
  return map[aspectKey || ''] || aspectKey || '--';
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

function pointsClaimStatusLabel(status: string | null | undefined) {
  const map: Record<string, string> = {
    active: '有效',
    expired: '已过期',
    disabled: '停用',
    not_started: '未开始',
    granted: '成功领取',
    already_claimed_this_week: '本周重复',
  };
  return map[status || ''] || status || '--';
}

function pointsClaimStatusClass(status: string | null | undefined) {
  if (status === 'active' || status === 'granted') return 'bg-emerald-50 text-emerald-600 border-emerald-100';
  if (status === 'already_claimed_this_week') return 'bg-amber-50 text-amber-700 border-amber-100';
  if (status === 'disabled') return 'bg-red-50 text-red-600 border-red-100';
  if (status === 'expired') return 'bg-gray-50 text-gray-500 border-gray-200';
  if (status === 'not_started') return 'bg-blue-50 text-blue-600 border-blue-100';
  return 'bg-slate-50 text-slate-500 border-slate-200';
}

function pointsClaimRecordFailureLabel(record: PointsClaimRecordResponse) {
  if (record.status === 'granted') return '已发放到账';
  if (record.status === 'already_claimed_this_week') return '本周已领取过免费积分';
  if (record.failure_reason === 'claim_link_expired' || record.status === 'expired') return '访问时链接已过期';
  if (record.failure_reason === 'claim_link_disabled' || record.status === 'disabled') return '访问时链接已停用';
  if (record.failure_reason === 'claim_link_not_started' || record.status === 'not_started') return '访问时链接未生效';
  return record.failure_reason || '--';
}

function formatClaimMoney(cents: number | null | undefined) {
  return formatAmount(Number(cents || 0));
}

function formatClaimDuration(hours: number | null | undefined) {
  const normalizedHours = Math.trunc(Number(hours || 0));
  if (!Number.isFinite(normalizedHours) || normalizedHours <= 0) return '--';
  if (normalizedHours % 24 === 0) {
    return `${normalizedHours / 24} 天`;
  }
  return `${normalizedHours} 小时`;
}

function formatClaimUrl(link: PointsClaimLinkResponse | null | undefined) {
  if (!link?.claim_url) return '';
  if (/^https?:\/\//i.test(link.claim_url)) return link.claim_url;
  if (typeof window === 'undefined') return link.claim_url;
  return `${window.location.origin}${link.claim_url.startsWith('/') ? link.claim_url : `/${link.claim_url}`}`;
}

function userStatusLabel(status: string) {
  const map: Record<string, string> = {
    active: '正常活动中',
    disabled: '已禁用',
  };
  return map[status] || status;
}

function identityLabel(identity: string | null | undefined) {
  const map: Record<string, string> = {
    normal_user: '普通会员',
    promoter: '推广大使',
    promotion_ambassador: '推广大使',
    vip_promoter: 'VIP 推广大使',
    vip_promotion_ambassador: 'VIP 推广大使',
    senior_promoter: 'VIP 推广大使',
    senior_promotion_ambassador: 'VIP 推广大使',
    svip_promoter: 'SVIP 推广大使',
    svip_promotion_ambassador: 'SVIP 推广大使',
  };
  return map[identity || ''] || identity || '--';
}

function identitySourceLabel(identityType: string | null | undefined) {
  const map: Record<string, string> = {
    phone: '手机号',
    wechat_unionid: '微信 UnionID',
    wechat_pending_unionid: '微信待补 UnionID',
    session: '待绑定',
    unknown: '待绑定',
  };
  return map[identityType || 'unknown'] || identityType || '待绑定';
}

function userPrimaryIdentityLine(user: InternalUserResponse) {
  return user.primary_phone || user.primary_unionid || (user.uid ? `UID ${user.uid}` : user.user_id);
}

function selectedUserIdentityValue() {
  const user = selectedUser.value?.user;
  if (!user) return '--';
  return user.primary_unionid || '--';
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

async function copyTextToClipboard(text: string): Promise<void> {
  if (typeof navigator !== 'undefined' && navigator.clipboard?.writeText && window.isSecureContext) {
    await navigator.clipboard.writeText(text);
    return;
  }

  if (typeof document === 'undefined') {
    throw new Error('copy_unavailable');
  }

  const input = document.createElement('textarea');
  input.value = text;
  input.setAttribute('readonly', 'true');
  input.style.position = 'fixed';
  input.style.left = '-9999px';
  input.style.top = '0';
  input.style.opacity = '0';
  document.body.appendChild(input);
  input.focus();
  input.select();
  input.setSelectionRange(0, input.value.length);

  try {
    if (!document.execCommand('copy')) {
      throw new Error('copy_failed');
    }
  } finally {
    document.body.removeChild(input);
  }
}

async function copyText(value: string | null | undefined, label = '内容') {
  const text = String(value || '').trim();
  if (!text) return;
  try {
    await copyTextToClipboard(text);
    globalMessage.value = `${label}已复制`;
  } catch {
    globalMessage.value = `${label}复制失败，请长按链接手动复制`;
  }
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

            <div v-if="settingsNavItem" class="block">
              <button
                @click="toggleSettingsPrimary"
                class="w-full flex items-center justify-between p-3 rounded-lg text-xs font-bold transition-all outline-none cursor-pointer"
                :class="activePrimary === 'settings' ? 'bg-brand-paper border-l-4 border-brand-primary text-brand-primary' : 'text-brand-ink/70 hover:bg-brand-paper hover:text-brand-ink-strong'"
              >
                <div class="flex items-center gap-2.5">
                  <Settings :size="15" />
                  <span>6. {{ settingsNavItem.label }}</span>
                </div>
                <span class="text-[9px] font-mono select-none text-brand-secondary">{{ isSettingsMenuOpen ? '▼' : '▶' }}</span>
              </button>

              <div v-show="isSettingsMenuOpen" class="pl-3.5 pr-1 py-1 space-y-1 block ml-4 border-l border-gray-100">
                <button
                  v-for="(item, index) in settingsNavItems"
                  :key="item.key"
                  @click="selectSettings(item.key)"
                  class="w-full flex items-center justify-between px-2 py-1.5 rounded-md text-[10.5px] font-semibold transition-all outline-none cursor-pointer"
                  :class="activePrimary === 'settings' && activeSettings === item.key ? 'bg-brand-paper/80 text-brand-primary font-bold' : 'text-brand-ink/60 hover:text-brand-ink-strong hover:bg-brand-paper/30'"
                >
                  <div class="flex items-center gap-2">
                    <component :is="settingsNavIcons[item.key]" :size="13" />
                    <span>6.{{ index + 1 }} {{ item.label }}</span>
                  </div>
                </button>
              </div>
            </div>
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
                      placeholder="按 UID、昵称、手机号或 UnionID 检索..."
                      @keyup.enter="searchUsers"
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
                  <button @click="searchUsers" class="bg-brand-primary text-white px-4 py-2 rounded-xl text-xs font-bold hover:bg-brand-primary-strong transition-colors outline-none cursor-pointer">
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
                      <th class="p-3 w-[15%] font-mono">UID / 状态</th>
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
                          <div class="relative w-7 h-7 shrink-0 bg-brand-primary/10 text-brand-primary font-serif font-bold flex items-center justify-center rounded-lg text-xs overflow-hidden">
                            <span>{{ userAvatarInitial(user) }}</span>
                            <img
                              v-if="userAvatarUrl(user)"
                              :src="userAvatarUrl(user)"
                              alt=""
                              class="absolute inset-0 w-full h-full object-cover"
                              @error="handleUserAvatarError"
                            />
                          </div>
                          <div class="min-w-0">
                            <div class="font-bold text-brand-ink-strong truncate">{{ user.nickname || '未命名用户' }}</div>
                            <div class="text-[10px] text-brand-secondary font-mono truncate">{{ user.registered_channel || '--' }}</div>
                          </div>
                        </div>
                      </td>
                      <td class="p-3 font-mono min-w-0">
                        <span class="text-brand-ink-strong block truncate" :title="user.user_id">{{ user.uid ? `UID ${user.uid}` : shortText(user.user_id, 10, 6) }}</span>
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

              <div class="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-gray-100 text-xs text-brand-secondary">
                <div class="font-mono">
                  显示 {{ userPageStart }}-{{ userPageEnd }} / {{ userTotal }}，每页 {{ userPageSize }} 条
                </div>
                <div class="flex items-center gap-2">
                  <button
                    @click="changeUserPage(-1)"
                    :disabled="!canGoPrevUserPage"
                    class="bg-white border border-gray-100 text-brand-ink-strong px-3 py-1.5 rounded-lg text-[10.5px] font-bold disabled:opacity-40 disabled:cursor-not-allowed hover:bg-brand-paper"
                  >
                    上一页
                  </button>
                  <span class="font-mono text-[11px] text-brand-secondary px-2">
                    第 {{ userCurrentPage }} / {{ userTotalPages }} 页
                  </span>
                  <button
                    @click="changeUserPage(1)"
                    :disabled="!canGoNextUserPage"
                    class="bg-white border border-gray-100 text-brand-ink-strong px-3 py-1.5 rounded-lg text-[10.5px] font-bold disabled:opacity-40 disabled:cursor-not-allowed hover:bg-brand-paper"
                  >
                    下一页
                  </button>
                </div>
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

          <div v-else-if="activePrimary === 'features' && activeFeature === 'points-claim'" class="space-y-6 text-left animate-fade-in">
            <div class="bg-white border border-gray-100 rounded-2xl p-6 space-y-6 shadow-sm">
              <div class="flex flex-wrap justify-between items-start gap-4 pb-4 border-b border-gray-100">
                <div class="space-y-0.5 block">
                  <h3 class="font-serif text-lg font-bold text-brand-primary flex items-center gap-2">
                    <Gift :size="20" />
                    <span>积分领取</span>
                  </h3>
                  <p class="text-xs text-brand-secondary">创建运营临时链接，按自然周限制用户成功领取次数，并保留重复访问记录。</p>
                </div>
                <button
                  @click="loadPointsClaimLinks"
                  class="bg-brand-primary hover:bg-brand-primary-strong text-white px-5 py-2 rounded-xl text-xs font-bold transition-all outline-none cursor-pointer shadow-sm shadow-brand-primary/10 flex items-center gap-1.5"
                >
                  {{ pointsClaimLoading ? '刷新中...' : '刷新链接' }}
                </button>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
                <div v-for="item in pointsClaimCards" :key="item.label" class="bg-brand-paper/45 border border-gray-100 rounded-xl p-4">
                  <div class="text-[10px] text-brand-secondary">{{ item.label }}</div>
                  <div class="text-xl font-bold font-mono mt-1 text-brand-ink-strong">{{ item.value }}</div>
                  <div class="text-[10px] text-brand-secondary">{{ item.sub }}</div>
                </div>
              </div>

              <div class="grid grid-cols-1 xl:grid-cols-[minmax(260px,0.3fr)_minmax(0,0.7fr)] gap-4 items-start">
                <section class="bg-brand-paper/35 border border-gray-100 rounded-2xl p-4 space-y-3">
                  <div class="flex items-center justify-between gap-3">
                    <div>
                      <h4 class="font-serif text-sm font-bold text-brand-ink-strong">生成临时领取链接</h4>
                    </div>
                    <span class="rounded-full bg-emerald-50 border border-emerald-100 px-2 py-0.5 text-[9.5px] font-bold text-emerald-700">周限 1 次</span>
                  </div>

                  <div class="grid grid-cols-1 gap-2.5 text-xs">
                    <label class="space-y-1.5 block">
                      <span class="text-[10.5px] font-bold text-brand-secondary">链接名称</span>
                      <input
                        v-model="pointsClaimForm.title"
                        type="text"
                        maxlength="128"
                        class="w-full bg-white border border-gray-100 rounded-lg px-2.5 py-2 text-xs text-brand-ink-strong outline-none focus:border-brand-primary"
                        placeholder="如：端午客服福利 500 积分"
                      />
                    </label>
                    <div class="grid grid-cols-2 gap-2">
                      <label class="space-y-1.5 block">
                        <span class="text-[10.5px] font-bold text-brand-secondary">领取积分</span>
                        <input
                          v-model.number="pointsClaimForm.points_amount"
                          type="number"
                          min="1"
                          step="1"
                          class="w-full bg-white border border-gray-100 rounded-lg px-2.5 py-2 text-xs font-mono text-brand-ink-strong outline-none focus:border-brand-primary"
                        />
                      </label>
                      <label class="space-y-1.5 block">
                        <span class="text-[10.5px] font-bold text-brand-secondary">人民币价值</span>
                        <input
                          v-model.number="pointsClaimForm.display_value_yuan"
                          type="number"
                          min="0"
                          step="0.01"
                          class="w-full bg-white border border-gray-100 rounded-lg px-2.5 py-2 text-xs font-mono text-brand-ink-strong outline-none focus:border-brand-primary"
                          placeholder="0.00"
                        />
                      </label>
                    </div>
                    <label class="space-y-1.5 block">
                      <span class="text-[10.5px] font-bold text-brand-secondary">有效期</span>
                      <div class="grid grid-cols-[minmax(0,1fr)_auto] gap-2">
                        <input
                          v-model.number="pointsClaimForm.expires_value"
                          type="number"
                          min="1"
                          :max="pointsClaimForm.expires_unit === 'days' ? 30 : 720"
                          step="1"
                          class="w-full bg-white border border-gray-100 rounded-lg px-2.5 py-2 text-xs font-mono text-brand-ink-strong outline-none focus:border-brand-primary"
                          :placeholder="pointsClaimForm.expires_unit === 'days' ? '最多 30' : '最多 720'"
                        />
                        <div class="grid grid-cols-2 gap-1 rounded-lg border border-gray-100 bg-white p-1">
                          <button
                            type="button"
                            @click="pointsClaimForm.expires_unit = 'hours'"
                            class="px-3 py-1.5 rounded-md text-[10.5px] font-bold transition-colors"
                            :class="pointsClaimForm.expires_unit === 'hours' ? 'bg-brand-primary text-white shadow-sm shadow-brand-primary/10' : 'text-brand-secondary hover:bg-brand-paper'"
                          >
                            小时
                          </button>
                          <button
                            type="button"
                            @click="pointsClaimForm.expires_unit = 'days'"
                            class="px-3 py-1.5 rounded-md text-[10.5px] font-bold transition-colors"
                            :class="pointsClaimForm.expires_unit === 'days' ? 'bg-brand-primary text-white shadow-sm shadow-brand-primary/10' : 'text-brand-secondary hover:bg-brand-paper'"
                          >
                            天
                          </button>
                        </div>
                      </div>
                      <span class="block text-[10px] text-brand-secondary">最多 30 天。</span>
                    </label>
                    <label class="space-y-1.5 block">
                      <span class="text-[10.5px] font-bold text-brand-secondary">内部备注</span>
                      <textarea
                        v-model="pointsClaimForm.operator_note"
                        maxlength="512"
                        class="w-full bg-white border border-gray-100 rounded-lg px-2.5 py-2 text-xs text-brand-ink-strong outline-none focus:border-brand-primary min-h-14"
                        placeholder="批次或渠道，可选"
                      ></textarea>
                    </label>
                  </div>

                  <div v-if="pointsClaimError" class="text-xs text-red-600 bg-red-50 border border-red-100 rounded-xl px-3 py-2">
                    {{ pointsClaimError }}
                  </div>

                  <button
                    @click="createPointsClaimLink"
                    :disabled="pointsClaimCreating"
                    class="w-full bg-brand-primary hover:bg-brand-primary-strong text-white px-5 py-2.5 rounded-xl text-xs font-bold transition-all outline-none cursor-pointer shadow-sm shadow-brand-primary/10 disabled:opacity-60 disabled:cursor-not-allowed"
                  >
                    {{ pointsClaimCreating ? '生成中...' : '生成领取链接' }}
                  </button>

                  <div v-if="latestCreatedPointsClaimLink" class="bg-white border border-emerald-100 rounded-xl p-3 space-y-2">
                    <div class="flex items-center justify-between gap-3">
                      <span class="text-xs font-bold text-emerald-700 flex items-center gap-1.5">
                        <CheckCircle2 :size="14" />
                        <span>最新链接已生成</span>
                      </span>
                      <span class="text-[10px] text-brand-secondary font-mono">{{ formatTime(latestCreatedPointsClaimLink.expires_at) }}</span>
                    </div>
                    <p class="font-mono text-[10.5px] text-brand-ink-strong break-all select-all">{{ formatClaimUrl(latestCreatedPointsClaimLink) }}</p>
                    <div class="flex flex-wrap gap-2">
                      <button @click="copyText(formatClaimUrl(latestCreatedPointsClaimLink), '领取链接')" class="bg-brand-primary text-white px-3 py-1.5 rounded-lg text-[10.5px] font-bold flex items-center gap-1.5">
                        <Copy :size="12" />
                        <span>复制链接</span>
                      </button>
                      <a :href="formatClaimUrl(latestCreatedPointsClaimLink)" target="_blank" rel="noreferrer" class="bg-white border border-gray-100 text-brand-primary px-3 py-1.5 rounded-lg text-[10.5px] font-bold flex items-center gap-1.5">
                        <ExternalLink :size="12" />
                        <span>打开预览</span>
                      </a>
                    </div>
                  </div>
                </section>

                <section class="bg-white border border-gray-100 rounded-2xl p-5 space-y-4">
                  <div class="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <h4 class="font-serif text-base font-bold text-brand-ink-strong">领取链接列表</h4>
                      <p class="text-[11.5px] text-brand-secondary">成功领取、重复访问和链接生命周期在这里追踪。</p>
                    </div>
                    <div class="flex flex-wrap items-center gap-2">
                      <input v-model="pointsClaimFilters.keyword" class="bg-gray-50 border border-gray-100 p-2.5 rounded-lg text-xs text-brand-ink-strong outline-none focus:border-brand-primary w-56" placeholder="名称 / 链接码 / ID" />
                      <AdminSelect
                        v-model="pointsClaimFilters.status"
                        :options="pointsClaimStatusSelectOptions"
                        min-width-class="min-w-[132px]"
                        panel-width-class="w-40"
                      />
                    </div>
                  </div>

                  <div class="flex flex-wrap justify-end gap-2">
                    <button @click="resetPointsClaimFilters(); loadPointsClaimLinks({resetPage: true})" class="bg-white border border-gray-100 text-brand-secondary px-4 py-2 rounded-xl text-xs font-bold hover:bg-gray-50">
                      重置
                    </button>
                    <button @click="searchPointsClaimLinks" class="bg-brand-primary text-white px-4 py-2 rounded-xl text-xs font-bold hover:bg-brand-primary-strong">
                      {{ pointsClaimLoading ? '查询中...' : '查询链接' }}
                    </button>
                  </div>

                  <div v-if="pointsClaimError" class="text-xs text-red-600 bg-red-50 border border-red-100 rounded-xl px-3 py-2">
                    {{ pointsClaimError }}
                  </div>

                  <div class="overflow-x-auto border border-gray-100 rounded-xl bg-white">
                    <table class="w-full table-fixed text-xs font-sans text-left">
                      <colgroup>
                        <col class="w-[220px]" />
                        <col class="w-[92px]" />
                        <col class="w-[56px]" />
                        <col class="w-[72px]" />
                        <col class="w-[72px]" />
                        <col class="w-[132px]" />
                        <col class="w-[132px]" />
                        <col class="w-[172px]" />
                      </colgroup>
                      <thead>
                        <tr class="bg-gray-50 border-b border-gray-100 text-brand-secondary uppercase font-mono text-[10px] tracking-wider">
                          <th class="px-3 py-2.5">链接</th>
                          <th class="px-3 py-2.5">额度</th>
                          <th class="px-3 py-2.5">状态</th>
                          <th class="px-3 py-2.5 text-right">已领</th>
                          <th class="px-3 py-2.5 text-right">重复</th>
                          <th class="px-3 py-2.5">创建时间</th>
                          <th class="px-3 py-2.5">过期时间</th>
                          <th class="px-3 py-2.5 text-right">操作</th>
                        </tr>
                      </thead>
                      <tbody class="divide-y divide-gray-100">
                        <tr v-for="item in pointsClaimLinks" :key="item.claim_link_id" class="hover:bg-brand-paper/50">
                          <td class="px-3 py-2.5 align-top">
                            <div class="font-bold text-brand-ink-strong leading-snug break-words" :title="item.title">{{ item.title }}</div>
                            <div class="text-[10px] text-brand-secondary font-mono break-all" :title="item.claim_code">{{ shortText(item.claim_code, 8, 5) }}</div>
                          </td>
                          <td class="px-3 py-2.5 align-top">
                            <div class="font-mono text-brand-primary font-bold">{{ item.points_amount }} pt</div>
                            <div class="text-[10px] text-brand-secondary font-mono">{{ formatClaimMoney(item.display_value_cents) }}</div>
                          </td>
                          <td class="px-3 py-2.5 align-top">
                            <span class="px-2 py-0.5 rounded text-[9px] font-bold inline-block border" :class="pointsClaimStatusClass(item.effective_status)">
                              {{ pointsClaimStatusLabel(item.effective_status) }}
                            </span>
                          </td>
                          <td class="px-3 py-2.5 align-top text-right font-mono text-emerald-600 font-bold">
                            {{ item.claimed_user_count }} 人
                          </td>
                          <td class="px-3 py-2.5 align-top text-right font-mono text-amber-700 font-bold">
                            {{ item.duplicate_attempt_count }} 次
                          </td>
                          <td class="px-3 py-2.5 align-top font-mono text-brand-secondary">{{ formatTime(item.created_at) }}</td>
                          <td class="px-3 py-2.5 align-top font-mono text-brand-secondary">{{ formatTime(item.expires_at) }}</td>
                          <td class="px-3 py-2.5 align-top">
                            <div class="flex justify-end gap-1.5 whitespace-nowrap">
                              <button @click="copyText(formatClaimUrl(item), '领取链接')" class="bg-white border border-gray-100 text-brand-primary px-2.5 py-1.5 rounded-lg text-[10px] font-bold inline-flex items-center gap-1">
                                <Copy :size="11" />
                                <span>复制</span>
                              </button>
                              <button @click="openPointsClaimLink(item)" class="bg-brand-primary text-white px-2.5 py-1.5 rounded-lg text-[10px] font-bold">记录</button>
                              <button
                                v-if="item.effective_status !== 'disabled'"
                                @click="disablePointsClaimLink(item)"
                                class="bg-red-50 border border-red-100 text-red-600 px-2.5 py-1.5 rounded-lg text-[10px] font-bold"
                              >
                                停用
                              </button>
                            </div>
                          </td>
                        </tr>
                        <tr v-if="!pointsClaimLoading && pointsClaimLinks.length === 0">
                          <td colspan="8" class="p-8 text-center text-brand-secondary font-mono">暂无积分领取链接</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>

                  <div class="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-gray-100 text-xs text-brand-secondary">
                    <div class="font-mono">
                      显示 {{ pointsClaimPageStart }}-{{ pointsClaimPageEnd }} / {{ pointsClaimTotal }}，每页 {{ pointsClaimPageSize }} 条
                    </div>
                    <div class="flex items-center gap-2">
                      <button
                        @click="changePointsClaimPage(-1)"
                        :disabled="!canGoPrevPointsClaimPage"
                        class="bg-white border border-gray-100 text-brand-ink-strong px-3 py-1.5 rounded-lg text-[10.5px] font-bold disabled:opacity-40 disabled:cursor-not-allowed hover:bg-brand-paper"
                      >
                        上一页
                      </button>
                      <span class="font-mono text-[11px] text-brand-secondary px-2">
                        第 {{ pointsClaimCurrentPage }} / {{ pointsClaimTotalPages }} 页
                      </span>
                      <button
                        @click="changePointsClaimPage(1)"
                        :disabled="!canGoNextPointsClaimPage"
                        class="bg-white border border-gray-100 text-brand-ink-strong px-3 py-1.5 rounded-lg text-[10.5px] font-bold disabled:opacity-40 disabled:cursor-not-allowed hover:bg-brand-paper"
                      >
                        下一页
                      </button>
                    </div>
                  </div>
                </section>
              </div>
            </div>
          </div>

          <div v-else-if="activePrimary === 'features'" class="space-y-6 text-left animate-fade-in">
            <div class="bg-white border border-gray-100 rounded-2xl p-6 space-y-6 shadow-sm">
              <div class="flex justify-between items-center pb-4 border-b border-gray-100">
                <div class="space-y-0.5 block">
                  <h3 class="font-serif text-lg font-bold text-brand-primary flex items-center gap-2">
                    <Smartphone :size="20" />
                    <span>{{ activeFeatureDisplayName }}配置</span>
                  </h3>
                  <p class="text-xs text-brand-secondary">{{ activeFeatureDescriptionText }}</p>
                </div>
                <button
                  @click="refreshPhoneQimenPage"
                  class="bg-brand-primary hover:bg-brand-primary-strong text-white px-5 py-2 rounded-xl text-xs font-bold transition-all outline-none cursor-pointer shadow-sm shadow-brand-primary/10 flex items-center gap-1.5"
                >
                  {{ phoneReviewLoading || phoneQimenSummaryLoading ? '刷新中...' : '刷新评测数据' }}
                </button>
              </div>

              <div class="grid grid-cols-1 xl:grid-cols-[minmax(0,1.2fr)_minmax(360px,0.8fr)] gap-5 items-stretch">
                <section class="h-full bg-brand-paper/35 border border-gray-100 rounded-2xl p-5 space-y-4">
                  <div v-if="activeFeature === 'phone-review'" class="flex items-center justify-between gap-3">
                    <div>
                      <h4 class="font-serif text-base font-bold text-brand-ink-strong">手机号评测数据大盘</h4>
                      <p class="text-[11.5px] text-brand-secondary">以评测主记录为统计口径，专项解锁和语音播报只作为关联指标。</p>
                    </div>
                    <span class="text-[10px] text-brand-secondary font-mono">{{ formatTime(phoneQimenSummary?.generated_at) }}</span>
                  </div>
                  <div v-if="activeFeature === 'phone-review' && phoneQimenSummaryError" class="text-xs text-red-600 bg-red-50 border border-red-100 rounded-xl px-3 py-2">
                    {{ phoneQimenSummaryError }}
                  </div>
                  <div v-if="activeFeature === 'phone-review'" class="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div v-for="item in phoneQimenSummaryCards" :key="item.label" class="bg-white border border-gray-100 rounded-xl p-3">
                      <div class="text-[10px] text-brand-secondary">{{ item.label }}</div>
                      <div class="text-lg font-bold font-mono mt-1" :class="item.tone">{{ item.value }}</div>
                      <div class="text-[10px] text-brand-secondary">{{ item.sub }}</div>
                    </div>
                  </div>
                  <div v-if="activeFeature !== 'phone-review'" class="h-full min-h-[196px] flex flex-col justify-center gap-3">
                    <div class="w-10 h-10 rounded-xl bg-brand-primary/10 text-brand-primary flex items-center justify-center">
                      <Calendar :size="20" />
                    </div>
                    <div>
                      <h4 class="font-serif text-base font-bold text-brand-ink-strong">四柱八字评测</h4>
                      <p class="text-[11.5px] text-brand-secondary mt-1 leading-relaxed">
                        公开与内部接口已接入，运营记录可在下方使用记录中筛选“四柱八字”和“四柱专项解锁”。
                      </p>
                    </div>
                  </div>
                </section>

                <section class="h-full bg-white border border-gray-100 rounded-2xl p-5 space-y-4">
                  <div class="flex items-center justify-between gap-3">
                    <div>
                      <h4 class="font-serif text-base font-bold text-brand-ink-strong">{{ activeFeatureDisplayName }}配置</h4>
                      <p class="text-[11.5px] text-brand-secondary">{{ activeFeatureDescriptionText }}</p>
                    </div>
                    <button
                      @click="saveRuntimeConfig(featureConfigItems, `${activeFeatureDisplayName}配置已保存`)"
                      class="bg-brand-primary hover:bg-brand-primary-strong text-white px-5 py-2.5 rounded-xl text-xs font-bold transition-all outline-none cursor-pointer shadow-sm shadow-brand-primary/10"
                    >
                      {{ runtimeConfigLoading ? '保存中...' : '保存配置' }}
                    </button>
                  </div>

                  <div v-if="featureConfigItems.length" class="space-y-3">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <label v-if="phoneReviewBaseCostItem" class="bg-brand-paper/40 border border-gray-100 rounded-xl px-3.5 py-3 space-y-1.5 block">
                        <span class="text-[10.5px] font-bold text-brand-secondary">{{ phoneReviewBaseCostItem.label }}</span>
                        <input
                          v-model="runtimeConfigDrafts[phoneReviewBaseCostItem.config_key]"
                          @input="runtimeConfigDirty = true"
                          type="number"
                          class="w-full bg-white border border-gray-100 rounded-lg px-2.5 py-2 text-xs font-mono outline-none focus:border-brand-primary"
                          :placeholder="String(phoneReviewBaseCostItem.default_value ?? '')"
                        />
                        <span class="block text-[10px] text-brand-secondary font-mono">{{ phoneReviewBaseCostItem.config_key }}</span>
                      </label>

                      <label v-if="phoneReviewAspectUnlockCostItem" class="bg-brand-paper/40 border border-gray-100 rounded-xl px-3.5 py-3 space-y-1.5 block">
                        <span class="text-[10.5px] font-bold text-brand-secondary">{{ phoneReviewAspectUnlockCostItem.label }}</span>
                        <input
                          v-model="runtimeConfigDrafts[phoneReviewAspectUnlockCostItem.config_key]"
                          @input="runtimeConfigDirty = true"
                          type="number"
                          class="w-full bg-white border border-gray-100 rounded-lg px-2.5 py-2 text-xs font-mono outline-none focus:border-brand-primary"
                          :placeholder="String(phoneReviewAspectUnlockCostItem.default_value ?? '')"
                        />
                        <span class="block text-[10px] text-brand-secondary font-mono">{{ phoneReviewAspectUnlockCostItem.config_key }}</span>
                      </label>
                    </div>

                    <div v-if="activeFeature === 'phone-review'" class="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <button
                        v-if="phoneReviewFreeAspectsItem"
                        type="button"
                        @click="openPhoneReviewAspectConfigModal('free')"
                        class="text-left bg-white border border-gray-100 hover:bg-brand-paper/60 rounded-xl px-3.5 py-3 transition-colors min-h-[74px]"
                      >
                        <span class="flex items-center justify-between gap-3">
                          <span class="text-xs font-bold text-brand-ink-strong">{{ phoneReviewFreeAspectsItem.label }}</span>
                          <span class="text-[10px] px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-600 border border-emerald-100">{{ runtimeConfigStringList(PHONE_REVIEW_FREE_ASPECTS_CONFIG_KEY).length }} 项</span>
                        </span>
                        <span class="block text-[11px] text-brand-secondary mt-1 truncate">{{ phoneReviewFreeAspectSummary }}</span>
                      </button>

                      <button
                        v-if="phoneReviewAspectOrderItem"
                        type="button"
                        @click="openPhoneReviewAspectConfigModal('order')"
                        class="text-left bg-white border border-gray-100 hover:bg-brand-paper/60 rounded-xl px-3.5 py-3 transition-colors min-h-[74px]"
                      >
                        <span class="flex items-center justify-between gap-3">
                          <span class="text-xs font-bold text-brand-ink-strong">{{ phoneReviewAspectOrderItem.label }}</span>
                          <span class="text-[10px] px-2 py-0.5 rounded-full bg-brand-primary/5 text-brand-primary border border-brand-primary/10">{{ phoneReviewOrderedAspectOptions.length }} 项</span>
                        </span>
                        <span class="block text-[11px] text-brand-secondary mt-1 truncate">{{ phoneReviewAspectOrderSummary }}</span>
                      </button>
                    </div>

                    <div v-else class="space-y-3">
                      <label
                        v-for="item in featureExtraConfigItems"
                        :key="item.config_key"
                        class="bg-brand-paper/40 border border-gray-100 rounded-xl px-3.5 py-3 space-y-1.5 block"
                      >
                        <span class="text-[10.5px] font-bold text-brand-secondary">{{ item.label }}</span>
                        <select
                          v-if="item.value_type === 'bool'"
                          v-model="runtimeConfigDrafts[item.config_key]"
                          @change="runtimeConfigDirty = true"
                          class="w-full bg-white border border-gray-100 rounded-lg px-2.5 py-2 text-xs outline-none focus:border-brand-primary"
                        >
                          <option :value="true">开启</option>
                          <option :value="false">关闭</option>
                        </select>
                        <textarea
                          v-else-if="item.value_type === 'json'"
                          v-model="runtimeConfigDrafts[item.config_key]"
                          @input="runtimeConfigDirty = true"
                          rows="3"
                          class="w-full bg-white border border-gray-100 rounded-lg px-2.5 py-2 text-xs font-mono outline-none focus:border-brand-primary"
                          :placeholder="JSON.stringify(item.default_value)"
                        ></textarea>
                        <input
                          v-else
                          v-model="runtimeConfigDrafts[item.config_key]"
                          @input="runtimeConfigDirty = true"
                          class="w-full bg-white border border-gray-100 rounded-lg px-2.5 py-2 text-xs font-mono outline-none focus:border-brand-primary"
                          :placeholder="String(item.default_value ?? '')"
                        />
                        <span class="block text-[10px] text-brand-secondary font-mono">{{ item.config_key }}</span>
                      </label>
                    </div>
                  </div>

                  <div v-else class="h-32 rounded-xl border border-dashed border-gray-200 bg-white/70 flex items-center justify-center text-xs text-brand-secondary font-mono">
                    暂无{{ activeFeatureDisplayName }}配置项
                  </div>
                </section>
              </div>

              <div class="bg-gray-50/50 border border-gray-100 p-5 rounded-xl space-y-4 shadow-xs text-left">
                <div
                  v-if="activeUsageReturnContext"
                  class="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-brand-primary/10 bg-brand-primary/5 px-4 py-3 text-xs"
                >
                  <div class="min-w-0">
                    <p class="font-bold text-brand-ink-strong">正在查看用户「{{ activeUsageReturnContext.userLabel }}」的手机号评测记录</p>
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

                <div class="flex flex-wrap items-center justify-between gap-3">
                  <div class="flex flex-wrap gap-3">
                    <input v-model="phoneReviewFilters.keyword" class="bg-white border border-gray-200 p-2.5 rounded-lg text-xs text-brand-ink-strong outline-none focus:border-brand-primary w-64" placeholder="用户 / 昵称 / 手机号 / 评测 ID" />
                    <AdminSelect
                      v-model="phoneReviewFilters.status"
                      :options="reviewStatusSelectOptions"
                      min-width-class="min-w-[132px]"
                      panel-width-class="w-44"
                    />
                    <AdminSelect
                      v-model="phoneReviewFilters.gender"
                      :options="genderSelectOptions"
                      min-width-class="min-w-[120px]"
                      panel-width-class="w-40"
                    />
                    <input v-model="phoneReviewFilters.channel" class="bg-white border border-gray-200 p-2.5 rounded-lg text-xs text-brand-ink-strong outline-none focus:border-brand-primary w-28" placeholder="渠道" />
                    <input v-model="phoneReviewFilters.date_from" class="bg-white border border-gray-200 p-2.5 rounded-lg text-xs text-brand-ink-strong outline-none focus:border-brand-primary w-36" placeholder="开始时间" />
                    <input v-model="phoneReviewFilters.date_to" class="bg-white border border-gray-200 p-2.5 rounded-lg text-xs text-brand-ink-strong outline-none focus:border-brand-primary w-36" placeholder="结束时间" />
                  </div>
                  <div class="flex gap-2">
                    <button @click="resetPhoneReviewFilters(); loadPhoneReviewRecords({resetPage: true})" class="bg-white border border-gray-100 text-brand-secondary px-4 py-2 rounded-xl text-xs font-bold hover:bg-gray-50">
                      重置
                    </button>
                    <button @click="searchPhoneReviewRecords" class="bg-brand-primary text-white px-4 py-2 rounded-xl text-xs font-bold hover:bg-brand-primary-strong">
                      {{ phoneReviewLoading ? '查询中...' : '查询评测' }}
                    </button>
                  </div>
                </div>

                <div v-if="phoneReviewError" class="text-xs text-red-600 bg-red-50 border border-red-100 rounded-xl px-3 py-2">
                  {{ phoneReviewError }}
                </div>

                <div class="overflow-x-auto border border-gray-100 rounded-xl bg-white">
                  <table class="w-full table-fixed text-xs font-sans text-left">
                    <colgroup>
                      <col class="w-[136px]" />
                      <col class="w-[124px]" />
                      <col class="w-[58px]" />
                      <col class="w-[104px]" />
                      <col class="w-[78px]" />
                      <col class="w-[78px]" />
                      <col class="w-[76px]" />
                      <col class="w-[88px]" />
                      <col class="w-[142px]" />
                      <col class="w-[92px]" />
                    </colgroup>
                    <thead>
                      <tr class="bg-gray-50 border-b border-gray-100 text-brand-secondary uppercase font-mono text-[10px] tracking-wider">
                        <th class="px-3 py-2.5">用户</th>
                        <th class="px-3 py-2.5">测评手机号</th>
                        <th class="px-2 py-2.5">性别</th>
                        <th class="px-3 py-2.5">状态</th>
                        <th class="px-2 py-2.5 text-right">基础消耗</th>
                        <th class="px-2 py-2.5 text-right">专项解锁</th>
                        <th class="px-2 py-2.5 text-right">语音次数</th>
                        <th class="px-3 py-2.5">生成耗时</th>
                        <th class="px-3 py-2.5">提交时间</th>
                        <th class="px-3 py-2.5 text-center">操作</th>
                      </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100 font-medium">
                      <tr v-for="record in phoneReviewRecords" :key="record.review_id" class="hover:bg-brand-paper/50">
                        <td class="px-3 py-2.5 align-top">
                          <div class="font-bold text-brand-ink-strong leading-snug break-words" :title="record.user_nickname || record.user_phone || record.user_uid || '未命名用户'">{{ record.user_nickname || record.user_phone || record.user_uid || '未命名用户' }}</div>
                          <div class="text-[10px] text-brand-secondary font-mono leading-snug break-words" :title="record.user_uid ? `UID ${record.user_uid}` : record.user_id || '--'">{{ record.user_uid ? `UID ${record.user_uid}` : shortText(record.user_id, 8, 4) }}</div>
                        </td>
                        <td class="px-3 py-2.5 align-top font-mono text-brand-ink-strong whitespace-nowrap">{{ record.phone }}</td>
                        <td class="px-2 py-2.5 align-top text-brand-secondary">{{ genderLabel(record.gender) }}</td>
                        <td class="px-3 py-2.5 align-top">
                          <span class="px-2 py-0.5 rounded text-[9px] font-bold inline-block border" :class="usageStatusClass(record.status)">
                            {{ reviewStatusLabel(record.status) }}
                          </span>
                          <div v-if="record.error_message" class="text-[10px] text-red-500 mt-1 leading-snug break-words" :title="record.error_message">{{ record.error_message }}</div>
                        </td>
                        <td class="px-2 py-2.5 align-top text-right font-mono text-brand-primary font-bold">{{ record.base_points_cost }}</td>
                        <td class="px-2 py-2.5 align-top text-right font-mono text-emerald-600 font-bold">{{ record.unlock_count }}</td>
                        <td class="px-2 py-2.5 align-top text-right font-mono text-amber-700 font-bold">{{ record.voice_count }}</td>
                        <td class="px-3 py-2.5 align-top font-mono text-brand-secondary break-words" :title="formatDuration(record.generation_duration_seconds)">{{ formatDuration(record.generation_duration_seconds) }}</td>
                        <td class="px-3 py-2.5 align-top font-mono text-brand-secondary whitespace-normal leading-snug" :title="formatTime(record.created_at)">{{ formatTime(record.created_at) }}</td>
                        <td class="px-3 py-2.5 align-top text-center">
                          <button
                            @click="openPhoneReviewDetail(record)"
                            class="inline-flex items-center justify-center rounded-lg border border-brand-primary/15 bg-brand-primary/5 px-3 py-1.5 text-[10.5px] font-bold text-brand-primary shadow-sm shadow-brand-primary/5 outline-none transition-colors hover:bg-brand-primary hover:text-white cursor-pointer"
                          >
                            详情
                          </button>
                        </td>
                      </tr>
                      <tr v-if="!phoneReviewLoading && phoneReviewRecords.length === 0">
                        <td colspan="10" class="p-8 text-center text-brand-secondary font-mono">暂无手机号评测记录</td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <div class="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-gray-100 text-xs text-brand-secondary">
                  <div class="font-mono">
                    显示 {{ phoneReviewPageStart }}-{{ phoneReviewPageEnd }} / {{ phoneReviewTotal }}，每页 {{ phoneReviewPageSize }} 条
                  </div>
                  <div class="flex items-center gap-2">
                    <button
                      @click="changePhoneReviewPage(-1)"
                      :disabled="!canGoPrevPhoneReviewPage"
                      class="bg-white border border-gray-100 text-brand-ink-strong px-3 py-1.5 rounded-lg text-[10.5px] font-bold disabled:opacity-40 disabled:cursor-not-allowed hover:bg-brand-paper"
                    >
                      上一页
                    </button>
                    <span class="font-mono text-[11px] text-brand-secondary px-2">
                      第 {{ phoneReviewCurrentPage }} / {{ phoneReviewTotalPages }} 页
                    </span>
                    <button
                      @click="changePhoneReviewPage(1)"
                      :disabled="!canGoNextPhoneReviewPage"
                      class="bg-white border border-gray-100 text-brand-ink-strong px-3 py-1.5 rounded-lg text-[10.5px] font-bold disabled:opacity-40 disabled:cursor-not-allowed hover:bg-brand-paper"
                    >
                      下一页
                    </button>
                  </div>
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
                  <p class="text-xs text-brand-secondary">审核用户申请成为推广大使、VIP 推广大使或 SVIP 推广大使。</p>
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
                  <span class="text-brand-secondary">推广大使门槛</span>
                  <input v-model.number="promotionRulesDraft.normal_threshold_cents" type="number" class="w-full bg-gray-50 border border-gray-100 rounded-xl p-2.5 outline-none" />
                </label>
                <label class="space-y-1 block">
                  <span class="text-brand-secondary">VIP 推广大使门槛</span>
                  <input v-model.number="promotionRulesDraft.senior_threshold_cents" type="number" class="w-full bg-gray-50 border border-gray-100 rounded-xl p-2.5 outline-none" />
                </label>
                <label class="space-y-1 block">
                  <span class="text-brand-secondary">推广大使返佣比例</span>
                  <input v-model.number="promotionRulesDraft.normal_commission_rate" type="number" step="0.01" class="w-full bg-gray-50 border border-gray-100 rounded-xl p-2.5 outline-none" />
                </label>
                <label class="space-y-1 block">
                  <span class="text-brand-secondary">VIP 返佣比例</span>
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
                  <h3 class="font-bold text-brand-ink-strong">
                    {{ activeSettingsTitle }}
                  </h3>
                  <p class="text-xs text-brand-secondary">
                    {{ activeSettingsDescription }}
                  </p>
                </div>
                <div class="flex gap-2">
                  <button v-if="activeSettings !== 'service-keys'" @click="activeSettings === 'llm-concurrency' ? Promise.allSettled([loadRuntimeConfig(), loadLlmConcurrency(), loadLlmKeys()]) : loadRuntimeConfig()" class="bg-white border border-gray-100 text-brand-secondary px-5 py-2.5 rounded-xl text-xs font-bold hover:bg-gray-50">
                    {{ runtimeConfigLoading ? '刷新中...' : '刷新配置' }}
                  </button>
                  <button v-if="activeSettings === 'llm-concurrency'" @click="loadLlmConcurrency" class="bg-brand-primary hover:bg-brand-primary-strong text-white px-5 py-2.5 rounded-xl text-xs font-bold transition-all outline-none cursor-pointer shadow-sm shadow-brand-primary/10">
                    {{ llmConcurrencyLoading ? '刷新中...' : '刷新状态' }}
                  </button>
                  <button v-if="activeSettings === 'service-keys'" @click="loadLlmKeys" class="bg-brand-primary hover:bg-brand-primary-strong text-white px-5 py-2.5 rounded-xl text-xs font-bold transition-all outline-none cursor-pointer shadow-sm shadow-brand-primary/10">
                    刷新密钥
                  </button>
                </div>
              </div>

              <div v-if="runtimeConfigError" class="text-xs text-red-600 bg-red-50 border border-red-100 rounded-xl px-3 py-2">
                {{ runtimeConfigError }}
              </div>

              <div v-if="activeSettings === 'basic-config'" class="grid grid-cols-1 xl:grid-cols-[minmax(300px,0.78fr)_minmax(0,1.22fr)] gap-4 items-stretch">
                <section class="bg-brand-paper/40 border border-gray-100 rounded-2xl p-4 space-y-3 h-full">
                  <div class="flex items-start justify-between gap-3">
                    <div class="min-w-0">
                      <h4 class="font-serif text-sm font-bold text-brand-ink-strong">初始积分设置</h4>
                      <p class="text-[11px] text-brand-secondary mt-0.5 leading-snug">保存初始积分，可只影响新用户，也可按差额同步全部正式用户。</p>
                    </div>
                    <div class="text-right shrink-0">
                      <p class="text-[9px] text-brand-secondary font-mono uppercase">Current</p>
                      <b class="text-lg font-mono text-brand-primary">{{ runtimeConfigDrafts[INITIAL_POINTS_CONFIG_KEY] ?? initialPointsDraft }}</b>
                    </div>
                  </div>

                  <label class="space-y-1 block">
                    <span class="text-[10.5px] font-bold text-brand-secondary">新注册初始积分</span>
                    <input
                      v-model.number="initialPointsDraft"
                      type="number"
                      min="0"
                      class="w-full bg-white border border-gray-100 rounded-lg px-2.5 py-2 text-xs font-mono text-brand-ink-strong outline-none focus:border-brand-primary"
                    />
                  </label>

                  <div class="grid grid-cols-2 gap-2">
                    <button
                      type="button"
                      @click="initialPointsScope = 'future_users'"
                      class="text-left rounded-xl border px-3 py-2 transition-colors min-h-[58px]"
                      :class="initialPointsScope === 'future_users' ? 'bg-white border-brand-primary/30 shadow-sm text-brand-ink-strong' : 'bg-white/60 border-gray-100 text-brand-secondary hover:bg-white'"
                    >
                      <span class="block text-xs font-bold">影响新用户</span>
                      <span class="block text-[10px] mt-0.5 leading-snug">老用户余额不变。</span>
                    </button>
                    <button
                      type="button"
                      @click="initialPointsScope = 'all_users'"
                      class="text-left rounded-xl border px-3 py-2 transition-colors min-h-[58px]"
                      :class="initialPointsScope === 'all_users' ? 'bg-red-50 border-red-100 shadow-sm text-red-700' : 'bg-white/60 border-gray-100 text-brand-secondary hover:bg-white'"
                    >
                      <span class="block text-xs font-bold">影响全部用户</span>
                      <span class="block text-[10px] mt-0.5 leading-snug">按差额写入流水。</span>
                    </button>
                  </div>

                  <textarea
                    v-model="initialPointsReason"
                    class="w-full bg-white border border-gray-100 rounded-lg px-2.5 py-2 text-xs outline-none min-h-14"
                    placeholder="操作原因，可选"
                  ></textarea>

                  <div class="flex flex-wrap items-center justify-between gap-2">
                    <div v-if="initialPointsResult" class="text-[10.5px] text-brand-secondary leading-snug">
                      上次：{{ initialPointsResult.previous_initial_grant }} → {{ initialPointsResult.initial_grant }}，调整 {{ initialPointsResult.affected_user_count }} 人。
                    </div>
                    <button
                      @click="saveInitialPointsSettings"
                      class="ml-auto bg-brand-primary hover:bg-brand-primary-strong text-white px-3.5 py-2 rounded-lg text-[11px] font-bold transition-all outline-none cursor-pointer shadow-sm shadow-brand-primary/10"
                    >
                      {{ initialPointsSaving ? '保存中...' : '保存初始积分' }}
                    </button>
                  </div>
                </section>

                <section class="bg-white border border-gray-100 rounded-2xl p-4 space-y-3 h-full flex flex-col">
                  <div class="flex items-start justify-between gap-3">
                    <div class="min-w-0">
                      <h4 class="font-serif text-sm font-bold text-brand-ink-strong">充值套餐设置</h4>
                      <p class="text-[11px] text-brand-secondary mt-0.5 leading-snug">最多 6 个展示卡片，点击卡片进入编辑。</p>
                    </div>
                    <button
                      @click="addRechargePackageDraft"
                      :disabled="!canAddRechargePackage"
                      class="bg-white border border-gray-100 text-brand-ink-strong px-3 py-1.5 rounded-lg text-[11px] font-bold hover:bg-brand-paper disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
                    >
                      新增套餐
                    </button>
                  </div>

                  <div v-if="rechargePackageDrafts.length === 0" class="flex-1 min-h-[176px] rounded-xl border border-dashed border-gray-200 bg-brand-paper/40 flex items-center justify-center text-xs text-brand-secondary font-mono">
                    暂无充值套餐，可点击“新增套餐”开始配置
                  </div>

                  <div v-else :class="rechargePackageGridClass">
                    <button
                      v-for="(packageDraft, index) in rechargePackageDrafts"
                      :key="packageDraft.package_key || index"
                      type="button"
                      @click="openRechargePackageEditor(index)"
                      class="relative h-full rounded-xl border p-3 text-left transition-colors hover:bg-brand-paper/70 flex flex-col justify-center"
                      :class="[rechargePackageCardLayoutClass(index), packageDraft.enabled ? 'bg-brand-paper/45 border-gray-100 text-brand-ink-strong' : 'bg-gray-50 border-gray-100 text-brand-secondary opacity-70']"
                    >
                      <span class="absolute right-2 top-2 text-[9px] font-mono text-brand-secondary">{{ index + 1 }}</span>
                      <span class="block text-[10px] text-brand-secondary font-bold">金额</span>
                      <span class="block mt-1 font-mono font-bold text-brand-primary" :class="rechargePackageAmountClass()">¥{{ Number(packageDraft.price_yuan || 0).toFixed(2) }}</span>
                      <span class="block mt-2 text-[10px] text-brand-secondary font-bold">积分</span>
                      <span class="block mt-0.5 font-mono font-bold" :class="rechargePackagePointsClass()">{{ packageDraft.points_amount }}</span>
                    </button>
                  </div>

                  <div class="flex flex-wrap items-center justify-between gap-2">
                    <p class="text-[10.5px] text-brand-secondary leading-snug">
                      {{ rechargePackageDrafts.length }} / {{ MAX_RECHARGE_PACKAGE_COUNT }} 个套餐。{{ rechargePackagesDirty ? '有未保存修改。' : '已同步。' }}
                    </p>
                    <button
                      @click="saveRechargePackages"
                      class="bg-brand-primary hover:bg-brand-primary-strong text-white px-3.5 py-2 rounded-lg text-[11px] font-bold transition-all outline-none cursor-pointer shadow-sm shadow-brand-primary/10"
                    >
                      {{ rechargePackagesSaving ? '保存中...' : '保存充值套餐' }}
                    </button>
                  </div>
                </section>
              </div>

              <div v-if="activeSettings === 'customer-service'" class="space-y-4">
                <section class="bg-white border border-gray-100 rounded-2xl p-4 space-y-4">
                  <div class="flex flex-wrap items-start justify-between gap-3 pb-2 border-b border-gray-100">
                    <div>
                      <h4 class="font-serif text-sm font-bold text-brand-ink-strong">基础联系方式</h4>
                      <p class="text-[11px] text-brand-secondary mt-0.5 leading-snug">控制统一客服弹窗里的微信号、二维码、复制按钮和未配置提示。</p>
                    </div>
                    <button
                      @click="saveCustomerServiceConfig"
                      class="bg-brand-primary hover:bg-brand-primary-strong text-white px-4 py-2 rounded-xl text-[11px] font-bold transition-all outline-none cursor-pointer shadow-sm shadow-brand-primary/10"
                    >
                      {{ runtimeConfigLoading ? '保存中...' : '保存客服配置' }}
                    </button>
                  </div>

                  <div class="grid grid-cols-1 xl:grid-cols-[minmax(0,1fr)_260px] gap-4 items-start">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <label
                        v-for="item in customerServiceBaseConfigItems"
                        :key="item.config_key"
                        class="space-y-1.5 block"
                      >
                        <span class="text-[10.5px] font-bold text-brand-secondary">{{ item.label }}</span>
                        <textarea
                          v-if="item.config_key === CUSTOMER_SERVICE_UNCONFIGURED_TEXT_CONFIG_KEY || item.config_key === CUSTOMER_SERVICE_QR_GUIDANCE_TEXT_CONFIG_KEY"
                          v-model="runtimeConfigDrafts[item.config_key]"
                          @input="runtimeConfigDirty = true"
                          class="w-full min-h-[72px] bg-brand-paper border border-gray-100 rounded-lg px-2.5 py-2 text-xs text-brand-ink-strong outline-none focus:border-brand-primary"
                          :placeholder="String(item.default_value || '')"
                        ></textarea>
                        <input
                          v-else
                          v-model="runtimeConfigDrafts[item.config_key]"
                          @input="runtimeConfigDirty = true"
                          type="text"
                          class="w-full bg-brand-paper border border-gray-100 rounded-lg px-2.5 py-2 text-xs font-mono text-brand-ink-strong outline-none focus:border-brand-primary"
                          :placeholder="String(item.default_value || '')"
                        />
                        <span
                          v-if="item.config_key === CUSTOMER_SERVICE_WECHAT_ID_CONFIG_KEY && !runtimeConfigDrafts[CUSTOMER_SERVICE_WECHAT_ID_CONFIG_KEY] && runtimeConfigDrafts[CUSTOMER_SERVICE_CONTACT_URL_CONFIG_KEY]"
                          class="block text-[10px] text-amber-700"
                        >
                          当前将兼容使用旧字段：{{ runtimeConfigDrafts[CUSTOMER_SERVICE_CONTACT_URL_CONFIG_KEY] }}
                        </span>
                        <span v-else class="block text-[10px] text-brand-secondary leading-snug">{{ item.description || '用于前台统一联系客服弹窗。' }}</span>
                      </label>
                    </div>

                    <div class="rounded-2xl border border-gray-100 bg-brand-paper/45 p-3 space-y-2">
                      <div class="h-48 rounded-xl border border-dashed border-gray-200 bg-white flex items-center justify-center overflow-hidden">
                        <img
                          v-if="customerServiceQrPreviewUrl"
                          :src="customerServiceQrPreviewUrl"
                          alt="客服二维码预览"
                          class="h-full w-full object-contain"
                        />
                        <span v-else class="text-[11px] text-brand-secondary">客服二维码暂未配置</span>
                      </div>
                      <input
                        ref="customerServiceQrInputRef"
                        type="file"
                        accept="image/jpeg,image/png,image/webp"
                        class="hidden"
                        @change="handleCustomerServiceQrFileChange"
                      />
                      <div class="grid grid-cols-2 gap-2">
                        <button
                          @click="openCustomerServiceQrUploader"
                          class="bg-white border border-gray-100 text-brand-ink-strong px-3 py-2 rounded-lg text-[10.5px] font-bold hover:bg-brand-paper disabled:opacity-60"
                          :disabled="customerServiceQrUploading"
                        >
                          {{ customerServiceQrUploading ? '上传中...' : '上传二维码' }}
                        </button>
                        <button
                          @click="deleteCustomerServiceQrCode"
                          class="bg-red-50 border border-red-100 text-red-600 px-3 py-2 rounded-lg text-[10.5px] font-bold hover:bg-red-100 disabled:opacity-60"
                          :disabled="customerServiceQrDeleting || !customerServiceQrPreviewUrl"
                        >
                          {{ customerServiceQrDeleting ? '删除中...' : '删除二维码' }}
                        </button>
                      </div>
                      <p v-if="customerServiceQrError" class="text-[10.5px] text-red-600 leading-snug">{{ customerServiceQrError }}</p>
                      <p v-else class="text-[10px] text-brand-secondary leading-snug">支持 JPG / PNG / WebP，大小不超过 1.5MB。</p>
                    </div>
                  </div>
                </section>

                <section class="bg-white border border-gray-100 rounded-2xl p-4 space-y-4">
                  <div class="flex flex-wrap items-start justify-between gap-3 pb-2 border-b border-gray-100">
                    <div>
                      <h4 class="font-serif text-sm font-bold text-brand-ink-strong">业务场景文案</h4>
                      <p class="text-[11px] text-brand-secondary mt-0.5 leading-snug">不同“联系客服”入口会读取对应文案；未命中时使用默认客服文案。</p>
                    </div>
                    <span class="rounded-full border border-emerald-100 bg-emerald-50 px-2.5 py-1 text-[10px] font-bold text-emerald-700">7 个场景</span>
                  </div>

                  <div class="grid grid-cols-1 lg:grid-cols-2 gap-3">
                    <label
                      v-for="item in CUSTOMER_SERVICE_COPY_CONFIGS"
                      :key="item.key"
                      class="block rounded-xl border border-gray-100 bg-brand-paper/35 p-3 space-y-2"
                    >
                      <span class="flex items-start justify-between gap-3">
                        <span>
                          <span class="block text-xs font-bold text-brand-ink-strong">{{ item.label }}</span>
                          <span class="mt-0.5 block text-[10px] text-brand-secondary">{{ item.scene }}</span>
                        </span>
                        <span class="shrink-0 rounded-full bg-white px-2 py-0.5 text-[9px] font-mono text-brand-secondary border border-gray-100">{{ item.key.replace('customer_service.copy.', '') }}</span>
                      </span>
                      <textarea
                        v-model="runtimeConfigDrafts[item.key]"
                        @input="runtimeConfigDirty = true"
                        class="w-full min-h-[88px] bg-white border border-gray-100 rounded-lg px-2.5 py-2 text-xs text-brand-ink-strong outline-none focus:border-brand-primary"
                        :placeholder="item.placeholder"
                      ></textarea>
                    </label>
                  </div>

                  <div class="flex justify-end">
                    <button
                      @click="saveCustomerServiceConfig"
                      class="bg-brand-primary hover:bg-brand-primary-strong text-white px-5 py-2.5 rounded-xl text-xs font-bold transition-all outline-none cursor-pointer shadow-sm shadow-brand-primary/10"
                    >
                      {{ runtimeConfigLoading ? '保存中...' : '保存客服配置' }}
                    </button>
                  </div>
                </section>
              </div>

              <div v-if="activeSettings === 'basic-config'" class="space-y-4">
                <h4 class="text-xs font-bold text-brand-secondary font-mono uppercase pb-2 border-b border-gray-100">基础系统配置</h4>
                <div v-if="basicSystemConfigItems.length" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div v-for="item in basicSystemConfigItems" :key="item.config_key" class="bg-brand-paper/40 border border-gray-100 rounded-xl p-4 space-y-2">
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

                <div v-else class="h-32 rounded-xl border border-dashed border-gray-200 bg-white/70 flex items-center justify-center text-xs text-brand-secondary font-mono">
                  暂无基础系统配置项
                </div>

                <button @click="saveRuntimeConfig(basicSystemConfigItems, '基础系统配置已保存')" class="bg-brand-primary hover:bg-brand-primary-strong text-white px-5 py-2.5 rounded-xl text-xs font-bold transition-all outline-none cursor-pointer shadow-sm shadow-brand-primary/10">
                  {{ runtimeConfigLoading ? '保存中...' : '保存基础系统配置' }}
                </button>
              </div>

              <div v-if="activeSettings === 'voice'" class="space-y-4">
                <div class="flex flex-wrap items-start justify-between gap-3 pb-2 border-b border-gray-100">
                  <div>
                    <h4 class="text-xs font-bold text-brand-secondary font-mono uppercase">语音播报配置</h4>
                    <p class="text-[11px] text-brand-secondary mt-1">控制 H5 与小程序共用的 TTS 模式、默认自动播报、供应商、音色、缓存和文本长度限制。</p>
                  </div>
                  <button
                    @click="saveRuntimeConfig(voiceSystemConfigItems, '语音播报配置已保存')"
                    class="bg-brand-primary hover:bg-brand-primary-strong text-white px-5 py-2.5 rounded-xl text-xs font-bold transition-all outline-none cursor-pointer shadow-sm shadow-brand-primary/10"
                  >
                    {{ runtimeConfigLoading ? '保存中...' : '保存语音配置' }}
                  </button>
                </div>

                <div v-if="voiceSystemConfigItems.length" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div v-for="item in voiceSystemConfigItems" :key="item.config_key" class="bg-brand-paper/40 border border-gray-100 rounded-xl p-4 space-y-2">
                    <div class="flex items-start justify-between gap-2">
                      <div>
                        <div class="text-sm font-bold text-brand-ink-strong">{{ item.label }}</div>
                        <div class="text-[10px] text-brand-secondary font-mono">{{ item.config_key }}</div>
                      </div>
                      <span class="text-[10px] px-2 py-0.5 rounded-full border" :class="item.advanced ? 'bg-amber-50 text-amber-700 border-amber-100' : 'bg-emerald-50 text-emerald-600 border-emerald-100'">
                        {{ item.advanced ? '高级' : '常用' }}
                      </span>
                    </div>
                    <p class="text-[11px] text-brand-secondary leading-relaxed">{{ item.help_text || item.description || '暂无说明' }}</p>
                    <template v-if="item.value_type === 'bool'">
                      <AdminSelect
                        v-model="runtimeConfigDrafts[item.config_key]"
                        @change="runtimeConfigDirty = true"
                        :options="booleanToggleSelectOptions"
                        min-width-class="w-full"
                        panel-width-class="w-full"
                      />
                    </template>
                    <template v-else-if="item.input_options?.length">
                      <div class="grid grid-cols-2 gap-2">
                        <button
                          v-for="option in item.input_options"
                          :key="option.value"
                          type="button"
                          @click="runtimeConfigDrafts[item.config_key] = option.value; runtimeConfigDirty = true"
                          class="text-left rounded-xl border px-3 py-2 text-xs font-bold transition-colors"
                          :class="runtimeConfigDrafts[item.config_key] === option.value ? 'bg-brand-primary text-white border-brand-primary shadow-sm shadow-brand-primary/10' : 'bg-white text-brand-ink-strong border-gray-100 hover:bg-brand-paper'"
                        >
                          {{ option.label }}
                        </button>
                      </div>
                    </template>
                    <template v-else-if="item.value_type === 'json'">
                      <textarea
                        v-model="runtimeConfigDrafts[item.config_key]"
                        @input="runtimeConfigDirty = true"
                        class="w-full bg-white border border-gray-100 rounded-lg p-2 text-xs outline-none min-h-24 font-mono"
                      ></textarea>
                    </template>
                    <template v-else>
                      <input
                        v-model="runtimeConfigDrafts[item.config_key]"
                        @input="runtimeConfigDirty = true"
                        :type="item.value_type === 'int' || item.value_type === 'float' ? 'number' : 'text'"
                        class="w-full bg-white border border-gray-100 rounded-lg p-2 text-xs outline-none"
                      />
                    </template>
                    <div class="text-[11px] text-brand-secondary">当前值：{{ runtimeInputText(item) }}</div>
                  </div>
                </div>

                <div v-else class="h-32 rounded-xl border border-dashed border-gray-200 bg-white/70 flex items-center justify-center text-xs text-brand-secondary font-mono">
                  暂无语音播报配置项
                </div>
              </div>

              <div v-if="activeSettings === 'safety'" class="space-y-4">
                <div class="flex flex-wrap items-start justify-between gap-3 pb-2 border-b border-gray-100">
                  <div>
                    <h4 class="text-xs font-bold text-brand-secondary font-mono uppercase">安全与合规</h4>
                    <p class="text-[11px] text-brand-secondary mt-1">安全模式用于紧急收敛前台能力。允许功能和强制隐藏功能使用勾选方式维护，不再直接编辑 JSON。</p>
                  </div>
                  <button
                    @click="saveRuntimeConfig(safetySystemConfigItems, '安全与合规配置已保存')"
                    class="bg-brand-primary hover:bg-brand-primary-strong text-white px-5 py-2.5 rounded-xl text-xs font-bold transition-all outline-none cursor-pointer shadow-sm shadow-brand-primary/10"
                  >
                    {{ runtimeConfigLoading ? '保存中...' : '保存安全配置' }}
                  </button>
                </div>

                <div v-if="safetySystemConfigItems.length" class="grid grid-cols-1 gap-4">
                  <div v-for="item in safetySystemConfigItems" :key="item.config_key" class="bg-brand-paper/40 border border-gray-100 rounded-xl p-4 space-y-3">
                    <div class="flex flex-wrap items-start justify-between gap-2">
                      <div>
                        <div class="text-sm font-bold text-brand-ink-strong">{{ item.label }}</div>
                        <div class="text-[10px] text-brand-secondary font-mono">{{ item.config_key }}</div>
                      </div>
                      <span class="text-[10px] px-2 py-0.5 rounded-full border" :class="item.high_risk ? 'bg-red-50 text-red-600 border-red-100' : 'bg-emerald-50 text-emerald-600 border-emerald-100'">
                        {{ item.high_risk ? '高风险' : '常规' }}
                      </span>
                    </div>
                    <p class="text-[11px] text-brand-secondary leading-relaxed">{{ item.help_text || item.description || '暂无说明' }}</p>

                    <template v-if="item.value_type === 'bool'">
                      <AdminSelect
                        v-model="runtimeConfigDrafts[item.config_key]"
                        @change="runtimeConfigDirty = true"
                        :options="booleanToggleSelectOptions"
                        min-width-class="w-full"
                        panel-width-class="w-full"
                      />
                    </template>
                    <template v-else-if="item.input_options?.length">
                      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                        <button
                          v-for="option in item.input_options"
                          :key="option.value"
                          type="button"
                          @click="toggleRuntimeConfigStringListValue(item.config_key, option.value)"
                          class="rounded-xl border px-3 py-2 text-left transition-colors"
                          :class="runtimeConfigStringList(item.config_key).includes(option.value) ? 'bg-brand-primary text-white border-brand-primary shadow-sm shadow-brand-primary/10' : 'bg-white text-brand-ink-strong border-gray-100 hover:bg-brand-paper'"
                        >
                          <span class="block text-xs font-bold">{{ option.label }}</span>
                          <span class="block text-[9.5px] font-mono opacity-70">{{ option.value }}</span>
                        </button>
                      </div>
                    </template>
                    <template v-else-if="item.value_type === 'json'">
                      <textarea
                        v-model="runtimeConfigDrafts[item.config_key]"
                        @input="runtimeConfigDirty = true"
                        class="w-full bg-white border border-gray-100 rounded-lg p-2 text-xs outline-none min-h-24 font-mono"
                      ></textarea>
                    </template>
                    <template v-else>
                      <input
                        v-model="runtimeConfigDrafts[item.config_key]"
                        @input="runtimeConfigDirty = true"
                        :type="item.value_type === 'int' || item.value_type === 'float' ? 'number' : 'text'"
                        class="w-full bg-white border border-gray-100 rounded-lg p-2 text-xs outline-none"
                      />
                    </template>
                    <div class="text-[11px] text-brand-secondary">当前值：{{ runtimeInputText(item) }}</div>
                  </div>
                </div>

                <div v-else class="h-32 rounded-xl border border-dashed border-gray-200 bg-white/70 flex items-center justify-center text-xs text-brand-secondary font-mono">
                  暂无安全与合规配置项
                </div>
              </div>

              <div v-if="activeSettings === 'llm-concurrency'" class="space-y-4">
                <div v-if="llmError" class="text-xs text-red-600 bg-red-50 border border-red-100 rounded-xl px-3 py-2">
                  {{ llmError }}
                </div>

                <section class="space-y-3">
                  <div class="flex flex-wrap items-start justify-between gap-3 pb-2 border-b border-gray-100">
                    <div>
                      <h4 class="text-xs font-bold text-brand-secondary font-mono uppercase">DeepSeek 运行概览</h4>
                      <p class="text-[11px] text-brand-secondary mt-1">前台请求优先，后台预热按比例让路；Redis URL 只由服务端环境变量提供。</p>
                    </div>
                    <span class="text-[10px] px-2.5 py-1 rounded-full border font-mono" :class="llmConcurrency?.backend_available ? 'bg-emerald-50 text-emerald-600 border-emerald-100' : 'bg-red-50 text-red-600 border-red-100'">
                      {{ llmConcurrency?.backend || 'memory' }} · {{ llmConcurrency?.backend_available ? '可用' : '不可用' }}
                    </span>
                  </div>

                  <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">
                    <div v-for="item in llmConcurrencyCards" :key="item.label" class="bg-brand-paper/40 border border-gray-100 rounded-xl p-4 min-h-[88px]">
                      <div class="text-[10px] text-brand-secondary font-bold">{{ item.label }}</div>
                      <div class="text-xl font-black font-mono text-brand-ink-strong mt-1">{{ item.value }}</div>
                      <div class="text-[10px] text-brand-secondary font-mono mt-1 truncate" :title="item.sub">{{ item.sub }}</div>
                    </div>
                  </div>
                </section>

                <section class="space-y-3">
                  <div class="flex flex-wrap items-start justify-between gap-3 pb-2 border-b border-gray-100">
                    <div>
                      <h4 class="text-xs font-bold text-brand-secondary font-mono uppercase">并发配置</h4>
                      <p class="text-[11px] text-brand-secondary mt-1">切换 Redis 前请先在服务端配置 `EASEWISE_REDIS_URL`；后台不展示 Redis URL 明文。</p>
                    </div>
                    <button
                      @click="saveRuntimeConfig(llmConcurrencyConfigItems, 'DeepSeek 并发治理配置已保存')"
                      class="bg-brand-primary hover:bg-brand-primary-strong text-white px-5 py-2.5 rounded-xl text-xs font-bold transition-all outline-none cursor-pointer shadow-sm shadow-brand-primary/10"
                    >
                      {{ runtimeConfigLoading ? '保存中...' : '保存并发配置' }}
                    </button>
                  </div>

                  <div v-if="llmConcurrencyConfigItems.length" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div v-for="item in llmConcurrencyConfigItems" :key="item.config_key" class="bg-brand-paper/40 border border-gray-100 rounded-xl p-4 space-y-2">
                      <div class="flex items-start justify-between gap-2">
                        <div>
                          <div class="text-sm font-bold text-brand-ink-strong">{{ item.label }}</div>
                          <div class="text-[10px] text-brand-secondary font-mono">{{ item.config_key }}</div>
                        </div>
                        <span class="text-[10px] px-2 py-0.5 rounded-full border" :class="item.high_risk ? 'bg-red-50 text-red-600 border-red-100' : 'bg-emerald-50 text-emerald-600 border-emerald-100'">
                          {{ item.high_risk ? '高风险' : '常规' }}
                        </span>
                      </div>
                      <p class="text-[11px] text-brand-secondary leading-relaxed">{{ item.description || '暂无说明' }}</p>
                      <template v-if="item.value_type === 'bool'">
                        <AdminSelect
                          v-model="runtimeConfigDrafts[item.config_key]"
                          @change="runtimeConfigDirty = true"
                          :options="booleanToggleSelectOptions"
                          min-width-class="w-full"
                          panel-width-class="w-full"
                        />
                      </template>
                      <template v-else-if="item.input_options?.length">
                        <AdminSelect
                          v-model="runtimeConfigDrafts[item.config_key]"
                          @change="runtimeConfigDirty = true"
                          :options="item.input_options.map((option) => ({value: option.value, label: option.label, dotClass: option.value === 'redis' ? 'bg-amber-500' : 'bg-emerald-500'}))"
                          min-width-class="w-full"
                          panel-width-class="w-full"
                        />
                      </template>
                      <template v-else>
                        <input
                          v-model="runtimeConfigDrafts[item.config_key]"
                          @input="runtimeConfigDirty = true"
                          :type="item.value_type === 'int' || item.value_type === 'float' ? 'number' : 'text'"
                          :step="item.value_type === 'float' ? '0.01' : undefined"
                          class="w-full bg-white border border-gray-100 rounded-lg p-2 text-xs outline-none"
                        />
                      </template>
                      <div class="text-[11px] text-brand-secondary">当前值：{{ runtimeInputText(item) }}</div>
                    </div>
                  </div>
                </section>

                <section class="space-y-3">
                  <h4 class="text-xs font-bold text-brand-secondary font-mono uppercase pb-2 border-b border-gray-100">Key 池运行态</h4>
                  <div class="overflow-x-auto border border-gray-100 rounded-xl bg-white">
                    <table class="w-full text-xs font-sans text-left">
                      <thead>
                        <tr class="bg-gray-50 border-b border-gray-100 text-brand-secondary uppercase font-mono text-[10px] tracking-wider">
                          <th class="p-3">Key</th>
                          <th class="p-3">状态</th>
                          <th class="p-3">并发</th>
                          <th class="p-3">可用槽位</th>
                          <th class="p-3">冷却</th>
                          <th class="p-3">最近 429</th>
                          <th class="p-3">最近错误</th>
                          <th class="p-3">最近使用</th>
                        </tr>
                      </thead>
                      <tbody class="divide-y divide-gray-100">
                        <tr v-for="item in llmKeys" :key="`runtime-${item.key_id}`" class="hover:bg-brand-paper/50">
                          <td class="p-3">
                            <div class="font-bold text-brand-ink-strong">{{ item.display_name }}</div>
                            <div class="font-mono text-[10px] text-brand-secondary">{{ item.model }} · P{{ item.priority }}</div>
                          </td>
                          <td class="p-3">
                            <span class="text-[10px] px-2 py-1 rounded-full border font-bold" :class="llmKeyRuntimeClass(item)">
                              {{ llmKeyRuntimeLabel(item) }}
                            </span>
                          </td>
                          <td class="p-3 font-mono text-brand-ink-strong">{{ item.current_inflight }} / {{ item.max_concurrency }}</td>
                          <td class="p-3 font-mono text-emerald-600 font-bold">{{ item.available_slots }}</td>
                          <td class="p-3 font-mono text-brand-secondary">{{ formatTime(item.cooldown_until) }}</td>
                          <td class="p-3 font-mono text-brand-secondary">{{ formatTime(item.last_rate_limited_at) }}</td>
                          <td class="p-3 text-brand-secondary max-w-[220px] truncate" :title="item.last_error_message || '--'">{{ item.last_error_message || '--' }}</td>
                          <td class="p-3 font-mono text-brand-secondary">{{ formatTime(item.last_used_at) }}</td>
                        </tr>
                        <tr v-if="!llmLoading && llmKeys.length === 0">
                          <td colspan="8" class="p-8 text-center text-brand-secondary font-mono">暂无 DeepSeek Key；系统会尝试读取服务器环境变量。</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </section>
              </div>

              <div v-if="activeSettings === 'service-keys'" class="space-y-4">
                <h4 class="text-xs font-bold text-brand-secondary font-mono uppercase pb-2 border-b border-gray-100">服务密钥管理</h4>
                <div class="bg-brand-paper/50 border border-gray-100 rounded-xl p-4 text-xs text-brand-secondary leading-relaxed">
                  可在这里配置 DeepSeek 与阿里云服务密钥。保存后系统只展示脱敏值，真实 Key 不会在列表或编辑表单中回显；运行时优先使用已启用的后台配置，未配置时继续读取服务器环境变量。
                </div>
                <div v-if="llmError" class="text-xs text-red-600 bg-red-50 border border-red-100 rounded-xl px-3 py-2">
                  {{ llmError }}
	                </div>
	                <div class="flex justify-end">
	                  <button @click="beginCreateLlmKey" class="bg-brand-primary text-white px-4 py-2 rounded-xl text-xs font-bold">新增服务密钥</button>
	                </div>
                <div v-if="llmKeyFormMode" class="border border-gray-100 rounded-xl p-4 space-y-4 bg-gray-50/60">
                  <div class="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <div class="text-xs font-bold text-brand-ink-strong">{{ llmKeyFormMode === 'edit' ? '编辑服务密钥' : '新增服务密钥' }}</div>
                      <div class="text-[11px] text-brand-secondary mt-1">
                        {{ llmKeyFormMode === 'edit' ? '真实 Key 留空则保留当前配置。' : '新增时必须填写真实 Key。' }}
                      </div>
                    </div>
                    <span class="text-[10px] px-2.5 py-1 rounded-full bg-white border border-gray-100 text-brand-secondary font-mono">
                      secret_ref 由系统自动生成
                    </span>
                  </div>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <label class="space-y-1.5 block">
                      <span class="text-[11px] font-bold text-brand-secondary">供应商</span>
                      <AdminSelect
                        v-model="llmKeyForm.provider"
                        @change="handleServiceKeyProviderChange"
                        :options="serviceKeyProviderSelectOptions"
                        min-width-class="w-full"
                        panel-width-class="w-full"
                      />
                    </label>
                    <label class="space-y-1.5 block">
                      <span class="text-[11px] font-bold text-brand-secondary">模型 / 服务</span>
                      <AdminSelect
                        v-model="llmKeyForm.model"
                        @change="handleServiceKeyModelChange"
                        :options="activeServiceKeyPresetOptions"
                        min-width-class="w-full"
                        panel-width-class="w-full"
                      />
                    </label>
                    <label class="space-y-1.5 block">
                      <span class="text-[11px] font-bold text-brand-secondary">密钥名称</span>
                      <input v-model="llmKeyForm.display_name" class="w-full bg-white border border-gray-100 rounded-lg p-2.5 text-xs outline-none" placeholder="例如：DeepSeek 主模型 Key" />
                    </label>
                    <label class="space-y-1.5 block">
                      <span class="text-[11px] font-bold text-brand-secondary">真实 Key</span>
                      <input v-model="llmKeyForm.secret_value" type="password" autocomplete="new-password" class="w-full bg-white border border-gray-100 rounded-lg p-2.5 text-xs outline-none" :placeholder="llmKeyFormMode === 'edit' ? '留空则保留原密钥' : '粘贴 DeepSeek 或阿里云真实 Key'" />
                    </label>
                    <label class="space-y-1.5 block">
                      <span class="text-[11px] font-bold text-brand-secondary">优先级</span>
                      <input v-model.number="llmKeyForm.priority" type="number" class="w-full bg-white border border-gray-100 rounded-lg p-2.5 text-xs outline-none" placeholder="数字越小优先级越高" />
                    </label>
                    <label class="space-y-1.5 block">
                      <span class="text-[11px] font-bold text-brand-secondary">单 Key 并发上限</span>
                      <input v-model.number="llmKeyForm.max_concurrency" type="number" min="1" class="w-full bg-white border border-gray-100 rounded-lg p-2.5 text-xs outline-none" placeholder="DeepSeek 默认建议 450" />
                    </label>
                    <label class="space-y-1.5 block">
                      <span class="text-[11px] font-bold text-brand-secondary">429 冷却秒数</span>
                      <input v-model.number="llmKeyForm.cooldown_seconds" type="number" min="1" class="w-full bg-white border border-gray-100 rounded-lg p-2.5 text-xs outline-none" placeholder="默认 60" />
                    </label>
                    <label class="space-y-1.5 block">
                      <span class="text-[11px] font-bold text-brand-secondary">最后操作人</span>
                      <input v-model="llmKeyForm.last_operator" class="w-full bg-white border border-gray-100 rounded-lg p-2.5 text-xs outline-none" placeholder="最后操作人" />
                    </label>
                    <label class="space-y-1.5 block md:col-span-2">
                      <span class="text-[11px] font-bold text-brand-secondary">备注</span>
                      <input v-model="llmKeyForm.remark" class="w-full bg-white border border-gray-100 rounded-lg p-2.5 text-xs outline-none" placeholder="例如：生产主 Key、备用 Key、阿里云语音服务 Token" />
                    </label>
                  </div>
                  <label class="inline-flex items-center gap-2 text-xs text-brand-secondary">
                    <input v-model="llmKeyForm.enabled" type="checkbox" />
                    启用
                  </label>
                  <div class="flex gap-2">
                    <button @click="submitLlmKeyForm" class="bg-brand-primary text-white px-4 py-2 rounded-lg text-xs font-bold">保存密钥</button>
                    <button @click="llmKeyFormMode = null" class="bg-white border border-gray-100 text-brand-secondary px-4 py-2 rounded-lg text-xs font-bold">取消</button>
                  </div>
                </div>
	                <div class="overflow-x-auto border border-gray-100 rounded-xl bg-white">
	                  <table class="w-full text-xs font-sans text-left">
	                    <thead>
	                      <tr class="bg-gray-50 border-b border-gray-100 text-brand-secondary uppercase font-mono text-[10px] tracking-wider">
	                        <th class="p-3">密钥名称</th>
	                        <th class="p-3">供应商</th>
	                        <th class="p-3">模型 / 服务</th>
	                        <th class="p-3">脱敏值</th>
	                        <th class="p-3">真实 Key</th>
	                        <th class="p-3">启用状态</th>
	                        <th class="p-3">优先级</th>
	                        <th class="p-3">并发</th>
	                        <th class="p-3">可用槽位</th>
	                        <th class="p-3">冷却</th>
	                        <th class="p-3">备注</th>
	                        <th class="p-3 text-right">操作</th>
	                      </tr>
	                    </thead>
	                    <tbody class="divide-y divide-gray-100">
	                      <tr v-for="item in llmKeys" :key="item.key_id" class="hover:bg-brand-paper/50">
	                        <td class="p-3 font-bold text-brand-ink-strong">{{ item.display_name }}</td>
	                        <td class="p-3 font-mono text-brand-secondary">{{ serviceKeyProviderLabel(item.provider) }}</td>
	                        <td class="p-3 font-mono text-brand-secondary">{{ serviceKeyModelLabel(item.provider, item.model) }}</td>
	                        <td class="p-3 font-mono text-brand-ink-strong">{{ item.masked_key }}</td>
	                        <td class="p-3">
	                          <span class="text-[10px] px-2 py-1 rounded-full border" :class="item.secret_configured ? 'bg-emerald-50 text-emerald-600 border-emerald-100' : 'bg-amber-50 text-amber-700 border-amber-100'">
	                            {{ item.secret_configured ? '已配置' : '未配置' }}
	                          </span>
	                        </td>
	                        <td class="p-3">{{ item.enabled ? '启用' : '停用' }}</td>
	                        <td class="p-3 font-mono text-brand-secondary">{{ item.priority }}</td>
	                        <td class="p-3 font-mono text-brand-ink-strong">{{ item.current_inflight }} / {{ item.max_concurrency }}</td>
	                        <td class="p-3 font-mono text-emerald-600 font-bold">{{ item.available_slots }}</td>
	                        <td class="p-3 font-mono text-brand-secondary">{{ formatTime(item.cooldown_until) }}</td>
	                        <td class="p-3 text-brand-secondary">{{ item.remark || '--' }}</td>
	                        <td class="p-3 text-right">
                          <div class="flex justify-end gap-2">
                            <button @click="beginEditLlmKey(item)" class="text-brand-primary font-bold">编辑</button>
                            <button @click="removeLlmKey(item.key_id)" class="text-red-500 font-bold">删除</button>
                          </div>
                        </td>
	                      </tr>
	                      <tr v-if="!llmLoading && llmKeys.length === 0">
	                        <td colspan="12" class="p-8 text-center text-brand-secondary font-mono">暂无服务密钥配置。系统将继续读取服务器环境变量。</td>
	                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      <div v-if="selectedRechargePackageDraft && rechargePackageEditIndex !== null" class="fixed inset-0 z-[60] bg-slate-950/35 backdrop-blur-sm px-4 py-6 flex items-center justify-center">
        <div class="w-full max-w-md bg-white border border-gray-100 rounded-2xl shadow-2xl overflow-hidden flex flex-col text-left">
          <div class="px-5 py-4 border-b border-gray-100 flex items-start justify-between gap-4">
            <div>
              <p class="text-[10px] font-mono text-brand-secondary uppercase font-bold">Recharge Package</p>
              <h2 class="font-serif text-lg font-bold text-brand-ink-strong">编辑充值套餐 {{ rechargePackageEditIndex + 1 }}</h2>
            </div>
            <button
              type="button"
              @click="closeRechargePackageEditor"
              class="w-8 h-8 rounded-lg bg-brand-paper hover:bg-gray-100 text-brand-ink-strong border border-gray-100 flex items-center justify-center shrink-0"
              title="关闭"
            >
              <X :size="15" />
            </button>
          </div>

          <div class="p-5 space-y-4">
            <div class="grid grid-cols-2 gap-3">
              <label class="space-y-1 block">
                <span class="text-[10.5px] font-bold text-brand-secondary">人民币金额</span>
                <input
                  v-model.number="selectedRechargePackageDraft.price_yuan"
                  @input="rechargePackagesDirty = true"
                  type="number"
                  min="0"
                  step="0.01"
                  class="w-full bg-gray-50 border border-gray-100 rounded-lg px-2.5 py-2 text-xs font-mono outline-none focus:border-brand-primary"
                  placeholder="9.9"
                />
              </label>
              <label class="space-y-1 block">
                <span class="text-[10.5px] font-bold text-brand-secondary">积分数量</span>
                <input
                  v-model.number="selectedRechargePackageDraft.points_amount"
                  @input="rechargePackagesDirty = true"
                  type="number"
                  min="1"
                  class="w-full bg-gray-50 border border-gray-100 rounded-lg px-2.5 py-2 text-xs font-mono outline-none focus:border-brand-primary"
                  placeholder="1000"
                />
              </label>
            </div>

            <label class="space-y-1 block">
              <span class="text-[10.5px] font-bold text-brand-secondary">启用状态</span>
              <AdminSelect
                v-model="selectedRechargePackageDraft.enabled"
                @change="rechargePackagesDirty = true"
                :options="booleanToggleSelectOptions"
                min-width-class="w-full"
                panel-width-class="w-full"
              />
            </label>

            <div class="grid grid-cols-2 gap-2">
              <button
                type="button"
                @click="moveRechargePackageDraft(rechargePackageEditIndex, rechargePackageEditIndex - 1)"
                :disabled="rechargePackageEditIndex === 0"
                class="bg-white border border-gray-100 text-brand-secondary px-3 py-2 rounded-lg text-[11px] font-bold flex items-center justify-center gap-1.5 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-brand-paper"
              >
                <ArrowUp :size="13" />
                <span>上移</span>
              </button>
              <button
                type="button"
                @click="moveRechargePackageDraft(rechargePackageEditIndex, rechargePackageEditIndex + 1)"
                :disabled="rechargePackageEditIndex >= rechargePackageDrafts.length - 1"
                class="bg-white border border-gray-100 text-brand-secondary px-3 py-2 rounded-lg text-[11px] font-bold flex items-center justify-center gap-1.5 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-brand-paper"
              >
                <ArrowDown :size="13" />
                <span>下移</span>
              </button>
            </div>
          </div>

          <div class="px-5 py-4 border-t border-gray-100 bg-gray-50/60 flex flex-wrap items-center justify-between gap-3">
            <button
              type="button"
              @click="removeRechargePackageDraft(rechargePackageEditIndex)"
              class="bg-red-50 border border-red-100 text-red-600 px-3 py-2 rounded-lg text-[11px] font-bold"
            >
              删除套餐
            </button>
            <button
              type="button"
              @click="closeRechargePackageEditor"
              class="ml-auto bg-brand-primary hover:bg-brand-primary-strong text-white px-4 py-2 rounded-lg text-xs font-bold shadow-sm shadow-brand-primary/10"
            >
              完成
            </button>
          </div>
        </div>
      </div>

      <div v-if="phoneReviewAspectConfigModal" class="fixed inset-0 z-[60] bg-slate-950/35 backdrop-blur-sm px-4 py-6 flex items-center justify-center">
        <div class="w-full max-w-2xl max-h-[88vh] bg-white border border-gray-100 rounded-2xl shadow-2xl overflow-hidden flex flex-col text-left">
          <div class="px-5 py-4 border-b border-gray-100 flex items-start justify-between gap-4">
            <div>
              <p class="text-[10px] font-mono text-brand-secondary uppercase font-bold">Phone Review Aspect Config</p>
              <h2 class="font-serif text-lg font-bold text-brand-ink-strong">
                {{ phoneReviewAspectConfigModal === 'free' ? '免费专项' : '专项顺序' }}
              </h2>
            </div>
            <button
              type="button"
              @click="closePhoneReviewAspectConfigModal"
              class="w-8 h-8 rounded-lg bg-brand-paper hover:bg-gray-100 text-brand-ink-strong border border-gray-100 flex items-center justify-center shrink-0"
              title="关闭"
            >
              <X :size="15" />
            </button>
          </div>

          <div class="p-5 overflow-y-auto">
            <div v-if="phoneReviewAspectConfigModal === 'free'" class="grid grid-cols-2 sm:grid-cols-3 gap-2">
              <button
                v-for="aspect in PHONE_REVIEW_ASPECT_OPTIONS"
                :key="aspect.key"
                type="button"
                @click="togglePhoneReviewFreeAspect(aspect.key)"
                class="rounded-xl border px-3 py-2.5 text-left transition-colors min-h-[58px]"
                :class="isPhoneReviewFreeAspect(aspect.key) ? 'bg-emerald-50 border-emerald-100 text-emerald-700 shadow-sm' : 'bg-white border-gray-100 text-brand-ink-strong hover:bg-brand-paper/60'"
              >
                <span class="block text-sm font-bold">{{ aspect.label }}</span>
                <span class="block text-[10px] mt-1 font-mono">{{ isPhoneReviewFreeAspect(aspect.key) ? '免费' : '收费' }}</span>
              </button>
            </div>

            <div v-else class="space-y-2">
              <div
                v-for="aspect in phoneReviewOrderedAspectOptions"
                :key="aspect.key"
                class="grid grid-cols-[minmax(0,1fr)_36px_36px] gap-2 items-center"
              >
                <button
                  type="button"
                  @click="togglePhoneReviewFreeAspect(aspect.key)"
                  class="rounded-xl border px-3 py-2 text-left transition-colors"
                  :class="aspect.is_free ? 'bg-emerald-50 border-emerald-100 text-emerald-700' : 'bg-white border-gray-100 text-brand-ink-strong hover:bg-brand-paper/60'"
                >
                  <span class="flex items-center justify-between gap-3">
                    <span class="text-sm font-bold">{{ aspect.index + 1 }}. {{ aspect.label }}</span>
                    <span class="text-[10px] font-mono">{{ aspect.is_free ? '免费' : '收费' }}</span>
                  </span>
                </button>
                <button
                  type="button"
                  @click="movePhoneReviewAspectOrder(aspect.key, -1)"
                  :disabled="aspect.index === 0"
                  class="w-9 h-9 rounded-xl border border-gray-100 bg-white text-brand-secondary flex items-center justify-center disabled:opacity-30 disabled:cursor-not-allowed hover:bg-brand-paper"
                  title="上移"
                >
                  <ArrowUp :size="14" />
                </button>
                <button
                  type="button"
                  @click="movePhoneReviewAspectOrder(aspect.key, 1)"
                  :disabled="aspect.index === phoneReviewOrderedAspectOptions.length - 1"
                  class="w-9 h-9 rounded-xl border border-gray-100 bg-white text-brand-secondary flex items-center justify-center disabled:opacity-30 disabled:cursor-not-allowed hover:bg-brand-paper"
                  title="下移"
                >
                  <ArrowDown :size="14" />
                </button>
              </div>
            </div>
          </div>

          <div class="px-5 py-4 border-t border-gray-100 flex flex-wrap items-center justify-between gap-3 bg-gray-50/60">
            <button
              v-if="phoneReviewAspectConfigModal === 'free'"
              type="button"
              @click="resetPhoneReviewFreeAspects"
              class="bg-white border border-gray-100 text-brand-secondary px-3 py-2 rounded-lg text-[11px] font-bold flex items-center gap-1.5"
            >
              <RotateCcw :size="13" />
              <span>清空免费</span>
            </button>
            <button
              v-else
              type="button"
              @click="resetPhoneReviewAspectOrder"
              class="bg-white border border-gray-100 text-brand-secondary px-3 py-2 rounded-lg text-[11px] font-bold flex items-center gap-1.5"
            >
              <RotateCcw :size="13" />
              <span>恢复默认顺序</span>
            </button>
            <button
              type="button"
              @click="closePhoneReviewAspectConfigModal"
              class="ml-auto bg-brand-primary hover:bg-brand-primary-strong text-white px-4 py-2 rounded-lg text-xs font-bold shadow-sm shadow-brand-primary/10"
            >
              完成
            </button>
          </div>
        </div>
      </div>

      <div v-if="selectedUser" class="fixed inset-0 z-50 bg-slate-950/35 backdrop-blur-sm px-4 py-6 flex items-center justify-center">
        <div class="w-full max-w-6xl max-h-[92vh] bg-white border border-gray-100 rounded-3xl shadow-2xl overflow-hidden flex flex-col text-left">
          <div class="px-6 py-5 border-b border-gray-100 flex flex-wrap items-start justify-between gap-5 bg-white">
            <div class="min-w-0 shrink-0 lg:w-[34%] flex items-center gap-3">
              <div class="relative w-12 h-12 rounded-2xl bg-brand-primary/10 text-brand-primary font-serif font-black flex items-center justify-center text-lg overflow-hidden border border-brand-primary/10 shrink-0">
                <span>{{ userAvatarInitial(selectedUser.user) }}</span>
                <img
                  v-if="userAvatarUrl(selectedUser.user)"
                  :src="userAvatarUrl(selectedUser.user)"
                  alt=""
                  class="absolute inset-0 w-full h-full object-cover"
                  @error="handleUserAvatarError"
                />
              </div>
              <div class="min-w-0">
                <p class="text-[10px] font-mono text-brand-secondary uppercase font-bold">User Operation File</p>
                <h2 class="font-serif text-xl font-bold text-brand-ink-strong truncate">{{ selectedUser.user.nickname || '未命名用户' }}</h2>
                <p class="font-mono text-[11px] text-brand-secondary select-all">{{ selectedUser.user.uid ? `UID ${selectedUser.user.uid}` : selectedUser.user.user_id }}</p>
              </div>
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

      <aside v-if="selectedPhoneReview" class="fixed top-0 right-0 w-full max-w-3xl bg-white border-l border-gray-100 h-full flex flex-col p-6 shadow-2xl text-left overflow-y-auto z-50">
        <div class="flex items-start justify-between gap-4 pb-4 border-b border-gray-100">
          <div class="min-w-0">
            <p class="text-[10px] font-mono text-brand-secondary uppercase font-bold">Phone Qimen Review Detail</p>
            <h2 class="font-serif text-lg font-bold text-brand-ink-strong">
              {{ selectedPhoneReview.review.phone }} · {{ genderLabel(selectedPhoneReview.review.gender) }}
            </h2>
            <p class="font-mono text-[11px] text-brand-secondary select-all truncate">{{ selectedPhoneReview.review.review_id }}</p>
          </div>
          <button @click="selectedPhoneReview = null" class="bg-brand-paper hover:bg-gray-100 text-brand-ink-strong text-xs px-3 py-1.5 rounded-lg border border-gray-100 shrink-0">关闭</button>
        </div>

        <div class="space-y-6 py-5 text-xs text-brand-secondary">
          <section class="space-y-3">
            <div class="flex flex-wrap items-center justify-between gap-3">
              <h3 class="font-bold text-brand-ink-strong">本次评测基本信息</h3>
              <span class="px-2 py-0.5 rounded text-[9px] font-bold inline-block border" :class="usageStatusClass(selectedPhoneReview.review.status)">
                {{ reviewStatusLabel(selectedPhoneReview.review.status) }}
              </span>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div class="bg-gray-50 rounded-xl border border-gray-100 p-3">
                <span class="block text-[10px] uppercase font-bold">用户</span>
                <span class="font-semibold text-brand-ink-strong">{{ selectedPhoneReview.review.user_nickname || selectedPhoneReview.review.user_phone || selectedPhoneReview.review.user_uid || '--' }}</span>
                <button
                  v-if="selectedPhoneReview.review.user_id"
                  @click="jumpToNullableUser(selectedPhoneReview.review.user_id)"
                  class="block mt-1 text-[10.5px] text-brand-primary font-bold"
                >
                  打开用户管理
                </button>
              </div>
              <div class="bg-gray-50 rounded-xl border border-gray-100 p-3">
                <span class="block text-[10px] uppercase font-bold">基础积分消耗</span>
                <span class="font-semibold text-brand-primary font-mono">{{ selectedPhoneReview.review.base_points_cost }} pt</span>
              </div>
              <div class="bg-gray-50 rounded-xl border border-gray-100 p-3">
                <span class="block text-[10px] uppercase font-bold">生成耗时</span>
                <span class="font-semibold text-brand-ink-strong font-mono">{{ formatDuration(selectedPhoneReview.review.generation_duration_seconds) }}</span>
              </div>
              <div class="bg-gray-50 rounded-xl border border-gray-100 p-3">
                <span class="block text-[10px] uppercase font-bold">提交时间</span>
                <span class="font-semibold text-brand-ink-strong font-mono">{{ formatTime(selectedPhoneReview.review.created_at) }}</span>
              </div>
              <div class="bg-gray-50 rounded-xl border border-gray-100 p-3">
                <span class="block text-[10px] uppercase font-bold">完成 / 更新时间</span>
                <span class="font-semibold text-brand-ink-strong font-mono">{{ formatTime(selectedPhoneReview.review.updated_at) }}</span>
              </div>
              <div class="bg-gray-50 rounded-xl border border-gray-100 p-3">
                <span class="block text-[10px] uppercase font-bold">渠道</span>
                <span class="font-semibold text-brand-ink-strong">{{ selectedPhoneReview.review.channel || '--' }}</span>
              </div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div class="bg-white rounded-xl border border-gray-100 p-3">
                <div class="flex items-center justify-between gap-2">
                  <span class="text-[10px] uppercase font-bold">评测 ID</span>
                  <button @click="copyText(selectedPhoneReview.review.review_id, '评测 ID')" class="text-[10.5px] text-brand-primary font-bold">复制</button>
                </div>
                <p class="font-mono text-brand-ink-strong break-all mt-1 select-all">{{ selectedPhoneReview.review.review_id }}</p>
              </div>
              <div class="bg-white rounded-xl border border-gray-100 p-3">
                <div class="flex items-center justify-between gap-2">
                  <span class="text-[10px] uppercase font-bold">用户 ID</span>
                  <button v-if="selectedPhoneReview.review.user_id" @click="copyText(selectedPhoneReview.review.user_id, '用户 ID')" class="text-[10.5px] text-brand-primary font-bold">复制</button>
                </div>
                <p class="font-mono text-brand-ink-strong break-all mt-1 select-all">{{ selectedPhoneReview.review.user_id || '--' }}</p>
              </div>
            </div>
            <div v-if="selectedPhoneReview.review.error_message" class="bg-red-50 border border-red-100 rounded-xl p-3 text-red-600">
              失败原因：{{ selectedPhoneReview.review.error_message }}
            </div>
          </section>

          <section class="space-y-3 border-t border-gray-100 pt-5">
            <div class="flex items-center justify-between gap-3">
              <h3 class="font-bold text-brand-ink-strong">专项解锁记录</h3>
              <span class="font-mono text-[10px] text-brand-secondary">{{ selectedPhoneReview.unlock_records.length }} 条</span>
            </div>
            <div class="overflow-x-auto border border-gray-100 rounded-xl bg-white">
              <table class="w-full text-xs">
                <thead class="bg-gray-50 text-brand-secondary font-mono text-[10px] uppercase">
                  <tr>
                    <th class="p-3 text-left">专项</th>
                    <th class="p-3 text-right">消耗积分</th>
                    <th class="p-3 text-left">解锁时间</th>
                    <th class="p-3 text-left">流水</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-100">
                  <tr v-for="unlock in selectedPhoneReview.unlock_records" :key="unlock.unlock_id">
                    <td class="p-3 font-bold text-brand-ink-strong">{{ unlock.aspect_name || aspectLabel(unlock.aspect_key) }}</td>
                    <td class="p-3 text-right font-mono text-brand-primary">{{ unlock.points_cost }}</td>
                    <td class="p-3 font-mono text-brand-secondary">{{ formatTime(unlock.unlocked_at) }}</td>
                    <td class="p-3 font-mono text-brand-secondary" :title="unlock.usage_record_id || '--'">{{ shortText(unlock.usage_record_id, 8, 4) }}</td>
                  </tr>
                  <tr v-if="selectedPhoneReview.unlock_records.length === 0">
                    <td colspan="4" class="p-6 text-center text-brand-secondary font-mono">暂无专项解锁记录</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          <section class="space-y-3 border-t border-gray-100 pt-5">
            <div class="flex items-center justify-between gap-3">
              <h3 class="font-bold text-brand-ink-strong">语音播报记录</h3>
              <span class="font-mono text-[10px] text-brand-secondary">{{ selectedPhoneReview.voice_records.length }} 条</span>
            </div>
            <div class="overflow-x-auto border border-gray-100 rounded-xl bg-white">
              <table class="w-full text-xs">
                <thead class="bg-gray-50 text-brand-secondary font-mono text-[10px] uppercase">
                  <tr>
                    <th class="p-3 text-left">场景</th>
                    <th class="p-3 text-left">状态</th>
                    <th class="p-3 text-left">供应商</th>
                    <th class="p-3 text-left">音色</th>
                    <th class="p-3 text-left">缓存</th>
                    <th class="p-3 text-left">失败原因</th>
                    <th class="p-3 text-left">生成时间</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-100">
                  <tr v-for="record in selectedPhoneReview.voice_records" :key="record.usage_record_id">
                    <td class="p-3 font-bold text-brand-ink-strong">{{ voiceSceneLabel(record) }}</td>
                    <td class="p-3">
                      <span class="px-2 py-0.5 rounded text-[9px] font-bold inline-block border" :class="usageStatusClass(record.status)">
                        {{ record.status }}
                      </span>
                    </td>
                    <td class="p-3 font-mono text-brand-secondary">{{ voiceRecordField(record, 'provider') }}</td>
                    <td class="p-3 font-mono text-brand-secondary">{{ voiceRecordField(record, 'voice_key') }}</td>
                    <td class="p-3 text-brand-secondary">{{ voiceCachedLabel(record) }}</td>
                    <td class="p-3 text-red-500 max-w-44 truncate" :title="voiceFailureText(record)">{{ voiceFailureText(record) }}</td>
                    <td class="p-3 font-mono text-brand-secondary">{{ formatTime(record.created_at) }}</td>
                  </tr>
                  <tr v-if="selectedPhoneReview.voice_records.length === 0">
                    <td colspan="7" class="p-6 text-center text-brand-secondary font-mono">暂无语音播报记录</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>
        </div>
      </aside>

      <aside v-if="selectedPointsClaimLink" class="fixed top-0 right-0 w-full max-w-3xl bg-white border-l border-gray-100 h-full flex flex-col p-6 shadow-2xl text-left overflow-y-auto z-50">
        <div class="flex items-start justify-between gap-4 pb-4 border-b border-gray-100">
          <div class="min-w-0">
            <p class="text-[10px] font-mono text-brand-secondary uppercase font-bold">Points Claim Link</p>
            <h2 class="font-serif text-lg font-bold text-brand-ink-strong truncate">{{ selectedPointsClaimLink.title }}</h2>
            <p class="font-mono text-[11px] text-brand-secondary select-all break-all">{{ selectedPointsClaimLink.claim_link_id }}</p>
          </div>
          <button @click="selectedPointsClaimLink = null" class="bg-brand-paper hover:bg-gray-100 text-brand-ink-strong text-xs px-3 py-1.5 rounded-lg border border-gray-100 shrink-0">关闭</button>
        </div>

        <div class="space-y-5 py-5 text-xs text-brand-secondary">
          <section class="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div class="bg-gray-50 rounded-xl border border-gray-100 p-3">
              <span class="block text-[10px] uppercase font-bold">当前状态</span>
              <span class="mt-1 px-2 py-0.5 rounded text-[9px] font-bold inline-block border" :class="pointsClaimStatusClass(selectedPointsClaimLink.effective_status)">
                {{ pointsClaimStatusLabel(selectedPointsClaimLink.effective_status) }}
              </span>
            </div>
            <div class="bg-gray-50 rounded-xl border border-gray-100 p-3">
              <span class="block text-[10px] uppercase font-bold">领取额度</span>
              <span class="font-semibold text-brand-primary font-mono">{{ selectedPointsClaimLink.points_amount }} pt</span>
            </div>
            <div class="bg-gray-50 rounded-xl border border-gray-100 p-3">
              <span class="block text-[10px] uppercase font-bold">人民币价值</span>
              <span class="font-semibold text-emerald-600 font-mono">{{ formatClaimMoney(selectedPointsClaimLink.display_value_cents) }}</span>
            </div>
            <div class="bg-gray-50 rounded-xl border border-gray-100 p-3">
              <span class="block text-[10px] uppercase font-bold">重复访问</span>
              <span class="font-semibold text-amber-700 font-mono">{{ selectedPointsClaimLink.duplicate_attempt_count }}</span>
            </div>
          </section>

          <section class="space-y-3 border border-gray-100 rounded-xl p-4 bg-white">
            <div class="flex flex-wrap items-center justify-between gap-3">
              <h3 class="font-bold text-brand-ink-strong">链接信息</h3>
              <div class="flex flex-wrap gap-2">
                <button @click="copyText(formatClaimUrl(selectedPointsClaimLink), '领取链接')" class="bg-brand-primary text-white px-3 py-1.5 rounded-lg text-[10.5px] font-bold flex items-center gap-1.5">
                  <Copy :size="12" />
                  <span>复制链接</span>
                </button>
                <a :href="formatClaimUrl(selectedPointsClaimLink)" target="_blank" rel="noreferrer" class="bg-white border border-gray-100 text-brand-primary px-3 py-1.5 rounded-lg text-[10.5px] font-bold flex items-center gap-1.5">
                  <ExternalLink :size="12" />
                  <span>打开</span>
                </a>
                <button
                  v-if="selectedPointsClaimLink.effective_status !== 'disabled'"
                  @click="disablePointsClaimLink(selectedPointsClaimLink)"
                  class="bg-red-50 border border-red-100 text-red-600 px-3 py-1.5 rounded-lg text-[10.5px] font-bold flex items-center gap-1.5"
                >
                  <XCircle :size="12" />
                  <span>停用</span>
                </button>
              </div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div class="bg-brand-paper/40 border border-gray-100 rounded-xl p-3">
                <span class="block text-[10px] uppercase font-bold">领取地址</span>
                <p class="font-mono text-brand-ink-strong break-all mt-1 select-all">{{ formatClaimUrl(selectedPointsClaimLink) }}</p>
              </div>
              <div class="bg-brand-paper/40 border border-gray-100 rounded-xl p-3">
                <span class="block text-[10px] uppercase font-bold">链接码</span>
                <p class="font-mono text-brand-ink-strong break-all mt-1 select-all">{{ selectedPointsClaimLink.claim_code }}</p>
              </div>
              <div class="bg-brand-paper/40 border border-gray-100 rounded-xl p-3">
                <span class="block text-[10px] uppercase font-bold">生效时间</span>
                <p class="font-mono text-brand-ink-strong mt-1">{{ formatTime(selectedPointsClaimLink.valid_from) }}</p>
              </div>
              <div class="bg-brand-paper/40 border border-gray-100 rounded-xl p-3">
                <span class="block text-[10px] uppercase font-bold">过期时间</span>
                <p class="font-mono text-brand-ink-strong mt-1">{{ formatTime(selectedPointsClaimLink.expires_at) }}</p>
              </div>
            </div>
            <p v-if="selectedPointsClaimLink.operator_note" class="text-[11px] text-brand-secondary leading-relaxed">
              内部备注：{{ selectedPointsClaimLink.operator_note }}
            </p>
          </section>

          <section class="space-y-3 border-t border-gray-100 pt-5">
            <div class="flex flex-wrap items-center justify-between gap-3">
              <h3 class="font-bold text-brand-ink-strong">领取动作记录</h3>
              <span class="font-mono text-[10px] text-brand-secondary">成功 {{ selectedPointsClaimLink.claimed_user_count }} · 重复 {{ selectedPointsClaimLink.duplicate_attempt_count }}</span>
            </div>

            <div class="flex flex-wrap items-center justify-between gap-2">
              <div class="flex flex-wrap gap-2">
                <AdminSelect
                  v-model="pointsClaimRecordsFilters.status"
                  :options="pointsClaimRecordStatusSelectOptions"
                  min-width-class="min-w-[132px]"
                  panel-width-class="w-44"
                />
                <input v-model="pointsClaimRecordsFilters.user_id" class="bg-gray-50 border border-gray-100 p-2.5 rounded-lg text-xs text-brand-ink-strong outline-none focus:border-brand-primary w-56" placeholder="用户 ID 精确筛选" />
              </div>
              <div class="flex gap-2">
                <button @click="resetPointsClaimRecordsFilters(); loadPointsClaimRecords({resetPage: true})" class="bg-white border border-gray-100 text-brand-secondary px-3 py-2 rounded-xl text-[10.5px] font-bold hover:bg-gray-50">
                  重置
                </button>
                <button @click="searchPointsClaimRecords" class="bg-brand-primary text-white px-3 py-2 rounded-xl text-[10.5px] font-bold hover:bg-brand-primary-strong">
                  {{ pointsClaimRecordsLoading ? '查询中...' : '查询记录' }}
                </button>
              </div>
            </div>

            <div v-if="pointsClaimRecordsError" class="text-xs text-red-600 bg-red-50 border border-red-100 rounded-xl px-3 py-2">
              {{ pointsClaimRecordsError }}
            </div>

            <div class="overflow-x-auto border border-gray-100 rounded-xl bg-white">
              <table class="w-full table-fixed text-xs font-sans text-left">
                <colgroup>
                  <col class="w-[150px]" />
                  <col class="w-[112px]" />
                  <col class="w-[96px]" />
                  <col class="w-[116px]" />
                  <col class="w-[142px]" />
                  <col class="w-[96px]" />
                </colgroup>
                <thead>
                  <tr class="bg-gray-50 border-b border-gray-100 text-brand-secondary uppercase font-mono text-[10px] tracking-wider">
                    <th class="px-3 py-2.5">用户</th>
                    <th class="px-3 py-2.5">状态</th>
                    <th class="px-3 py-2.5 text-right">额度快照</th>
                    <th class="px-3 py-2.5">周周期</th>
                    <th class="px-3 py-2.5">访问时间</th>
                    <th class="px-3 py-2.5 text-right">用户档案</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-100">
                  <tr v-for="record in selectedPointsClaimRecords" :key="record.claim_record_id" class="hover:bg-brand-paper/50">
                    <td class="px-3 py-2.5 align-top">
                      <div class="font-bold text-brand-ink-strong leading-snug break-words" :title="record.user_nickname || record.user_phone || record.user_uid || record.user_id">
                        {{ record.user_nickname || record.user_phone || record.user_uid || '未命名用户' }}
                      </div>
                      <div class="text-[10px] text-brand-secondary font-mono break-all">{{ record.user_uid ? `UID ${record.user_uid}` : shortText(record.user_id, 8, 4) }}</div>
                    </td>
                    <td class="px-3 py-2.5 align-top">
                      <span class="px-2 py-0.5 rounded text-[9px] font-bold inline-block border" :class="pointsClaimStatusClass(record.status)">
                        {{ pointsClaimStatusLabel(record.status) }}
                      </span>
                      <div class="text-[10px] text-brand-secondary mt-1 leading-snug">{{ pointsClaimRecordFailureLabel(record) }}</div>
                    </td>
                    <td class="px-3 py-2.5 align-top text-right">
                      <div class="font-mono text-brand-primary font-bold">{{ record.points_amount_snapshot }} pt</div>
                      <div class="font-mono text-brand-secondary text-[10px]">{{ formatClaimMoney(record.display_value_cents_snapshot) }}</div>
                    </td>
                    <td class="px-3 py-2.5 align-top font-mono text-brand-secondary">
                      <div>{{ record.week_key }}</div>
                      <div class="text-[10px]">{{ formatTime(record.week_starts_at) }}</div>
                    </td>
                    <td class="px-3 py-2.5 align-top font-mono text-brand-secondary">{{ formatTime(record.created_at) }}</td>
                    <td class="px-3 py-2.5 align-top text-right">
                      <button @click="jumpToNullableUser(record.user_id)" class="bg-white border border-gray-100 text-brand-primary px-2.5 py-1.5 rounded-lg text-[10.5px] font-bold">
                        查看用户
                      </button>
                    </td>
                  </tr>
                  <tr v-if="!pointsClaimRecordsLoading && selectedPointsClaimRecords.length === 0">
                    <td colspan="6" class="p-8 text-center text-brand-secondary font-mono">暂无领取动作记录</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-gray-100 text-xs text-brand-secondary">
              <div class="font-mono">
                显示 {{ pointsClaimRecordsPageStart }}-{{ pointsClaimRecordsPageEnd }} / {{ pointsClaimRecordsTotal }}，每页 {{ pointsClaimRecordsPageSize }} 条
              </div>
              <div class="flex items-center gap-2">
                <button
                  @click="changePointsClaimRecordsPage(-1)"
                  :disabled="!canGoPrevPointsClaimRecordsPage"
                  class="bg-white border border-gray-100 text-brand-ink-strong px-3 py-1.5 rounded-lg text-[10.5px] font-bold disabled:opacity-40 disabled:cursor-not-allowed hover:bg-brand-paper"
                >
                  上一页
                </button>
                <span class="font-mono text-[11px] text-brand-secondary px-2">
                  第 {{ pointsClaimRecordsCurrentPage }} / {{ pointsClaimRecordsTotalPages }} 页
                </span>
                <button
                  @click="changePointsClaimRecordsPage(1)"
                  :disabled="!canGoNextPointsClaimRecordsPage"
                  class="bg-white border border-gray-100 text-brand-ink-strong px-3 py-1.5 rounded-lg text-[10.5px] font-bold disabled:opacity-40 disabled:cursor-not-allowed hover:bg-brand-paper"
                >
                  下一页
                </button>
              </div>
            </div>
          </section>
        </div>
      </aside>

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
            <h3 class="font-bold text-brand-ink-strong">LLM 运行字段</h3>
            <p>Key：{{ selectedUsage.record.llm_key_name || selectedUsage.record.llm_key_id || '--' }}</p>
            <p>模型：{{ selectedUsage.record.llm_model || '--' }}</p>
            <p>优先级：{{ selectedUsage.record.llm_priority_class || '--' }}</p>
            <p>等待 / 响应：{{ selectedUsage.record.llm_wait_ms ?? '--' }} ms / {{ selectedUsage.record.llm_duration_ms ?? '--' }} ms</p>
            <p>重试次数：{{ selectedUsage.record.llm_retry_count }}</p>
            <p>错误：{{ selectedUsage.record.llm_error_type || '--' }} {{ selectedUsage.record.llm_error_message || '' }}</p>
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
            <textarea v-model="orderReviewNote" class="w-full bg-gray-50 border border-gray-100 rounded-xl p-3 text-xs outline-none min-h-20" placeholder="操作说明（线下收款确认 / 退款备注）"></textarea>
            <input v-model="orderRefundReason" class="w-full bg-gray-50 border border-gray-100 rounded-xl p-2.5 text-xs outline-none" placeholder="退款原因（创建退款请求时使用）" />
            <div class="flex flex-wrap gap-2">
              <button v-if="canManualCompleteOrder(selectedOrder)" @click="manualCompleteSelectedOrder" class="bg-brand-primary text-white px-3 py-1.5 rounded-lg text-[10.5px] font-bold">确认已线下收款并完成订单</button>
              <button v-if="canManualCompleteOrder(selectedOrder)" @click="reviewSelectedOrder('reject')" class="bg-white border border-gray-100 text-brand-secondary px-3 py-1.5 rounded-lg text-[10.5px] font-bold">拒绝订单</button>
              <span v-else class="bg-gray-50 border border-gray-100 text-brand-secondary px-3 py-1.5 rounded-lg text-[10.5px] font-bold">当前状态不可手动完成</span>
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
