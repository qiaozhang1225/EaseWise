<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue';
import {
  AlertCircle,
  ArrowRight,
  CheckCircle2,
  ChevronLeft,
  Eye,
  EyeOff,
  Loader2,
  LockKeyhole,
  ShieldCheck,
  Smartphone,
  X,
} from 'lucide-vue-next';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';

const {
  state,
  cancelAuthRequest,
  checkPhoneAuthStatus,
  loginWithPhonePassword,
  customerServiceCopyForScene,
  openCustomerServiceModal,
  registerWithPhonePassword,
  humanizeError,
} = useEaseWiseApp();

type AuthMode = 'options' | 'phone' | 'login' | 'register' | 'forgot_password' | 'wechat_loading';

const mode = ref<AuthMode>('options');
const phone = ref('');
const password = ref('');
const confirmPassword = ref('');
const phoneHint = ref('');
const actionError = ref('');
const submitting = ref(false);
const passwordVisible = ref(false);
const phoneInputRef = ref<HTMLInputElement | null>(null);
const passwordInputRef = ref<HTMLInputElement | null>(null);

const visible = computed(() => state.authPromptVisible);
const promptReason = computed(() => state.authPromptReason || '继续当前操作');
const loginActionText = computed(() => {
  const reason = promptReason.value;
  if (/智能体|对话/u.test(reason)) {
    return '开启对话';
  }
  if (/个人中心|个人主页|积分记录|评测记录|修改用户名|修改密码/u.test(reason)) {
    return '开启个人中心';
  }
  if (/充值|支付|套餐/u.test(reason)) {
    return '开启充值';
  }
  return '开始评测';
});
const loginDialogTitle = computed(() => `立刻登录 · ${loginActionText.value}`);
const dialogTitle = computed(() => {
  if (mode.value === 'forgot_password') {
    return '找回密码';
  }
  if (mode.value === 'register') {
    return '开辟易理账号';
  }
  if (mode.value === 'login') {
    return loginDialogTitle.value;
  }
  if (mode.value === 'phone') {
    return loginDialogTitle.value;
  }
  if (mode.value === 'wechat_loading') {
    return '微信授权待接入';
  }
  return loginDialogTitle.value;
});
const dialogSubtitle = computed(() => {
  if (mode.value === 'forgot_password') {
    return '当前版本尚未接入短信或微信验证，先保留安全指引入口。';
  }
  if (mode.value === 'register') {
    return '建立您在 EaseWise「易如反掌」的数字命盘归位';
  }
  return '登录后方可使用评测及智能体对话功能';
});
const primaryActionLabel = computed(() => {
  if (mode.value === 'forgot_password') {
    return '返回登录';
  }
  if (mode.value === 'register') {
    return '注册';
  }
  if (mode.value === 'login') {
    return '登录';
  }
  return '下一步';
});

watch(visible, (value) => {
  if (value) {
    resetForm();
  }
});

function resetForm(): void {
  mode.value = 'options';
  phone.value = '';
  password.value = '';
  confirmPassword.value = '';
  phoneHint.value = '';
  actionError.value = '';
  submitting.value = false;
  passwordVisible.value = false;
}

function closeModal(): void {
  cancelAuthRequest();
  resetForm();
}

function validatePhoneInput(): string | null {
  const normalizedPhone = phone.value.replace(/\D/g, '');
  if (!/^1[3-9]\d{9}$/.test(normalizedPhone)) {
    actionError.value = '请输入正确的中国大陆手机号码。';
    return null;
  }
  phone.value = normalizedPhone;
  return normalizedPhone;
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

async function handleWechatEntry(): Promise<void> {
  mode.value = 'wechat_loading';
  actionError.value = '微信一键登录入口已预留，请先使用手机号登录/注册完成测试闭环。';
}

function openForgotPasswordHelp(): void {
  mode.value = 'forgot_password';
  actionError.value = '';
  phoneHint.value = '';
}

function openForgotPasswordCustomerService(): void {
  openCustomerServiceModal('account_security');
}

async function handlePhoneNext(): Promise<void> {
  if (submitting.value) {
    return;
  }
  const normalizedPhone = validatePhoneInput();
  if (!normalizedPhone) {
    return;
  }
  submitting.value = true;
  actionError.value = '';
  phoneHint.value = '';
  try {
    const status = await checkPhoneAuthStatus(normalizedPhone);
    if (status.registered) {
      mode.value = 'login';
      phoneHint.value = '该手机号已注册，请直接输入密码登录。';
      await focusPasswordInput();
    } else {
      mode.value = 'register';
      phoneHint.value = '该手机号尚未注册，请先设置密码完成注册。';
      await focusPasswordInput();
    }
  } catch (error) {
    actionError.value = humanizeError(error);
  } finally {
    submitting.value = false;
  }
}

async function handleAuthSubmit(): Promise<void> {
  if (submitting.value) {
    return;
  }
  const normalizedPhone = validatePhoneInput();
  if (!normalizedPhone) {
    return;
  }
  if (mode.value === 'register') {
    if (!validatePasswordStrength(password.value)) {
      actionError.value = '密码强度不足，请使用 8-32 位且至少包含两类字符。';
      return;
    }
    if (password.value !== confirmPassword.value) {
      actionError.value = '两次输入的密码不一致。';
      return;
    }
  }
  if (mode.value === 'login' && !password.value.trim()) {
    actionError.value = '请输入密码。';
    return;
  }

  submitting.value = true;
  actionError.value = '';
  try {
    if (mode.value === 'register') {
      await registerWithPhonePassword(normalizedPhone, password.value, confirmPassword.value);
    } else {
      await loginWithPhonePassword(normalizedPhone, password.value);
    }
  } catch (error) {
    actionError.value = humanizeError(error);
  } finally {
    submitting.value = false;
  }
}

async function handleEnterSubmit(): Promise<void> {
  if (mode.value === 'phone') {
    await handlePhoneNext();
    return;
  }
  if (mode.value === 'login' || mode.value === 'register') {
    await handleAuthSubmit();
  }
}

function switchToPhoneFlow(): void {
  mode.value = 'phone';
  actionError.value = '';
  phoneHint.value = '';
  void focusPhoneInput();
}

function isRegisterMode(): boolean {
  return mode.value === 'register';
}

function handleBack(): void {
  if (mode.value === 'forgot_password') {
    mode.value = 'login';
    actionError.value = '';
    phoneHint.value = '';
    return;
  }
  if (mode.value === 'register' || mode.value === 'login') {
    mode.value = 'phone';
    actionError.value = '';
    phoneHint.value = '';
    return;
  }
  if (mode.value === 'phone' || mode.value === 'wechat_loading') {
    mode.value = 'options';
    actionError.value = '';
    phoneHint.value = '';
    return;
  }
  mode.value = 'options';
}

async function focusPhoneInput(): Promise<void> {
  await nextTick();
  phoneInputRef.value?.focus();
}

async function focusPasswordInput(): Promise<void> {
  await nextTick();
  passwordInputRef.value?.focus();
}
</script>

<template>
  <transition name="fade">
    <div
      v-if="visible"
      class="fixed inset-0 z-[100] bg-slate-900/40 backdrop-blur-md flex items-center justify-center p-4"
      @click.self="closeModal"
    >
      <div class="w-full max-w-sm bg-white border border-brand-primary/15 rounded-3xl overflow-hidden shadow-2xl relative text-left">
        <div class="absolute -top-12 -right-12 text-brand-primary/[0.015] font-serif font-black text-[160px] pointer-events-none select-none">
          ☯
        </div>

        <button
          type="button"
          class="absolute top-4 right-4 w-7 h-7 rounded-full bg-gray-50 border border-gray-100 hover:bg-gray-100 text-gray-400 hover:text-gray-600 flex items-center justify-center hover:scale-105 active:scale-95 transition-all outline-none cursor-pointer z-10"
          @click="closeModal"
        >
          <X :size="14" />
        </button>

        <div class="px-6 pt-7 pb-4 text-center relative">
          <div class="inline-flex items-center justify-center w-11 h-11 rounded-full bg-brand-primary/10 border border-brand-primary/20 mb-3 select-none text-brand-primary text-[20px] font-serif animate-pulse">
            ☯
          </div>

          <transition name="fade" mode="out-in">
            <h2 :key="dialogTitle" class="text-base font-serif font-black text-brand-ink-strong tracking-wider uppercase mb-1">
              {{ dialogTitle }}
            </h2>
          </transition>
          <p class="text-[10px] text-brand-secondary leading-relaxed">
            {{ dialogSubtitle }}
          </p>

          <div
            v-if="promptReason && mode !== 'forgot_password'"
            class="mt-3 bg-brand-primary/5 border border-brand-primary/10 text-brand-primary-strong px-3 py-2 rounded-xl text-[10px] text-left leading-relaxed flex items-start gap-1.5"
          >
            <AlertCircle :size="12" class="shrink-0 mt-0.5 text-brand-primary" />
            <span>为了继续{{ promptReason }}，请先完成登录。</span>
          </div>
        </div>

        <div class="px-6 pb-6 space-y-4 relative">
          <transition name="shake">
            <div
              v-if="actionError"
              class="bg-rose-500/10 border border-rose-500/15 text-rose-700 rounded-xl px-3 py-2 text-[10.5px] leading-relaxed flex items-center gap-2"
            >
              <AlertCircle :size="13" class="shrink-0 text-rose-600" />
              <span>{{ actionError }}</span>
            </div>
          </transition>

          <transition name="fade">
            <div
              v-if="phoneHint"
              class="bg-emerald-500/10 border border-emerald-500/15 text-emerald-700 rounded-xl px-3 py-2 text-[10.5px] leading-relaxed flex items-center gap-2"
            >
              <CheckCircle2 :size="13" class="shrink-0 text-emerald-600" />
              <span>{{ phoneHint }}</span>
            </div>
          </transition>

          <div v-if="mode === 'options'" class="space-y-3">
            <button
              type="button"
              class="w-full py-3 bg-[#07C160] hover:bg-[#06B055] active:scale-[0.98] text-white font-semibold text-xs rounded-xl flex items-center justify-center gap-2 cursor-pointer transition-all outline-none shadow-md"
              @click="handleWechatEntry"
            >
              <span class="text-sm">💬</span>
              <span>微信一键授权安全登录</span>
            </button>

            <button
              type="button"
              class="w-full py-3 bg-brand-primary hover:bg-brand-primary-strong active:scale-[0.98] text-white font-bold text-xs rounded-xl flex items-center justify-center gap-2 cursor-pointer transition-all outline-none border border-transparent shadow-sm"
              @click="switchToPhoneFlow"
            >
              <Smartphone :size="14" />
              <span>常用手机号安全登录 / 注册</span>
            </button>

            <div class="pt-2 text-center select-none">
              <span class="text-[9px] text-brand-secondary/40 uppercase tracking-widest font-mono">
                Secure sandboxed connection verified
              </span>
            </div>
          </div>

          <div v-else-if="mode === 'wechat_loading'" class="py-8 text-center space-y-4">
            <Loader2 class="w-10 h-10 text-[#07C160] animate-spin mx-auto" />
            <div class="space-y-1">
              <p class="text-[12.5px] font-bold text-[#07C160]">微信授权能力预留中...</p>
              <p class="text-[10px] text-brand-secondary">请先使用手机号登录/注册完成当前测试闭环</p>
            </div>
            <button
              type="button"
              class="w-full py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-600 font-bold rounded-xl text-xs flex items-center justify-center gap-1 cursor-pointer transition-all outline-none"
              @click="handleBack"
            >
              <ChevronLeft :size="12" />
              <span>返回登录方式</span>
            </button>
          </div>

          <div v-else-if="mode === 'forgot_password'" class="py-5 space-y-4">
            <div class="mx-auto w-12 h-12 rounded-full bg-amber-500/10 border border-amber-200 text-amber-600 flex items-center justify-center select-none">
              <AlertCircle :size="20" />
            </div>
            <div class="space-y-2 text-center">
              <h3 class="text-[13px] font-bold text-brand-ink-strong">忘记密码暂不支持自助重置</h3>
              <p class="text-[11px] text-brand-secondary leading-relaxed px-1">
                由于短信验证和微信验证暂未接入，为保护账号资产，当前版本不开放直接重置密码。
                你可以先联系客服人工核验，或等待验证能力上线后再使用自助找回。
              </p>
              <div class="rounded-xl bg-brand-paper border border-gray-100 px-3 py-2 text-left text-[10.5px] text-brand-secondary leading-relaxed">
                <p class="font-bold text-brand-ink-strong">客服指引</p>
                <p class="mt-1">{{ customerServiceCopyForScene('account_security') }}</p>
              </div>
            </div>
            <button
              type="button"
              class="w-full py-2.5 bg-brand-primary hover:bg-brand-primary-strong text-white active:scale-95 font-bold rounded-xl text-xs flex items-center justify-center gap-1 cursor-pointer transition-all outline-none border border-transparent shadow-sm"
              @click="openForgotPasswordCustomerService"
            >
              联系客服人工核验
            </button>
            <button
              type="button"
              class="w-full py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-600 active:scale-95 font-bold rounded-xl text-xs flex items-center justify-center gap-1 cursor-pointer transition-all outline-none border border-transparent"
              @click="handleBack"
            >
              <ChevronLeft :size="12" />
              <span>返回登录</span>
            </button>
          </div>

          <form v-else class="space-y-4" @submit.prevent="handleEnterSubmit">
            <div class="space-y-1">
              <div class="flex items-center justify-between gap-2">
                <label class="text-[9px] text-brand-secondary uppercase tracking-wider font-semibold">大陆手机号码</label>
                <button
                  v-if="mode === 'login'"
                  type="button"
                  class="text-[9.5px] text-brand-primary hover:text-brand-primary-strong outline-none cursor-pointer leading-none font-bold"
                  @click="openForgotPasswordHelp"
                >
                  忘记密码？
                </button>
              </div>
              <div class="relative flex items-center bg-brand-paper border border-gray-200 rounded-xl focus-within:border-brand-primary transition-all">
                <span class="pl-3.5 text-[11px] text-brand-primary font-bold">+86</span>
                <span class="h-4 w-px bg-gray-300 mx-2"></span>
                <input
                  ref="phoneInputRef"
                  v-model="phone"
                  type="tel"
                  inputmode="numeric"
                  autocomplete="tel"
                  maxlength="11"
                  placeholder="请输入您的11位大陆号码"
                  class="w-full bg-transparent border-none text-[12px] text-brand-ink py-2.5 pr-3.5 outline-none font-mono placeholder-gray-400"
                />
              </div>
            </div>

            <transition name="slide-down">
              <div v-if="mode !== 'phone'" class="space-y-3">
                <div class="space-y-1">
                  <div class="flex justify-between items-center">
                    <label class="text-[9px] text-brand-secondary uppercase tracking-wider font-semibold">
                      {{ isRegisterMode() ? '设置登入密码' : '账户登入密码' }}
                    </label>
                    <button
                      type="button"
                      class="text-[9.5px] text-brand-primary hover:text-brand-primary-strong outline-none cursor-pointer leading-none font-bold"
                      @click="mode = isRegisterMode() ? 'login' : 'register'; actionError = ''; phoneHint = ''"
                    >
                      {{ isRegisterMode() ? '使用已有密码登录' : '没有账号？立即注册' }}
                    </button>
                  </div>
                  <div class="relative flex items-center bg-brand-paper border border-gray-200 rounded-xl focus-within:border-brand-primary transition-all">
                    <span class="pl-3.5 text-gray-400 shrink-0"><LockKeyhole :size="12" /></span>
                    <span class="h-4 w-px bg-gray-300 mx-2"></span>
                    <input
                      ref="passwordInputRef"
                      v-model="password"
                      :type="passwordVisible ? 'text' : 'password'"
                      autocomplete="current-password"
                      placeholder="8-32位，至少包含两类字符"
                      class="w-full bg-transparent border-none text-[12px] text-brand-ink py-2.5 pr-10 outline-none placeholder-gray-400"
                    />
                    <button
                      type="button"
                      class="absolute right-3.5 text-gray-400 hover:text-gray-600 cursor-pointer select-none outline-none border-none bg-transparent"
                      @click="passwordVisible = !passwordVisible"
                    >
                      <Eye v-if="passwordVisible" :size="13" />
                      <EyeOff v-else :size="13" />
                    </button>
                  </div>
                </div>

                <transition name="slide-down">
                  <div v-if="isRegisterMode()" class="space-y-1">
                    <label class="text-[9px] text-brand-secondary uppercase tracking-wider font-semibold">确认您的登入密码</label>
                    <div class="relative flex items-center bg-brand-paper border border-gray-200 rounded-xl focus-within:border-brand-primary transition-all">
                      <span class="pl-3.5 text-gray-400 shrink-0"><LockKeyhole :size="12" /></span>
                      <span class="h-4 w-px bg-gray-300 mx-2"></span>
                      <input
                        v-model="confirmPassword"
                        type="password"
                        autocomplete="new-password"
                        placeholder="重复输入上方相同的安全密码"
                        class="w-full bg-transparent border-none text-[12px] text-brand-ink py-2.5 pr-3.5 outline-none placeholder-gray-400"
                      />
                    </div>
                  </div>
                </transition>
              </div>
            </transition>

            <div class="flex gap-2 pt-2">
              <button
                type="button"
                class="flex-1 py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-600 font-bold rounded-xl text-xs flex items-center justify-center gap-1 cursor-pointer transition-all outline-none"
                @click="handleBack"
              >
                <ChevronLeft :size="12" />
                <span>{{ mode === 'register' ? '上一步' : '返回' }}</span>
              </button>

              <button
                type="submit"
                class="flex-1 py-2.5 bg-brand-primary hover:bg-brand-primary-strong text-white active:scale-95 font-bold rounded-xl text-xs flex items-center justify-center gap-1 cursor-pointer transition-all outline-none border border-transparent shadow-sm disabled:opacity-60"
                :disabled="submitting"
              >
                <Loader2 v-if="submitting" :size="13" class="animate-spin" />
                <ArrowRight v-else :size="13" />
                <span>{{ submitting ? '处理中' : primaryActionLabel }}</span>
              </button>
            </div>

            <div class="text-center pt-1">
              <span class="text-[9.5px] text-brand-secondary/60">
                当前阶段使用手机号 + 密码闭环，微信一键登录为后续预留。
              </span>
            </div>
          </form>

          <div
            v-if="mode === 'options' || mode === 'phone'"
            class="flex items-start gap-2 pt-2 text-[10px] text-brand-secondary leading-relaxed max-w-[95%] select-none"
          >
            <input
              type="checkbox"
              checked
              disabled
              class="accent-brand-primary rounded border-gray-300 shrink-0 mt-0.5 cursor-pointer"
            />
            <label class="cursor-default">
              <span>登录即代表同意 EaseWise 的</span>
              <span class="text-brand-primary font-bold">《用户服务协议》</span>
              <span>与</span>
              <span class="text-brand-primary font-bold">《隐私保护政策》</span>
              <span>，并允许账号安全同步积分、订单和评测记录。</span>
            </label>
          </div>

          <div class="flex items-center justify-center gap-1 text-[9px] text-brand-secondary/40 select-none bg-gray-50/50 border-t border-gray-100 pt-3">
            <ShieldCheck :size="10" />
            <span>本平台所有内容仅供娱乐，并无参考价值。</span>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.shake-enter-active {
  animation: shake 0.35s ease-in-out;
}

@keyframes shake {
  0%,
  100% {
    transform: translateX(0);
  }
  20%,
  60% {
    transform: translateX(-4px);
  }
  40%,
  80% {
    transform: translateX(4px);
  }
}
</style>
