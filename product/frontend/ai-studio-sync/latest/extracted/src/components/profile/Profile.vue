<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import {
  User, Shield, Coins, History, LogOut, ArrowRight, Camera, Key, CheckCircle2,
  Phone, Calendar, Star, Compass, AlertCircle, MessageSquare, Info, X
} from 'lucide-vue-next';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';
import { resolveApiAssetUrl } from '../../lib/api';
import SystemIntro from './SystemIntro.vue';
import AmbassadorDetail from './AmbassadorDetail.vue';

const emit = defineEmits<{
  (e: 'navigate-to-tab', tab: string, params?: any): void;
}>();

const {
  state, displayNickname, displayAvatarText, updateProfile, uploadAvatar,
  changePassword, logout, refreshPoints, refreshPointsLedger,
  refreshReviewHistory, refreshFourPillarsHistory, refreshCurrentReview,
  refreshCurrentFourPillarsReview, requestRegisteredUser
} = useEaseWiseApp();

const activeHistoryTab = ref<'phone' | 'bazi'>('phone');

// Modal States
const showNicknameModal = ref(false);
const showPasswordModal = ref(false);
const showFeedbackModal = ref(false);
const showLogoutConfirmModal = ref(false);
const showIntroModal = ref(false);
const showAmbassadorModal = ref(false);

const showLedgerModal = ref(false);
const showHistoryModal = ref(false);

// Form Fields
const nicknameForm = ref('');
const passwordForm = ref({ current: '', next: '', confirm: '' });
const feedbackText = ref('');

const toastError = ref<string | null>(null);
const toastSuccess = ref<string | null>(null);

// File ref for Local Avatar Input
const avatarFileInputRef = ref<HTMLInputElement | null>(null);

// Computeds
const isLoggedIn = computed(() => Boolean(state.user));

const userIdentityLabel = computed(() => {
  if (!state.user) return '游客';
  const level = state.user.identity_level || 'standard';
  if (level === 'admin') return 'SVIP 推广大使';
  if (level === 'vip') return 'VIP 推广大使';
  if (level === 'promoter') return '推广大使';
  return '普通用户';
});

const userUid = computed(() => {
  return state.user?.uid || state.user?.user_id || 'EW-GUEST-000';
});

function showToast(msg: string, type: 'success' | 'error' = 'success') {
  if (type === 'success') {
    toastSuccess.value = msg;
    setTimeout(() => toastSuccess.value = null, 2500);
  } else {
    toastError.value = msg;
    setTimeout(() => toastError.value = null, 2500);
  }
}

async function handleUpdateProfile() {
  if (!nicknameForm.value.trim()) return;
  try {
    await updateProfile({ nickname: nicknameForm.value.trim() });
    showNicknameModal.value = false;
    showToast("个人信息修改成功！");
  } catch (error: any) {
    showToast(error.message || "更新失败", 'error');
  }
}

async function handleUpdatePassword() {
  const f = passwordForm.value;
  if (!f.current || !f.next || !f.confirm) {
    showToast("请完整填入各项密码", 'error');
    return;
  }
  if (f.next !== f.confirm) {
    showToast("两次新密码输入不一致", 'error');
    return;
  }
  try {
    await changePassword(f.current, f.next, f.confirm);
    showPasswordModal.value = false;
    passwordForm.value = { current: '', next: '', confirm: '' };
    showToast("登录密码修改成功！");
  } catch (error: any) {
    showToast(error.message || "当前密码输入有误", 'error');
  }
}

async function handleSendFeedback() {
  if (!feedbackText.value.trim()) return;
  showFeedbackModal.value = false;
  feedbackText.value = '';
  showToast("谢谢您的建言！反馈已送达平台客服。");
}

function triggerAvatarFileSelect() {
  if (!isLoggedIn.value) {
    triggerGuestLogin();
    return;
  }
  avatarFileInputRef.value?.click();
}

async function handleAvatarFileChange(e: Event) {
  const target = e.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;

  const allowed = ['image/jpeg', 'image/png', 'image/webp'];
  if (!allowed.includes(file.type)) {
    showToast("只支持 jpg, png, webp 格式的图片", 'error');
    return;
  }

  const maxSize = 5 * 1024 * 1024;
  if (file.size > maxSize) {
    showToast("头像图片大小不能超过 5MB", 'error');
    return;
  }

  const reader = new FileReader();
  reader.onload = async (event) => {
    const dataUrl = event.target?.result as string;
    try {
      await uploadAvatar(dataUrl);
      showToast("个人头像更新成功！");
    } catch (err: any) {
      showToast(err.message || "上传头像失败", 'error');
    }
  };
  reader.readAsDataURL(file);
}

async function handleOpenLedgerModal() {
  if (!isLoggedIn.value) {
    await requestRegisteredUser('查看积分记录列表');
    return;
  }
  try {
    await refreshPointsLedger();
    showLedgerModal.value = true;
  } catch (err) {
    showToast("积分账单载入失败", 'error');
  }
}

async function handleOpenHistoryModal() {
  if (!isLoggedIn.value) {
    await requestRegisteredUser('查看过往评测历史');
    return;
  }
  try {
    await refreshReviewHistory();
    await refreshFourPillarsHistory();
    showHistoryModal.value = true;
  } catch (err) {
    showToast("评测历史载入失败", 'error');
  }
}

async function handleLoadHistoryPhone(reviewId: string) {
  try {
    await refreshCurrentReview(reviewId);
    emit('navigate-to-tab', 'phone');
  } catch (err) {
    showToast("加载奇门报告失败", 'error');
  }
}

async function handleLoadHistoryBazi(reviewId: string) {
  try {
    await refreshCurrentFourPillarsReview(reviewId);
    emit('navigate-to-tab', 'bazi');
  } catch (err) {
    showToast("加载八字报告失败", 'error');
  }
}

async function triggerGuestLogin() {
  await requestRegisteredUser('同步数据或开启充值特权');
}

async function confirmLogout() {
  await logout();
  showLogoutConfirmModal.value = false;
  showToast("已成功退出登录。");
}

const loadUserData = async () => {
  if (isLoggedIn.value) {
    void refreshPoints();
    void refreshPointsLedger();
    void refreshReviewHistory();
    void refreshFourPillarsHistory();
  }
};

watch(isLoggedIn, (newVal) => {
  if (newVal) {
    void loadUserData();
  }
});

onMounted(() => {
  void loadUserData();
});
</script>

<template>
  <div class="pt-4 pb-32 max-w-md mx-auto px-margin-mobile text-left relative">
    <!-- Success Toast -->
    <transition name="fade">
      <div v-if="toastSuccess" class="fixed top-4 left-1/2 -translate-x-1/2 z-50 bg-emerald-600 text-white px-4 py-2.5 rounded-full font-sans text-[13px] shadow-lg font-medium flex items-center gap-1.5 whitespace-nowrap">
        <CheckCircle2 :size="15" />
        <span>{{ toastSuccess }}</span>
      </div>
    </transition>

    <!-- Error Toast -->
    <transition name="fade">
      <div v-if="toastError" class="fixed top-4 left-1/2 -translate-x-1/2 z-50 bg-amber-600 text-white px-4 py-2.5 rounded-full font-sans text-[13px] shadow-lg font-medium flex items-center gap-1.5 whitespace-nowrap">
        <AlertCircle :size="15" />
        <span>{{ toastError }}</span>
      </div>
    </transition>

    <!-- Profile Header Section -->
    <section class="mb-5 bg-white rounded-2xl p-5 border border-brand-paper shadow-sm">
      <!-- REGISTERED VIEW -->
      <div v-if="isLoggedIn">
        <div class="flex items-center gap-4 relative">
          <!-- Local File Upload Clickable Target with hover effect -->
          <div
            @click="triggerAvatarFileSelect"
            class="w-16 h-16 rounded-full bg-brand-primary text-white flex items-center justify-center font-serif text-2xl font-bold select-none border-2 border-brand-paper shadow-md relative shrink-0 cursor-pointer overflow-hidden group"
          >
            <img v-if="state.user?.avatar_url" :src="resolveApiAssetUrl(state.user.avatar_url)" class="w-full h-full object-cover rounded-full" />
            <span v-else>{{ displayAvatarText }}</span>
            <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity">
              <Camera :size="16" class="text-white" />
            </div>
          </div>
          <!-- Hidden Native File Input -->
          <input
            type="file"
            ref="avatarFileInputRef"
            @change="handleAvatarFileChange"
            accept="image/jpeg,image/png,image/webp"
            class="hidden"
          />

          <div class="flex-1 min-w-[120px]">
            <h3 class="font-serif text-[17px] font-bold text-brand-ink-strong truncate">{{ displayNickname }}</h3>
            <p class="font-sans text-[10px] text-brand-secondary/80 mt-1 flex items-center gap-1.5 select-none">
              <span class="px-2 py-0.5 bg-brand-primary/10 text-brand-primary-strong rounded font-extrabold tracking-wider scale-95 origin-left">
                {{ userIdentityLabel }}
              </span>
              <span class="font-mono text-zinc-400">UID: {{ userUid }}</span>
            </p>
          </div>

          <button
            @click="nicknameForm = state.user?.nickname || ''; showNicknameModal = true"
            class="bg-brand-paper hover:bg-zinc-100 text-brand-ink px-3 py-1.5 rounded-xl font-sans text-[11px] font-bold border border-gray-150 cursor-pointer flex items-center gap-1 shrink-0 outline-none"
          >
            <Camera :size="12" />
            <span>修改昵称</span>
          </button>
        </div>

        <!-- My Points Balance Card -->
        <div class="grid grid-cols-2 gap-4 mt-5 pt-4 border-t border-gray-50 text-center">
          <div class="bg-brand-paper/40 rounded-xl p-3 border border-brand-paper/70 flex flex-col justify-center items-center">
            <span class="font-sans text-[11px] text-brand-secondary/85 font-extrabold flex items-center gap-1">
              <Coins :size="13" class="text-brand-primary" />
              <span>我的积分结存</span>
            </span>
            <span class="font-serif text-[24px] font-extrabold text-brand-secondary mt-1">
              {{ state.points?.balance ?? 0 }}
            </span>
          </div>

          <div class="flex flex-col justify-center items-center">
            <button
              @click="emit('navigate-to-tab', 'recharge', { source: 'profile', return_to: 'profile' })"
              class="w-full h-full bg-brand-primary text-white font-sans text-[13px] font-bold rounded-xl cursor-pointer hover:bg-brand-primary/95 shadow-sm active:scale-95 transition-transform border-none flex items-center justify-center gap-1.5 py-4 outline-none"
            >
              <span>去充值</span>
              <ArrowRight :size="15" />
            </button>
          </div>
        </div>
      </div>

      <!-- GUEST / ANONYMOUS FALLBACK VIEW -->
      <div v-else class="text-center py-4">
        <div class="w-14 h-14 bg-brand-paper text-brand-secondary rounded-full flex items-center justify-center mx-auto mb-3 border shadow-inner">
          <User :size="26" />
        </div>
        <h3 class="font-serif text-[17px] font-bold text-brand-ink-strong">游客用户</h3>
        <p class="font-sans text-[11.5px] text-brand-secondary max-w-sm mx-auto mt-2 leading-relaxed">
          注册并绑定手机号，获取初始体验积分，并长久同步您的手机格局与一生身运排盘数据。
        </p>
        <button
          @click="triggerGuestLogin"
          class="mt-4 bg-brand-primary hover:bg-brand-primary/95 text-white font-sans text-[13px] font-bold px-6 py-2.5 rounded-xl shadow-md cursor-pointer inline-flex items-center gap-1.5 active:scale-95 transition-transform outline-none border-none"
        >
          <span>立即登录 / 注册</span>
          <ArrowRight :size="14" />
        </button>
      </div>
    </section>

    <!-- Main Compact Action List (Replaces inline tabs as required locally) -->
    <section class="mb-5 bg-white rounded-2xl p-4 border border-brand-paper shadow-sm text-left">
      <div class="space-y-2.5">

        <!-- Action Row 1: 合伙与推广说明书 -->
        <button
          @click="showIntroModal = true"
          class="w-full bg-brand-paper/40 hover:bg-brand-paper/85 border border-gray-100/60 rounded-xl p-3.5 flex items-center justify-between cursor-pointer outline-none font-sans text-[12.5px] font-bold text-brand-secondary"
        >
          <span class="flex items-center gap-2.5">
            <Info :size="15" class="text-brand-primary" />
            <span>合伙与推广说明书</span>
          </span>
          <ArrowRight :size="14" class="text-brand-secondary/40" />
        </button>

        <!-- Action Row 2: 推广提成与规则门槛 (Visible only if logged-in) -->
        <button
          v-if="isLoggedIn"
          @click="showAmbassadorModal = true"
          class="w-full bg-brand-paper/40 hover:bg-brand-paper/85 border border-gray-100/60 rounded-xl p-3.5 flex items-center justify-between cursor-pointer outline-none font-sans text-[12.5px] font-bold text-brand-secondary"
        >
          <span class="flex items-center gap-2.5">
            <Star :size="15" class="text-brand-primary" />
            <span>推广大使</span>
          </span>
          <ArrowRight :size="14" class="text-brand-secondary/40" />
        </button>

        <!-- Action Row 3: 积分记录 overlay -->
        <button
          @click="handleOpenLedgerModal"
          class="w-full bg-brand-paper/40 hover:bg-brand-paper/85 border border-gray-100/60 rounded-xl p-3.5 flex items-center justify-between cursor-pointer outline-none font-sans text-[12.5px] font-bold text-brand-secondary"
        >
          <span class="flex items-center gap-2.5">
            <Coins :size="15" class="text-brand-primary" />
            <span>积分记录</span>
          </span>
          <ArrowRight :size="14" class="text-brand-secondary/40" />
        </button>

        <!-- Action Row 4: 评测记录 overlay -->
        <button
          @click="handleOpenHistoryModal"
          class="w-full bg-brand-paper/40 hover:bg-brand-paper/85 border border-gray-100/60 rounded-xl p-3.5 flex items-center justify-between cursor-pointer outline-none font-sans text-[12.5px] font-bold text-brand-secondary"
        >
          <span class="flex items-center gap-2.5">
            <History :size="15" class="text-brand-primary" />
            <span>评测记录</span>
          </span>
          <ArrowRight :size="14" class="text-brand-secondary/40" />
        </button>

        <!-- Action Row 5: 修改密码 (Visible if logged-in) -->
        <button
          v-if="isLoggedIn"
          @click="showPasswordModal = true"
          class="w-full bg-brand-paper/40 hover:bg-brand-paper/85 border border-gray-100/60 rounded-xl p-3.5 flex items-center justify-between cursor-pointer outline-none font-sans text-[12.5px] font-bold text-brand-secondary"
        >
          <span class="flex items-center gap-2.5">
            <Key :size="15" class="text-brand-primary" />
            <span>修改密码</span>
          </span>
          <ArrowRight :size="14" class="text-brand-secondary/40" />
        </button>

        <!-- Action Row 6: 反馈问题 -->
        <button
          @click="showFeedbackModal = true"
          class="w-full bg-brand-paper/40 hover:bg-brand-paper/85 border border-gray-100/60 rounded-xl p-3.5 flex items-center justify-between cursor-pointer outline-none font-sans text-[12.5px] font-bold text-brand-secondary"
        >
          <span class="flex items-center gap-2.5">
            <MessageSquare :size="15" class="text-brand-primary" />
            <span>反馈问题</span>
          </span>
          <ArrowRight :size="14" class="text-brand-secondary/40" />
        </button>

        <!-- Action Row 7: 退出登录 (Visible if logged-in) -->
        <button
          v-if="isLoggedIn"
          @click="showLogoutConfirmModal = true"
          class="w-full bg-rose-50 hover:bg-rose-100 border border-thin border-rose-100 rounded-xl p-3.5 flex items-center justify-between cursor-pointer outline-none font-sans text-[12.5px] font-bold text-rose-600"
        >
          <span class="flex items-center gap-2.5">
            <LogOut :size="15" />
            <span>退出登录</span>
          </span>
          <ArrowRight :size="14" class="text-rose-400" />
        </button>
      </div>
    </section>

    <!-- Centered Brand Footer -->
    <footer class="text-center py-6 select-none shrink-0">
      <p class="font-serif text-[11px] font-extrabold text-zinc-400 tracking-wider">
        易如反掌 / EaseWise
      </p>
    </footer>

    <!-- PROFILE EDITOR MODAL -->
    <transition name="fade">
      <div v-if="showNicknameModal" class="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
        <div class="bg-white rounded-3xl w-full max-w-sm p-5 border border-brand-paper shadow-2xl relative">
          <h3 class="font-serif text-[16px] font-bold text-brand-ink-strong mb-4">修改昵称</h3>
          <input
            v-model="nicknameForm"
            type="text"
            placeholder="请输入您新的雅致昵称..."
            class="w-full bg-brand-paper/40 px-3.5 py-3 rounded-2xl border border-gray-150 outline-none text-[13px] text-brand-ink font-sans mb-4"
          />
          <div class="flex gap-3">
            <button
              @click="showNicknameModal = false"
              class="flex-1 py-3 bg-brand-paper hover:bg-zinc-100 text-brand-secondary text-[12.5px] font-bold rounded-2xl cursor-pointer border border-gray-150 outline-none"
            >
              取消
            </button>
            <button
              @click="handleUpdateProfile"
              class="flex-1 py-3 bg-brand-primary text-white text-[12.5px] font-bold rounded-2xl cursor-pointer hover:bg-brand-primary/95 shadow-md outline-none border-none"
            >
              完成修改
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- PASSWORD CHANGE MODAL -->
    <transition name="fade">
      <div v-if="showPasswordModal" class="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
        <div class="bg-white rounded-3xl w-full max-w-sm p-5 border border-brand-paper shadow-2xl relative">
          <h3 class="font-serif text-[16px] font-bold text-brand-ink-strong mb-4">修改密码</h3>
          <div class="space-y-3 mb-4">
            <input
              v-model="passwordForm.current"
              type="password"
              placeholder="当前旧登录密码..."
              class="w-full bg-brand-paper/40 px-3.5 py-3 rounded-2xl border border-gray-150 outline-none text-[13px] text-brand-ink font-sans"
            />
            <input
              v-model="passwordForm.next"
              type="password"
              placeholder="设置新登录密码..."
              class="w-full bg-brand-paper/40 px-3.5 py-3 rounded-2xl border border-gray-150 outline-none text-[13px] text-brand-ink font-sans"
            />
            <input
              v-model="passwordForm.confirm"
              type="password"
              placeholder="再次确认新密码确认..."
              class="w-full bg-brand-paper/40 px-3.5 py-3 rounded-2xl border border-gray-150 outline-none text-[13px] text-brand-ink font-sans"
            />
          </div>
          <div class="flex gap-3">
            <button
              @click="showPasswordModal = false"
              class="flex-1 py-3 bg-brand-paper hover:bg-zinc-100 text-brand-secondary text-[12.5px] font-bold rounded-2xl cursor-pointer border border-gray-150 outline-none"
            >
              取消
            </button>
            <button
              @click="handleUpdatePassword"
              class="flex-1 py-3 bg-brand-primary text-white text-[12.5px] font-bold rounded-2xl cursor-pointer hover:bg-brand-primary/95 shadow-md outline-none border-none"
            >
              重设密码
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- PRODUCT FEEDBACK MODAL -->
    <transition name="fade">
      <div v-if="showFeedbackModal" class="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
        <div class="bg-white rounded-3xl w-full max-w-sm p-5 border border-brand-paper shadow-2xl relative">
          <h3 class="font-serif text-[16px] font-bold text-brand-ink-strong mb-2 flex items-center gap-1.5 leading-tight">
            <span>反馈问题</span>
          </h3>
          <p class="font-sans text-[11.5px] text-brand-secondary leading-relaxed mb-3">
            产品使用中遇到任何问题或体验不佳，请随时向我们反馈，开发团队将用心改进。
          </p>

          <textarea
            v-model="feedbackText"
            placeholder="请输入您对 EaseWise 的反馈与产品建议..."
            rows="4"
            class="w-full bg-brand-paper/35 p-3 rounded-2xl border border-gray-150 outline-none text-[12.5px] text-brand-ink font-sans mb-4 resize-none leading-relaxed"
          ></textarea>

          <div class="flex gap-3">
            <button
              @click="showFeedbackModal = false"
              class="flex-1 py-3 bg-brand-paper hover:bg-zinc-100 text-brand-secondary text-[12.5px] font-bold rounded-2xl cursor-pointer border border-gray-150 outline-none"
            >
              取消
            </button>
            <button
              @click="handleSendFeedback"
              :disabled="!feedbackText.trim()"
              class="flex-1 py-3 bg-brand-primary text-white text-[12.5px] font-bold rounded-2xl cursor-pointer hover:bg-brand-primary/95 shadow-md outline-none border-none disabled:bg-gray-200 disabled:text-gray-400 disabled:cursor-not-allowed"
            >
              提交反馈
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- LOGOUT CONFIRM MODAL -->
    <transition name="fade">
      <div v-if="showLogoutConfirmModal" class="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4">
        <div class="bg-white rounded-3xl w-full max-w-sm p-5 border border-brand-paper shadow-2xl relative">
          <h3 class="font-serif text-[16.5px] font-bold text-brand-ink-strong mb-2">退出登录</h3>
          <p class="font-sans text-[11.5px] text-brand-secondary leading-relaxed mb-4">
            确定要注销当前账号并退出登录吗？您将回到游客模式，可以在之后随时重新登录。
          </p>
          <div class="flex gap-3">
            <button
              @click="showLogoutConfirmModal = false"
              class="flex-1 py-3 bg-brand-paper hover:bg-zinc-100 text-brand-secondary text-[12px] font-bold rounded-2xl cursor-pointer border border-gray-150 outline-none"
            >
              取消
            </button>
            <button
              @click="confirmLogout"
              class="flex-1 py-3 bg-rose-500 hover:bg-rose-600 text-white text-[12px] font-bold rounded-2xl cursor-pointer shadow-md outline-none border-none"
            >
              确认退出
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- LEDGER RECORD MODAL OVERLAY -->
    <transition name="fade">
      <div v-if="showLedgerModal" class="fixed inset-0 z-50 bg-black/45 flex items-center justify-center p-4 backdrop-blur-sm">
        <div class="bg-white rounded-3xl w-full max-w-sm p-6 border border-brand-paper shadow-2xl relative max-h-[80vh] flex flex-col">
          <h3 class="font-serif text-[16px] font-extrabold text-brand-ink-strong mb-4 pb-2 border-b shrink-0 flex items-center justify-between">
            <span>积分记录</span>
            <button @click="showLedgerModal = false" class="text-zinc-400 hover:text-zinc-600 outline-none border-none bg-transparent cursor-pointer p-1">
              <X :size="18" />
            </button>
          </h3>

          <div class="flex-1 overflow-y-auto no-scrollbar pr-0.5 space-y-2.5">
            <div v-if="state.pointsLedger.length === 0" class="flex flex-col items-center justify-center py-12 text-gray-400">
              <Coins :size="28" class="text-zinc-300 mb-2 animate-pulse" />
              <span class="text-[11.5px] font-serif font-bold text-zinc-500">暂无积分收支流水</span>
            </div>
            <div
              v-else
              v-for="item in state.pointsLedger"
              :key="item.ledger_id"
              class="bg-brand-paper/25 rounded-xl p-3 border border-gray-50 flex justify-between items-center"
            >
              <div class="text-left">
                <p class="font-serif text-[12.5px] font-extrabold text-brand-ink-strong">{{ item.remark || '系统礼包积分' }}</p>
                <p class="font-sans text-[10px] text-zinc-400 mt-0.5">{{ new Date(item.created_at).toLocaleString() }}</p>
              </div>
              <span
                class="font-mono text-[13.5px] font-black shrink-0 pl-2"
                :class="item.delta > 0 ? 'text-emerald-600' : 'text-rose-500'"
              >
                {{ item.delta > 0 ? `+${item.delta}` : item.delta }}
              </span>
            </div>
          </div>

          <button
            @click="showLedgerModal = false"
            class="mt-5 w-full py-3 bg-brand-primary text-white text-[12.5px] font-bold rounded-2xl cursor-pointer hover:bg-brand-primary/95 shadow-md border-none outline-none shrink-0"
          >
            完成鉴阅
          </button>
        </div>
      </div>
    </transition>

    <!-- REVIEW HISTORY MODAL OVERLAY -->
    <transition name="fade">
      <div v-if="showHistoryModal" class="fixed inset-0 z-50 bg-black/45 flex items-center justify-center p-4 backdrop-blur-sm">
        <div class="bg-white rounded-3xl w-full max-w-sm p-6 border border-brand-paper shadow-2xl relative max-h-[80vh] flex flex-col">
          <h3 class="font-serif text-[16px] font-extrabold text-brand-ink-strong mb-3 pb-2 border-b shrink-0 flex items-center justify-between">
            <span>评测记录</span>
            <button @click="showHistoryModal = false" class="text-zinc-400 hover:text-zinc-600 outline-none border-none bg-transparent cursor-pointer p-1">
              <X :size="18" />
            </button>
          </h3>

          <!-- Sub-selection tabs inside the history modal -->
          <div class="flex border border-gray-150 rounded-xl overflow-hidden shrink-0 font-sans text-[11.5px] font-bold select-none mb-4.5 bg-zinc-50">
            <button
              @click="activeHistoryTab = 'phone'"
              class="flex-1 py-2 cursor-pointer outline-none border-none font-bold"
              :class="activeHistoryTab === 'phone' ? 'bg-brand-primary text-white font-black' : 'bg-transparent text-brand-secondary hover:bg-zinc-100'"
            >
              手机奇门
            </button>
            <button
              @click="activeHistoryTab = 'bazi'"
              class="flex-1 py-2 cursor-pointer outline-none border-none font-bold"
              :class="activeHistoryTab === 'bazi' ? 'bg-brand-primary text-white font-black' : 'bg-transparent text-brand-secondary hover:bg-zinc-100'"
            >
              生辰八字
            </button>
          </div>

          <div class="flex-1 overflow-y-auto no-scrollbar pr-0.5 space-y-2.5">
            <!-- Case 1: Phone evaluations list -->
            <div v-if="activeHistoryTab === 'phone'" class="space-y-2.5">
              <div v-if="state.reviewHistory.length === 0" class="flex flex-col items-center justify-center py-12 text-gray-400">
                <Compass :size="28" class="text-zinc-300 animate-pulse mb-2" />
                <span class="text-[11.5px] font-serif font-bold text-zinc-500">暂无手机格局评断记录</span>
              </div>
              <div
                v-else
                v-for="item in state.reviewHistory"
                :key="item.id"
                @click="handleLoadHistoryPhone(item.id); showHistoryModal = false"
                class="bg-brand-paper/25 hover:bg-brand-paper/70 rounded-xl p-3 border border-gray-100 cursor-pointer transition-colors flex items-center justify-between"
              >
                <div class="text-left">
                  <p class="font-serif text-[13px] font-bold text-brand-ink-strong flex items-center gap-1.5">
                    <Phone :size="12" class="text-brand-primary shrink-0" />
                    <span class="font-mono font-bold">{{ item.masked_phone }}</span>
                    <span class="text-[9.5px] font-sans px-1.5 py-0.5 bg-brand-primary/10 text-brand-primary-strong rounded">
                      {{ item.gender === 'female' ? '坤造' : '乾造' }}
                    </span>
                  </p>
                  <p class="font-sans text-[10px] text-zinc-400 mt-1">
                    评析得分: {{ item.score }} 分 · {{ new Date(item.created_at).toLocaleDateString() }}
                  </p>
                </div>
                <ArrowRight :size="13" class="text-zinc-400 shrink-0" />
              </div>
            </div>

            <!-- Case 2: Bazi evaluations list -->
            <div v-if="activeHistoryTab === 'bazi'" class="space-y-2.5">
              <div v-if="state.fourPillarsHistory.length === 0" class="flex flex-col items-center justify-center py-12 text-gray-400">
                <Calendar :size="28" class="text-zinc-300 mb-2" />
                <span class="text-[11.5px] font-serif font-bold text-zinc-500">暂无八字排命盘记录</span>
              </div>
              <div
                v-else
                v-for="item in state.fourPillarsHistory"
                :key="item.id"
                @click="handleLoadHistoryBazi(item.id); showHistoryModal = false"
                class="bg-brand-paper/25 hover:bg-brand-paper/70 rounded-xl p-3 border border-gray-100 cursor-pointer transition-colors flex items-center justify-between"
              >
                <div class="text-left">
                  <p class="font-serif text-[13px] font-bold text-brand-ink-strong flex items-center gap-1.5">
                    <Calendar :size="12" class="text-brand-primary shrink-0" />
                    <span class="font-mono">{{ item.birth_date }}</span>
                    <span class="text-[9.5px] font-sans px-1.5 py-0.5 bg-brand-primary/10 text-brand-primary-strong rounded">
                      {{ item.gender === 'female' ? '坤造' : '乾造' }}
                    </span>
                  </p>
                  <p class="font-sans text-[10px] text-zinc-400 mt-1">
                    排盘总分: {{ item.score }} 分
                  </p>
                </div>
                <ArrowRight :size="13" class="text-zinc-400 shrink-0" />
              </div>
            </div>
          </div>

          <button
            @click="showHistoryModal = false"
            class="mt-5 w-full py-3 bg-brand-primary text-white text-[12.5px] font-bold rounded-2xl cursor-pointer hover:bg-brand-primary/95 shadow-md border-none outline-none shrink-0"
          >
            完成鉴阅
          </button>
        </div>
      </div>
    </transition>

    <!-- SYSTEM INTRO SCREEN OVERLAY -->
    <SystemIntro v-if="showIntroModal" @close="showIntroModal = false" />

    <!-- AMBASSADOR DETAIL SCREEN OVERLAY -->
    <AmbassadorDetail v-if="showAmbassadorModal" :is-promoter="state.user?.identity_level === 'promoter'" :user-uid="userUid" @close="showAmbassadorModal = false" />
  </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
