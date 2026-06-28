<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import {
  Camera,
  ChevronRight,
  Receipt,
  History,
  MessageSquare,
  Share2,
  X,
  AlertTriangle,
  RefreshCw,
  LogOut,
  LogIn,
  PencilLine,
  KeyRound,
} from 'lucide-vue-next';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';
import { resolveApiAssetUrl } from '../../lib/api';
import type { FourPillarsReviewSummary, PointsLedgerEntryResponse, ReviewSummary } from '../../types/api';
import SystemIntro from './SystemIntro.vue';

const emit = defineEmits<{
  (e: 'navigate-to-tab', tab: string, params?: Record<string, string | number | undefined>): void;
}>();

type CombinedReviewHistoryItem =
  | (ReviewSummary & { type: 'phone' })
  | (FourPillarsReviewSummary & { type: 'bazi' });

const {
  state,
  bootstrapApp,
  refreshPointsLedger,
  refreshReviewHistory,
  refreshFourPillarsHistory,
  refreshCurrentReview,
  refreshCurrentFourPillarsReview,
  logout,
  updateProfile,
  uploadAvatar,
  changePassword,
  displayNickname,
  displayAvatarText,
  isGuestUser,
  isRegisteredUser,
  requestRegisteredUser,
  openCustomerServiceModal,
  humanizeError,
} = useEaseWiseApp();

const activeModal = ref<string | null>(null);
const feedbackText = ref('');
const showSystemIntro = ref(false);
const openingReviewId = ref<string | null>(null);
const historyActionError = ref('');
const profileEditorVisible = ref(false);
const profileNicknameDraft = ref('');
const profileSaveError = ref('');
const profileSaving = ref(false);
const avatarInputRef = ref<HTMLInputElement | null>(null);
const avatarUploading = ref(false);
const avatarUploadError = ref('');
const avatarImageFailed = ref(false);
const passwordEditorVisible = ref(false);
const currentPasswordDraft = ref('');
const newPasswordDraft = ref('');
const confirmPasswordDraft = ref('');
const passwordSaveError = ref('');
const passwordSaveSuccess = ref('');
const passwordSaving = ref(false);
const logoutSaving = ref(false);
const logoutError = ref('');

const currentPoints = computed(() => state.points?.balance ?? 0);
const reportHistory = computed(() => state.reviewHistory);
const combinedHistory = computed<CombinedReviewHistoryItem[]>(() => {
  const phoneItems = state.reviewHistory.map((item) => ({
    ...item,
    type: 'phone' as const,
  }));
  const baziItems = state.fourPillarsHistory.map((item) => ({
    ...item,
    type: 'bazi' as const,
  }));
  return [...phoneItems, ...baziItems].sort((a, b) => {
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
  });
});
const ledgerRecords = computed(() => state.pointsLedger);
const userReady = computed(() => Boolean(state.user));
const profileAvatarUrl = computed(() => resolveApiAssetUrl(state.user?.avatar_url));
const profileUserUidDisplay = computed(() => state.user?.uid || '未生成');
const primaryAccountActionLabel = computed(() => (isRegisteredUser.value ? '退出登录' : '登录 / 注册'));
const profileIdentityLabel = computed(() => {
  if (!isRegisteredUser.value) {
    return '游客';
  }
  const identityLevel = state.user?.identity_level || 'normal_user';
  const identityMap: Record<string, string> = {
    normal_user: '普通用户',
    promoter: '推广大使',
    promotion_ambassador: '推广大使',
    vip_promoter: 'VIP 推广大使',
    vip_promotion_ambassador: 'VIP 推广大使',
    senior_promoter: 'VIP 推广大使',
    senior_promotion_ambassador: 'VIP 推广大使',
    svip_promoter: 'SVIP 推广大使',
    svip_promotion_ambassador: 'SVIP 推广大使',
  };
  return identityMap[identityLevel] || '普通用户';
});
const profileIdentityClass = computed(() => {
  if (profileIdentityLabel.value.startsWith('SVIP')) {
    return 'bg-gradient-to-r from-violet-600 via-pink-600 to-amber-500 text-white font-black text-[11.5px] px-4 py-1.5 rounded-full shadow-[0_8px_24px_rgba(139,92,246,0.45)] tracking-widest border-2 border-amber-300/40 uppercase';
  }
  if (profileIdentityLabel.value.startsWith('VIP')) {
    return 'bg-gradient-to-r from-rose-500 via-orange-500 to-rose-600 text-white font-black text-[11px] px-3.5 py-1.5 rounded-full shadow-[0_6px_16px_rgba(244,63,94,0.35)] tracking-wider border border-white/20';
  }
  if (profileIdentityLabel.value === '推广大使') {
    return 'bg-gradient-to-r from-[#DFB26F] via-[#F6DFA2] to-[#B38C4F] text-[#422C0A] border border-[#F6DFA2]/40 font-black text-[10.5px] px-3.5 py-1.5 rounded-full shadow-[0_4px_12px_rgba(223,178,111,0.32)] tracking-wide';
  }
  if (profileIdentityLabel.value === '普通用户') {
    return 'bg-sky-50 text-sky-700 border border-sky-200/80 text-[10.5px] font-bold px-3 py-1 rounded-full shadow-[0_2px_6px_rgba(14,165,233,0.1)]';
  }
  return 'bg-neutral-100 text-neutral-600 border border-neutral-200/60 text-[10.5px] font-medium px-2.5 py-1 rounded-full';
});
const connectionHint = computed(() => {
  if (state.connectionError) {
    return `本地 API 暂未连通：${state.connectionError}`;
  }
  return '';
});
const profileFallbackTitle = computed(() => {
  if (state.booting) {
    return '正在同步账户状态';
  }
  if (state.connectionError) {
    return '数据连接暂时不可用';
  }
  return '游客状态无法使用评测类功能及智能体';
});
const profileFallbackActionLabel = computed(() => {
  if (state.booting) {
    return '同步中';
  }
  if (state.connectionError) {
    return '重新连接';
  }
  return '登录 / 注册';
});

onMounted(() => {
  void bootstrapApp();
});

watch(
  () => state.user?.avatar_url,
  () => {
    avatarImageFailed.value = false;
  },
);

watch(activeModal, async (value) => {
  if (value !== 'history') {
    openingReviewId.value = null;
    historyActionError.value = '';
  }
  if (value === 'ledger') {
    await refreshPointsLedger().catch(() => undefined);
  }
  if (value === 'history') {
    await Promise.allSettled([
      refreshReviewHistory(),
      refreshFourPillarsHistory(),
    ]);
  }
});

async function handleProfileFallbackAction(): Promise<void> {
  if (state.booting) {
    return;
  }
  if (state.connectionError) {
    await bootstrapApp();
    return;
  }
  await requestRegisteredUser('个人中心');
}

async function handleAccountAction(): Promise<void> {
  if (!isRegisteredUser.value) {
    await requestRegisteredUser('个人中心');
    return;
  }
  logoutError.value = '';
  activeModal.value = 'logout_confirm';
}

async function confirmLogout(): Promise<void> {
  if (logoutSaving.value) {
    return;
  }
  logoutSaving.value = true;
  logoutError.value = '';
  try {
    await logout();
    activeModal.value = null;
  } catch (error) {
    logoutError.value = humanizeError(error);
  } finally {
    logoutSaving.value = false;
  }
}

async function openAvatarUploader(): Promise<void> {
  const authenticated = await requestRegisteredUser('个人中心');
  if (!authenticated) {
    return;
  }
  avatarUploadError.value = '';
  avatarInputRef.value?.click();
}

async function handleAvatarFileChange(event: Event): Promise<void> {
  if (avatarUploading.value) {
    return;
  }
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  input.value = '';
  if (!file) {
    return;
  }
  if (!/^image\/(jpeg|png|webp)$/u.test(file.type)) {
    avatarUploadError.value = '请上传 JPG、PNG 或 WebP 格式的头像。';
    return;
  }
  if (file.size > 5 * 1024 * 1024) {
    avatarUploadError.value = '头像文件请控制在 5MB 以内。';
    return;
  }

  avatarUploading.value = true;
  avatarUploadError.value = '';
  try {
    const imageDataUrl = await buildAvatarDataUrl(file);
    await uploadAvatar(imageDataUrl);
  } catch (error) {
    avatarUploadError.value = humanizeError(error);
  } finally {
    avatarUploading.value = false;
  }
}

function handleAvatarImageError(): void {
  avatarImageFailed.value = true;
}

function buildAvatarDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = () => reject(new Error('头像读取失败，请重新选择图片。'));
    reader.onload = () => {
      const image = new Image();
      image.onerror = () => reject(new Error('头像图片无法识别，请换一张图片。'));
      image.onload = () => {
        const size = 320;
        const canvas = document.createElement('canvas');
        canvas.width = size;
        canvas.height = size;
        const context = canvas.getContext('2d');
        if (!context) {
          reject(new Error('当前浏览器暂不支持头像压缩。'));
          return;
        }
        const scale = Math.max(size / image.width, size / image.height);
        const width = image.width * scale;
        const height = image.height * scale;
        context.drawImage(image, (size - width) / 2, (size - height) / 2, width, height);
        resolve(canvas.toDataURL('image/jpeg', 0.86));
      };
      image.src = String(reader.result || '');
    };
    reader.readAsDataURL(file);
  });
}

async function openProtectedModal(modal: 'ledger' | 'history'): Promise<void> {
  const authenticated = await requestRegisteredUser(modal === 'ledger' ? '积分记录' : '评测记录');
  if (authenticated) {
    activeModal.value = modal;
  }
}

async function openProfileEditor(): Promise<void> {
  const authenticated = await requestRegisteredUser('修改用户名');
  if (!authenticated) {
    return;
  }
  profileNicknameDraft.value = state.user?.nickname?.trim() || '';
  profileSaveError.value = '';
  profileEditorVisible.value = true;
}

async function submitProfileEditor(): Promise<void> {
  if (profileSaving.value) {
    return;
  }
  const nickname = profileNicknameDraft.value.trim();
  if (!nickname) {
    profileSaveError.value = '请输入用户名/昵称。';
    return;
  }
  profileSaving.value = true;
  profileSaveError.value = '';
  try {
    await updateProfile({ nickname });
    profileEditorVisible.value = false;
  } catch (error) {
    profileSaveError.value = humanizeError(error);
  } finally {
    profileSaving.value = false;
  }
}

function resetPasswordEditor(): void {
  currentPasswordDraft.value = '';
  newPasswordDraft.value = '';
  confirmPasswordDraft.value = '';
  passwordSaveError.value = '';
  passwordSaveSuccess.value = '';
  passwordSaving.value = false;
}

function closePasswordEditor(): void {
  passwordEditorVisible.value = false;
  resetPasswordEditor();
}

function validatePasswordStrength(value: string): boolean {
  if (value.trim() !== value) {
    return false;
  }
  if (value.length < 8 || value.length > 32) {
    return false;
  }
  if (new Set(value).size <= 1) {
    return false;
  }
  const categoryCount = [
    /\d/.test(value),
    /[a-zA-Z]/.test(value),
    /[^a-zA-Z0-9]/.test(value),
  ].filter(Boolean).length;
  return categoryCount >= 2;
}

async function openPasswordEditor(): Promise<void> {
  const authenticated = await requestRegisteredUser('修改密码');
  if (!authenticated) {
    return;
  }
  resetPasswordEditor();
  passwordEditorVisible.value = true;
}

async function submitPasswordEditor(): Promise<void> {
  if (passwordSaving.value) {
    return;
  }
  passwordSaveError.value = '';
  passwordSaveSuccess.value = '';

  if (!currentPasswordDraft.value.trim()) {
    passwordSaveError.value = '请输入当前密码。';
    return;
  }
  if (!validatePasswordStrength(newPasswordDraft.value)) {
    passwordSaveError.value = '新密码强度不足，请使用 8-32 位且至少包含两类字符。';
    return;
  }
  if (newPasswordDraft.value !== confirmPasswordDraft.value) {
    passwordSaveError.value = '两次输入的新密码不一致。';
    return;
  }
  if (newPasswordDraft.value === currentPasswordDraft.value) {
    passwordSaveError.value = '新密码不能与当前密码相同。';
    return;
  }

  passwordSaving.value = true;
  try {
    await changePassword(currentPasswordDraft.value, newPasswordDraft.value, confirmPasswordDraft.value);
    passwordSaveSuccess.value = '密码已更新成功，建议你立即妥善保存。';
    currentPasswordDraft.value = '';
    newPasswordDraft.value = '';
    confirmPasswordDraft.value = '';
  } catch (error) {
    passwordSaveError.value = humanizeError(error);
  } finally {
    passwordSaving.value = false;
  }
}

function handleFeedbackSubmit(): void {
  if (!feedbackText.value.trim()) {
    return;
  }
  window.alert('感谢你的反馈，我们已经记录，后续会结合产品排期继续完善。');
  feedbackText.value = '';
  activeModal.value = null;
}

function formatDateTime(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}

const ledgerBizTypeTitleMap: Record<string, string> = {
  signup_bonus: '注册赠送积分',
  wechat_initial_grant: '注册初始积分发放',
  phone_review_base: '手机号评测扣减',
  phone_review_base_charge: '手机号评测扣减',
  phone_review_base_refund: '手机号评测失败返还',
  phone_review_aspect_unlock: '手机号评测维度解锁',
  phone_review_aspect_unlock_charge: '手机号评测维度解锁',
  recharge_order: '积分充值到账',
  manual_adjust: '后台积分调整',
};

const ledgerRemarkTitleMap: Record<string, string> = {
  'initial test points': '注册赠送积分',
  wechat_initial_grant: '注册初始积分发放',
  phone_review_base_charge: '手机号评测扣减',
  phone_review_base_refund: '手机号评测失败返还',
  phone_review_aspect_unlock_charge: '手机号评测维度解锁',
  manual_adjust: '后台积分调整',
};

function hasChineseText(value: string): boolean {
  return /[\u3400-\u9fff]/u.test(value);
}

function resolveLedgerRemarkTitle(remark: string): string | null {
  const normalizedRemark = remark.trim();
  if (!normalizedRemark) {
    return null;
  }

  const lowerCaseRemark = normalizedRemark.toLowerCase();
  if (ledgerRemarkTitleMap[lowerCaseRemark]) {
    return ledgerRemarkTitleMap[lowerCaseRemark];
  }

  if (lowerCaseRemark.startsWith('recharge_order:')) {
    return '积分充值到账';
  }

  if (lowerCaseRemark.startsWith('phone_review_aspect_unlock:')) {
    return '手机号评测维度解锁';
  }

  if (hasChineseText(normalizedRemark)) {
    return normalizedRemark;
  }

  return null;
}

function formatLedgerTitle(entry: PointsLedgerEntryResponse): string {
  if (entry.remark?.trim()) {
    const resolvedRemarkTitle = resolveLedgerRemarkTitle(entry.remark);
    if (resolvedRemarkTitle) {
      return resolvedRemarkTitle;
    }
  }

  return ledgerBizTypeTitleMap[entry.biz_type] || '积分记录更新';
}

function formatLedgerDelta(entry: PointsLedgerEntryResponse): string {
  return `${entry.delta > 0 ? '+' : ''}${entry.delta} 分`;
}

function resolveLedgerColor(entry: PointsLedgerEntryResponse): string {
  return entry.delta >= 0 ? 'text-green-500' : 'text-red-500';
}

function formatReviewStatus(review: CombinedReviewHistoryItem): string {
  if (review.status === 'completed') {
    if (review.type === 'phone') {
      return review.score !== null ? `评分: ${review.score} 分` : '评测已完成';
    }
    return '命盘与大运信息已生成';
  }
  if (review.status === 'failed') {
    return '评测失败';
  }
  return review.progress_message || '评测处理中';
}

function resolveReviewActionText(review: CombinedReviewHistoryItem): string {
  if (openingReviewId.value === review.id) {
    return '打开中...';
  }
  if (review.status === 'completed') {
    return review.type === 'phone' ? '查看手机号评测详情' : '查看四柱命盘与专项分析';
  }
  if (review.status === 'failed') {
    return '查看失败原因';
  }
  return review.type === 'phone' ? '继续查看手机号评测进度' : '继续查看四柱推演进度';
}

async function handleOpenReview(review: CombinedReviewHistoryItem): Promise<void> {
  if (openingReviewId.value) {
    return;
  }

  historyActionError.value = '';
  openingReviewId.value = review.id;

  try {
    if (review.type === 'phone') {
      await refreshCurrentReview(review.id);
      activeModal.value = null;
      emit('navigate-to-tab', 'phone');
      return;
    }
    await refreshCurrentFourPillarsReview(review.id);
    activeModal.value = null;
    emit('navigate-to-tab', 'bazi');
  } catch (error) {
    historyActionError.value = humanizeError(error);
  } finally {
    openingReviewId.value = null;
  }
}
</script>

<template>
  <div class="pt-4 pb-32 max-w-md mx-auto px-margin-mobile relative text-left">
    <section class="mb-5 mt-4">
      <div
        v-if="userReady"
        class="bg-white rounded-2xl p-5 border border-gray-100 flex items-center justify-between shadow-sm relative overflow-hidden"
      >
        <div class="absolute right-0 bottom-0 text-slate-100/40 font-serif text-[42px] select-none translate-y-3 translate-x-1">
          ☯
        </div>
        <div class="flex items-center gap-3.5 z-10 min-w-0 flex-1">
          <div class="relative group shrink-0">
            <div class="relative w-14 h-14 rounded-full overflow-hidden border-2 border-brand-primary/10 bg-brand-primary/5 flex items-center justify-center font-serif font-bold text-brand-primary text-[20px] shadow-inner select-none">
              <span>{{ displayAvatarText }}</span>
              <img
                v-if="profileAvatarUrl && !avatarImageFailed"
                :src="profileAvatarUrl"
                alt=""
                class="absolute inset-0 w-full h-full object-cover"
                @error="handleAvatarImageError"
              />
            </div>
            <input
              ref="avatarInputRef"
              type="file"
              accept="image/jpeg,image/png,image/webp"
              class="hidden"
              @change="handleAvatarFileChange"
            />
            <button
              type="button"
              class="absolute -bottom-1 -right-1 bg-white border border-gray-100 hover:border-brand-primary/20 text-brand-secondary hover:text-brand-primary w-5 h-5 rounded-full flex items-center justify-center shadow-sm select-none cursor-pointer outline-none"
              title="上传头像"
              aria-label="上传头像"
              @click="openAvatarUploader"
            >
              <RefreshCw v-if="avatarUploading" :size="10" class="animate-spin" />
              <Camera v-else :size="10" />
            </button>
          </div>

          <div class="text-left min-w-0">
            <div class="flex items-center gap-1.5 flex-wrap">
              <h3 class="font-serif text-[17px] font-black text-brand-ink-strong truncate max-w-[11rem]">{{ displayNickname }}</h3>
              <button
                type="button"
                class="text-gray-400 hover:text-brand-primary cursor-pointer select-none outline-none inline-flex items-center"
                @click="openProfileEditor"
              >
                <PencilLine :size="12" />
              </button>
            </div>

            <p class="mt-1 text-[10.5px] text-brand-secondary/85 font-mono flex items-center gap-1 select-none min-w-0">
              <span class="bg-gray-100 text-gray-500 px-1.5 py-0.5 rounded scale-90 origin-left truncate max-w-[13rem]">
                UID: {{ profileUserUidDisplay }}
              </span>
            </p>
            <p v-if="avatarUploadError" class="mt-1.5 text-[10px] text-red-500 leading-relaxed">
              {{ avatarUploadError }}
            </p>
          </div>
        </div>
        <span
          class="inline-flex items-center gap-1.5 select-none transition-all shrink-0 ml-3"
          :class="profileIdentityClass"
        >
          {{ profileIdentityLabel }}
        </span>
      </div>

      <div
        v-else
        class="bg-white rounded-2xl p-5 border border-gray-100 flex items-center justify-between shadow-sm relative overflow-hidden"
      >
        <div class="absolute right-0 bottom-0 text-slate-100/40 font-serif text-[42px] select-none translate-y-3 translate-x-1">
          ☯
        </div>
        <div class="flex items-center gap-3.5 z-10 min-w-0">
          <div class="w-14 h-14 rounded-full border border-gray-100 bg-gray-50 flex items-center justify-center text-gray-400 shrink-0 shadow-inner select-none">
            <AlertTriangle :size="20" />
          </div>
          <div class="text-left min-w-0">
            <h3 class="text-[16px] font-serif font-black text-brand-ink-strong">游客用户</h3>
            <p class="text-[10.5px] text-brand-secondary/80 mt-1 leading-relaxed">
              {{ profileFallbackTitle }}
            </p>
            <p v-if="connectionHint" class="text-[10px] text-brand-secondary/70 mt-1 leading-relaxed">
              {{ connectionHint }}
            </p>
          </div>
        </div>
        <button
          @click="handleProfileFallbackAction"
          class="z-10 inline-flex items-center gap-1 px-3.5 py-1.5 text-[10.5px] font-bold rounded-full select-none bg-neutral-100 hover:bg-neutral-200 text-neutral-600 border border-neutral-300/60 shadow-xs cursor-pointer transition-all active:scale-95"
          :disabled="state.booting"
        >
          <RefreshCw v-if="state.booting || state.connectionError" :size="13" :class="state.booting ? 'animate-spin' : ''" />
          <LogIn v-else :size="12" />
          <span>{{ profileFallbackActionLabel }}</span>
        </button>
      </div>
    </section>

    <section class="mb-5">
      <div class="bg-[#151210] border border-stone-800 text-white rounded-2xl p-5 flex flex-col justify-between relative overflow-hidden shadow-lg">
        <div class="absolute right-[-10%] bottom-[-15%] opacity-[0.03] text-brand-accent font-serif font-black text-[120px] pointer-events-none select-none">
          ☯
        </div>

        <div class="relative z-10 flex items-center justify-between gap-5">
          <div class="min-w-0">
            <div>
              <p class="text-[10px] font-semibold text-stone-400 gap-1 uppercase tracking-widest mb-1 select-none">我的积分结存</p>
              <div class="flex items-baseline gap-1">
                <span class="font-serif text-[32px] font-black text-[#E8C895] leading-none">{{ currentPoints }}</span>
                <span class="text-[9.5px] text-stone-400 font-mono scale-90">Points</span>
              </div>
            </div>
          </div>

          <button
            @click="emit('navigate-to-tab', 'recharge', { source: 'profile', return_to: 'profile' })"
            class="h-10 bg-[#DEC299] hover:bg-[#EBD3B1] text-brand-ink-strong px-5 rounded-xl text-[12px] font-black active:scale-95 transition-all shrink-0 cursor-pointer outline-none shadow-sm border border-stone-600/30 inline-flex items-center justify-center"
          >
            去充值
          </button>
        </div>
      </div>
    </section>

    <section class="mb-5">
      <div
        @click="showSystemIntro = true"
        class="bg-gradient-to-r from-brand-primary/5 to-purple-500/5 rounded-2xl p-4 border border-brand-primary/10 flex items-center justify-between cursor-pointer hover:brightness-98 transition-all"
      >
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-full bg-brand-primary/10 flex items-center justify-center text-brand-primary shrink-0">
            <Share2 :size="16" />
          </div>
          <div class="text-left">
            <p class="font-sans text-[13px] font-bold text-brand-ink-strong">升级为「易如反掌」推广大使</p>
            <p class="font-sans text-[11px] text-brand-secondary mt-0.5">邀请朋友一起体验优秀传统文化，赚取高额佣金</p>
          </div>
        </div>
        <button
          @click.stop="showSystemIntro = true"
          class="font-sans text-[11px] font-bold text-brand-primary bg-white hover:bg-brand-primary/5 px-3 py-1.5 rounded-full border border-brand-primary/20 shrink-0 cursor-pointer transition-all outline-none"
        >
          详情
        </button>
      </div>
    </section>

    <section class="mb-8">
      <div class="bg-white rounded-2xl overflow-hidden hairline-border divide-y divide-gray-100 shadow-sm">
        <div
          @click="showSystemIntro = true"
          class="flex items-center justify-between p-4 bg-brand-primary/[0.02] hover:bg-brand-primary/[0.05] transition-colors cursor-pointer select-none"
        >
          <div class="flex items-center gap-3">
            <Share2 :size="18" class="text-brand-primary" />
            <span class="font-sans text-[14px] font-black text-brand-primary-strong">合伙与推广说明书</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="text-[9.5px] text-brand-primary bg-brand-primary/10 px-2 py-0.5 rounded-full font-extrabold font-sans">福利与返佣体系</span>
            <ChevronRight :size="16" class="text-brand-primary" />
          </div>
        </div>

        <div
          @click="openProtectedModal('ledger')"
          class="flex items-center justify-between p-4 bg-white hover:bg-gray-50/50 transition-colors cursor-pointer select-none"
        >
          <div class="flex items-center gap-3">
            <Receipt :size="18" class="text-brand-secondary" />
            <span class="font-sans text-[13px] font-bold text-brand-ink-strong">积分记录</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span v-if="ledgerRecords.length > 0" class="font-sans text-[10px] text-brand-primary font-bold bg-brand-primary/10 px-1.5 py-0.5 rounded-full">
              {{ ledgerRecords.length }}
            </span>
            <ChevronRight :size="16" class="text-gray-300" />
          </div>
        </div>

        <div
          @click="openProtectedModal('history')"
          class="flex items-center justify-between p-4 bg-white hover:bg-gray-50/50 transition-colors cursor-pointer select-none"
        >
          <div class="flex items-center gap-3">
            <History :size="18" class="text-brand-secondary" />
            <span class="font-sans text-[13px] font-bold text-brand-ink-strong">评测记录</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span v-if="combinedHistory.length > 0" class="font-sans text-[10px] text-brand-primary font-bold bg-brand-primary/10 px-1.5 py-0.5 rounded-full">
              {{ combinedHistory.length }}
            </span>
            <ChevronRight :size="16" class="text-gray-300" />
          </div>
        </div>

        <div
          @click="openPasswordEditor"
          class="flex items-center justify-between p-4 bg-white hover:bg-gray-50/50 transition-colors cursor-pointer select-none"
        >
          <div class="flex items-center gap-3">
            <KeyRound :size="18" class="text-brand-secondary" />
            <span class="font-sans text-[13px] font-bold text-brand-ink-strong">修改密码</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="font-sans text-[9px] text-gray-400 font-bold bg-gray-100 px-1.5 py-0.5 rounded-md">密保安全</span>
            <ChevronRight :size="16" class="text-gray-300" />
          </div>
        </div>

        <div
          @click="activeModal = 'feedback'"
          class="flex items-center justify-between p-4 bg-white hover:bg-gray-50/50 transition-colors cursor-pointer select-none"
        >
          <div class="flex items-center gap-3">
            <MessageSquare :size="18" class="text-brand-secondary" />
            <span class="font-sans text-[13px] font-bold text-brand-ink-strong">反馈问题</span>
          </div>
          <ChevronRight :size="16" class="text-gray-300" />
        </div>
      </div>
    </section>

    <div class="text-center px-1">
      <button
        @click="handleAccountAction"
        class="w-full py-3.5 rounded-xl bg-brand-primary text-white font-sans text-[13px] font-bold hover:bg-brand-primary-strong transition-colors active:scale-[0.99] flex items-center justify-center gap-2 cursor-pointer outline-none shadow-md"
      >
        <LogOut v-if="!isGuestUser" :size="16" />
        <LogIn v-else :size="16" />
        <span>{{ primaryAccountActionLabel }}</span>
      </button>
    </div>

    <transition name="fade">
      <div v-if="activeModal === 'logout_confirm'" class="fixed inset-0 bg-slate-900/40 flex items-center justify-center p-4 z-[100] backdrop-blur-sm">
        <div class="bg-white border border-brand-primary/15 rounded-2xl p-5 w-full max-w-xs space-y-4 shadow-2xl relative text-left">
          <div class="space-y-2 text-center pb-1">
            <div class="w-11 h-11 rounded-full bg-rose-50/50 border border-rose-100 text-rose-500 flex items-center justify-center mx-auto text-center select-none scale-105">
              <AlertTriangle :size="20" />
            </div>
            <h3 class="text-sm font-serif font-black text-brand-ink-strong tracking-wide">正在登出账号</h3>
            <p class="text-[11px] text-brand-secondary leading-relaxed px-1">
              您确定要退出当前账号吗？
            </p>
            <p class="text-[11px] text-brand-secondary leading-relaxed px-1">
              评测和智能体功能必须要登录才能使用
            </p>
            <p
              v-if="logoutError"
              class="rounded-xl border border-red-100 bg-red-50 px-3 py-2 font-sans text-[11px] text-red-600 leading-relaxed text-left"
            >
              {{ logoutError }}
            </p>
          </div>

          <div class="flex gap-2.5 pt-1">
            <button
              type="button"
              @click="activeModal = null"
              class="flex-1 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-600 text-xs font-bold rounded-lg outline-none cursor-pointer"
              :disabled="logoutSaving"
            >
              取消登出
            </button>
            <button
              type="button"
              @click="confirmLogout"
              class="flex-1 py-1.5 bg-rose-500 hover:bg-rose-600 text-white hover:brightness-110 text-xs font-bold rounded-lg outline-none cursor-pointer shadow-sm border border-transparent disabled:opacity-60"
              :disabled="logoutSaving"
            >
              {{ logoutSaving ? '正在登出...' : '确认登出' }}
            </button>
          </div>
        </div>
      </div>
    </transition>

    <footer class="mt-14 text-center pb-8 shrink-0">
      <p class="font-sans text-[11px] font-bold text-brand-secondary/50 tracking-widest">
        易如反掌 · 服务积分与推广规则以后端配置为准
      </p>
      <p class="font-sans text-[10px] text-gray-400 mt-2">
        易如反掌 / EaseWise
      </p>
    </footer>

    <transition name="fade">
      <div v-if="activeModal === 'ledger'" class="fixed inset-0 bg-brand-ink-strong/60 flex items-center justify-center p-4 z-[100] backdrop-blur-sm">
        <div class="bg-white rounded-2xl p-5 w-full max-w-sm space-y-4 hairline-border shadow-2xl relative">
          <div class="flex justify-between items-center pb-2 border-b border-gray-100 text-left w-full">
            <div class="text-left">
              <h3 class="font-sans text-[17px] font-bold text-brand-ink-strong">积分记录</h3>
              <p class="font-sans text-[11px] text-brand-secondary">当前展示最近的积分获取与扣减记录</p>
            </div>
            <button @click="activeModal = null" class="p-1 rounded-full text-brand-secondary hover:bg-gray-100 outline-none cursor-pointer shrink-0">
              <X :size="18" />
            </button>
          </div>

          <div class="max-h-[300px] overflow-y-auto no-scrollbar space-y-3.5 pr-1 py-1">
            <div v-if="ledgerRecords.length > 0" class="space-y-3.5">
              <div v-for="entry in ledgerRecords" :key="entry.ledger_id" class="flex justify-between items-start text-xs border-b border-gray-50 pb-2.5">
                <div class="text-left">
                  <p class="font-sans text-[13px] font-bold text-brand-ink">{{ formatLedgerTitle(entry) }}</p>
                  <p class="font-sans text-[10px] text-brand-secondary mt-0.5">{{ formatDateTime(entry.created_at) }}</p>
                </div>
                <div class="text-right">
                  <span class="font-mono text-[13px] font-bold" :class="resolveLedgerColor(entry)">{{ formatLedgerDelta(entry) }}</span>
                  <p class="font-sans text-[10px] text-brand-secondary mt-0.5">余额 {{ entry.balance_after }} 分</p>
                </div>
              </div>
            </div>
            <div v-else class="py-8 text-center space-y-2">
              <p class="font-sans text-[13px] text-brand-secondary">暂无积分变动记录。</p>
              <p class="font-sans text-[10px] text-brand-secondary/60">完成手机号评测或后台发放积分后，会在这里显示。</p>
            </div>
          </div>

          <button @click="activeModal = null" class="w-full py-2.5 bg-brand-paper hover:bg-gray-100 text-brand-ink font-sans text-[13px] font-semibold rounded-lg shrink-0 outline-none cursor-pointer">
            确定返回
          </button>
        </div>
      </div>
    </transition>

    <transition name="fade">
      <div v-if="activeModal === 'history'" class="fixed inset-0 bg-brand-ink-strong/60 flex items-center justify-center p-4 z-[100] backdrop-blur-sm">
        <div class="bg-white rounded-2xl p-5 w-full max-w-sm space-y-4 hairline-border shadow-2xl relative">
          <div class="flex justify-between items-center pb-2 border-b border-gray-100 w-full">
            <div class="text-left">
              <h3 class="font-sans text-[17px] font-bold text-brand-ink-strong">我的评测记录</h3>
              <p class="font-sans text-[11px] text-brand-secondary">数字奇门与四柱八字记录统一展示</p>
            </div>
            <button @click="activeModal = null" class="p-1 rounded-full text-brand-secondary hover:bg-gray-100 outline-none cursor-pointer">
              <X :size="18" />
            </button>
          </div>

          <div class="max-h-[300px] overflow-y-auto no-scrollbar space-y-3 py-1">
            <p
              v-if="historyActionError"
              class="rounded-xl border border-red-100 bg-red-50 px-3 py-2 font-sans text-[11px] text-red-600 leading-relaxed"
            >
              {{ historyActionError }}
            </p>
            <div v-if="combinedHistory.length > 0" class="space-y-3">
              <button
                v-for="review in combinedHistory"
                :key="`${review.type}:${review.id}`"
                type="button"
                class="w-full bg-brand-paper/50 p-3 rounded-xl border border-gray-100 flex items-start justify-between gap-3 text-xs text-left transition-all hover:bg-white hover:border-brand-primary/20 disabled:opacity-60 disabled:cursor-not-allowed"
                :disabled="!!openingReviewId"
                @click="handleOpenReview(review)"
              >
                <div class="min-w-0 flex-1 space-y-1">
                  <div class="flex items-center gap-1.5 flex-wrap">
                    <span
                      class="font-sans text-[10px] font-black px-2 py-0.5 rounded-full border"
                      :class="review.type === 'phone'
                        ? 'bg-sky-50 text-sky-700 border-sky-100'
                        : 'bg-amber-50 text-amber-800 border-amber-100'"
                    >
                      {{ review.type === 'phone' ? '数字奇门' : '四柱八字' }}
                    </span>
                    <span class="font-sans text-[10px] text-brand-secondary">{{ formatDateTime(review.created_at) }}</span>
                  </div>
                  <p v-if="review.type === 'phone'" class="font-sans text-[13px] font-bold text-brand-ink-strong">
                    <span class="text-brand-secondary/70 text-[11px] font-medium">评测号码：</span>
                    <span class="font-black tracking-wide text-brand-primary-strong">{{ review.masked_phone || review.phone_number }}</span>
                    <span class="ml-1.5 text-[10px] font-medium text-brand-secondary bg-sky-50/70 border border-sky-100/60 px-1.5 py-0.5 rounded">
                      {{ review.gender === 'male' ? '男命' : '女命' }}
                    </span>
                  </p>
                  <div v-else class="space-y-1">
                    <p class="font-serif text-[13px] font-bold text-brand-ink-strong">
                      <span class="font-sans text-brand-secondary/70 text-[11px] font-medium">评测命造：</span>
                      <span class="text-amber-900">{{ review.name?.trim() || '生辰盘主' }}</span>
                      <span class="ml-1.5 font-sans text-[10px] font-medium text-brand-secondary bg-amber-50/70 border border-amber-100/60 px-1.5 py-0.5 rounded">
                        {{ review.gender === 'male' ? '乾造·男' : '坤造·女' }}
                      </span>
                    </p>
                    <p class="font-sans text-[10.5px] text-brand-secondary leading-snug">
                      生辰：
                      <span class="font-mono bg-zinc-50 border border-gray-150 px-1 py-0.5 rounded text-zinc-700 text-[10px]">
                        {{ review.birth_date }} {{ review.birth_time }}
                      </span>
                    </p>
                  </div>
                  <p class="font-sans text-[10px] text-brand-secondary/80 mt-1">
                    {{ resolveReviewActionText(review) }}
                  </p>
                </div>
                <div class="shrink-0 flex flex-col items-end gap-1.5">
                  <span class="font-sans text-[13px] font-bold text-brand-primary bg-brand-primary/10 px-2.5 py-1 rounded-full shrink-0">
                    {{ formatReviewStatus(review) }}
                  </span>
                  <ChevronRight :size="14" class="text-brand-secondary/60" />
                </div>
              </button>
            </div>
            <div v-else class="py-8 text-center space-y-2">
              <p class="font-sans text-[13px] text-brand-secondary">暂无评测历史记录。</p>
              <p class="font-sans text-[10px] text-brand-secondary/60">你可以先完成一次手机号评测，或到四柱八字起盘排盘。</p>
            </div>
          </div>

          <button @click="activeModal = null" class="w-full py-2.5 bg-brand-paper hover:bg-gray-100 text-brand-ink font-sans text-[13px] font-semibold rounded-lg outline-none cursor-pointer">
            确定返回
          </button>
        </div>
      </div>
    </transition>

    <transition name="fade">
      <div v-if="activeModal === 'feedback'" class="fixed inset-0 bg-brand-ink-strong/60 flex items-center justify-center p-4 z-[100] backdrop-blur-sm">
        <div class="bg-white rounded-2xl p-5 w-full max-w-sm space-y-4 hairline-border shadow-2xl relative">
          <div class="flex justify-between items-center pb-2 border-b border-gray-100 w-full">
            <div class="text-left">
              <h3 class="font-sans text-[17px] font-bold text-brand-ink-strong">反馈问题</h3>
              <p class="font-sans text-[11px] text-brand-secondary">提交你遇到的问题、建议或合作需求</p>
            </div>
            <button @click="activeModal = null" class="p-1 rounded-full text-brand-secondary hover:bg-gray-100 outline-none cursor-pointer">
              <X :size="18" />
            </button>
          </div>

          <div class="space-y-3 text-left">
            <label class="font-sans text-[11px] font-bold text-brand-secondary tracking-wide">反馈详情</label>
            <textarea
              v-model="feedbackText"
              class="w-full bg-brand-paper font-sans text-[13px] text-brand-ink-strong p-3.5 h-28 rounded-xl border border-gray-100 focus:border-brand-primary outline-none resize-none transition-all"
              placeholder="请输入你遇到的问题、改进建议或合作需求..."
            />
          </div>

          <div class="pt-2 flex gap-2">
            <button @click="activeModal = null" class="flex-1 py-2.5 bg-gray-50 hover:bg-gray-100 text-brand-ink font-sans text-[13px] font-semibold rounded-lg outline-none cursor-pointer">
              取消
            </button>
            <button
              @click="handleFeedbackSubmit"
              class="flex-1 py-2.5 bg-brand-primary text-white hover:bg-brand-primary-strong font-sans text-[13px] font-bold rounded-lg outline-none cursor-pointer disabled:opacity-55"
              :disabled="!feedbackText.trim()"
            >
              提交反馈
            </button>
          </div>
        </div>
      </div>
    </transition>

    <transition name="fade">
      <div v-if="profileEditorVisible" class="fixed inset-0 bg-brand-ink-strong/60 flex items-center justify-center p-4 z-[110] backdrop-blur-sm">
        <div class="bg-white rounded-2xl p-5 w-full max-w-sm space-y-4 hairline-border shadow-2xl relative">
          <div class="flex justify-between items-center pb-2 border-b border-gray-100 w-full">
            <div class="text-left">
              <h3 class="font-sans text-[17px] font-bold text-brand-ink-strong">修改用户名</h3>
              <p class="font-sans text-[11px] text-brand-secondary">当前名称将同步到个人中心与后台可见昵称</p>
            </div>
            <button @click="profileEditorVisible = false" class="p-1 rounded-full text-brand-secondary hover:bg-gray-100 outline-none cursor-pointer">
              <X :size="18" />
            </button>
          </div>

          <div class="space-y-3 text-left">
            <label class="font-sans text-[11px] font-bold text-brand-secondary tracking-wide">用户名 / 昵称</label>
            <input
              v-model="profileNicknameDraft"
              class="w-full bg-brand-paper font-sans text-[13px] text-brand-ink-strong p-3 rounded-xl border border-gray-100 focus:border-brand-primary outline-none transition-all"
              placeholder="请输入用户名或昵称"
              maxlength="64"
            />
            <p v-if="profileSaveError" class="rounded-xl border border-red-100 bg-red-50 px-3 py-2 font-sans text-[11px] text-red-600 leading-relaxed">
              {{ profileSaveError }}
            </p>
          </div>

          <div class="pt-2 flex gap-2">
            <button @click="profileEditorVisible = false" class="flex-1 py-2.5 bg-gray-50 hover:bg-gray-100 text-brand-ink font-sans text-[13px] font-semibold rounded-lg outline-none cursor-pointer">
              取消
            </button>
            <button
              @click="submitProfileEditor"
              class="flex-1 py-2.5 bg-brand-primary text-white hover:bg-brand-primary-strong font-sans text-[13px] font-bold rounded-lg outline-none cursor-pointer disabled:opacity-55"
              :disabled="profileSaving"
            >
              {{ profileSaving ? '保存中...' : '保存' }}
            </button>
          </div>
        </div>
      </div>
    </transition>

    <transition name="fade">
      <div v-if="passwordEditorVisible" class="fixed inset-0 bg-brand-ink-strong/60 flex items-center justify-center p-4 z-[120] backdrop-blur-sm">
        <div class="bg-white rounded-2xl p-5 w-full max-w-sm space-y-4 hairline-border shadow-2xl relative">
          <div class="flex justify-between items-center pb-2 border-b border-gray-100 w-full">
            <div class="text-left">
              <h3 class="font-sans text-[17px] font-bold text-brand-ink-strong">修改登录密码</h3>
              <p class="font-sans text-[11px] text-brand-secondary">请输入当前密码，并设置一个新的登录密码</p>
            </div>
            <button @click="closePasswordEditor" class="p-1 rounded-full text-brand-secondary hover:bg-gray-100 outline-none cursor-pointer">
              <X :size="18" />
            </button>
          </div>

          <div class="space-y-3 text-left">
            <label class="font-sans text-[11px] font-bold text-brand-secondary tracking-wide">当前密码</label>
            <input
              v-model="currentPasswordDraft"
              type="password"
              autocomplete="current-password"
              class="w-full bg-brand-paper font-sans text-[13px] text-brand-ink-strong p-3 rounded-xl border border-gray-100 focus:border-brand-primary outline-none transition-all"
              placeholder="请输入当前登录密码"
            />

            <label class="font-sans text-[11px] font-bold text-brand-secondary tracking-wide">新密码</label>
            <input
              v-model="newPasswordDraft"
              type="password"
              autocomplete="new-password"
              class="w-full bg-brand-paper font-sans text-[13px] text-brand-ink-strong p-3 rounded-xl border border-gray-100 focus:border-brand-primary outline-none transition-all"
              placeholder="8-32位，至少包含两类字符"
            />

            <label class="font-sans text-[11px] font-bold text-brand-secondary tracking-wide">确认新密码</label>
            <input
              v-model="confirmPasswordDraft"
              type="password"
              autocomplete="new-password"
              class="w-full bg-brand-paper font-sans text-[13px] text-brand-ink-strong p-3 rounded-xl border border-gray-100 focus:border-brand-primary outline-none transition-all"
              placeholder="请再次输入新密码"
            />

            <div class="rounded-xl border border-amber-100 bg-amber-50 px-3 py-2 font-sans text-[11px] text-amber-700 leading-relaxed">
              <p>如果忘记当前密码，当前版本暂未接入短信验证自助找回。请先联系客服人工核验，或等待验证能力接入后再重置。</p>
              <button
                type="button"
                class="mt-2 inline-flex items-center gap-1 rounded-lg bg-white px-2.5 py-1.5 text-[10.5px] font-bold text-amber-800 shadow-sm outline-none"
                @click="openCustomerServiceModal('account_security')"
              >
                <MessageSquare :size="11" />
                <span>联系客服</span>
              </button>
            </div>

            <p v-if="passwordSaveError" class="rounded-xl border border-red-100 bg-red-50 px-3 py-2 font-sans text-[11px] text-red-600 leading-relaxed">
              {{ passwordSaveError }}
            </p>
            <p v-if="passwordSaveSuccess" class="rounded-xl border border-emerald-100 bg-emerald-50 px-3 py-2 font-sans text-[11px] text-emerald-700 leading-relaxed">
              {{ passwordSaveSuccess }}
            </p>
          </div>

          <div class="pt-2 flex gap-2">
            <button @click="closePasswordEditor" class="flex-1 py-2.5 bg-gray-50 hover:bg-gray-100 text-brand-ink font-sans text-[13px] font-semibold rounded-lg outline-none cursor-pointer">
              取消
            </button>
            <button
              @click="submitPasswordEditor"
              class="flex-1 py-2.5 bg-brand-primary text-white hover:bg-brand-primary-strong font-sans text-[13px] font-bold rounded-lg outline-none cursor-pointer disabled:opacity-55"
              :disabled="passwordSaving"
            >
              {{ passwordSaving ? '保存中...' : '保存密码' }}
            </button>
          </div>
        </div>
      </div>
    </transition>

    <transition name="slide">
      <SystemIntro v-if="showSystemIntro" @close="showSystemIntro = false" />
    </transition>
  </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.slide-enter-active, .slide-leave-active {
  transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.25s ease;
}
.slide-enter-from, .slide-leave-to {
  transform: translateY(100%);
  opacity: 0.95;
}
</style>
