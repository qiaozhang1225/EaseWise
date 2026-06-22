<script setup lang="ts">
import { ref, computed } from 'vue';
import {
  X, Phone, Key, HelpCircle, Loader2, ArrowRight, ShieldCheck,
  Lock, Eye, EyeOff, MessageSquare, AlertCircle, ShieldAlert
} from 'lucide-vue-next';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';

const {
  state, checkPhoneAuthStatus, registerWithPhonePassword, loginWithPhonePassword,
  cancelAuthRequest, humanizeError
} = useEaseWiseApp();

type AuthMode = 'options' | 'phone' | 'login' | 'register' | 'forgot_password' | 'wechat_loading';

const mode = ref<AuthMode>('options');
const phone = ref('');
const password = ref('');
const confirmPassword = ref('');
const errorText = ref<string | null>(null);

const maxPhoneLength = 11;
const isCheckingPhone = ref(false);
const isSubmitting = ref(false);
const passwordVisible = ref(false);

const loginActionText = computed(() => {
  const reason = state.authPromptReason || 'default';
  if (/智能体|对话/u.test(reason)) return '开启智能体对话';
  if (/个人中心|个人主页|积分记录|评测记录|修改用户名|修改密码/u.test(reason)) return '开启个人中心';
  if (/充值|支付|套餐/u.test(reason)) return '开启积分充值';
  return '开始同修评测';
});

function handleReset() {
  phone.value = '';
  password.value = '';
  confirmPassword.value = '';
  errorText.value = null;
  mode.value = 'options';
  passwordVisible.value = false;
}

function handleClose() {
  handleReset();
  cancelAuthRequest();
}

function validatePhoneInput(): string | null {
  const normalizedPhone = phone.value.replace(/\D/g, '');
  if (!/^1[3-9]\d{9}$/.test(normalizedPhone)) {
    errorText.value = '请输入正确的中国大陆 11 位手机号码。';
    return null;
  }
  phone.value = normalizedPhone;
  return normalizedPhone;
}

function validatePasswordStrength(value: string): boolean {
  if (value.trim() !== value) return false;
  if (value.length < 8 || value.length > 32) return false;
  if (new Set(value).size <= 1) return false;
  const categoryCount = [
    /\d/.test(value),
    /[a-zA-Z]/.test(value),
    /[^a-zA-Z0-9]/.test(value),
  ].filter(Boolean).length;
  return categoryCount >= 2;
}

async function handleNextStep() {
  errorText.value = null;
  const normalized = validatePhoneInput();
  if (!normalized) return;

  isCheckingPhone.value = true;
  try {
    const res = await checkPhoneAuthStatus(normalized);
    if (res.status === 'registered') {
      mode.value = 'login';
    } else {
      mode.value = 'register';
    }
  } catch (err) {
    // Falls back to new registration in preview mode for a seamless experience
    mode.value = 'register';
  } finally {
    isCheckingPhone.value = false;
  }
}

async function handleLogin() {
  errorText.value = null;
  const normalized = phone.value.replace(/\D/g, '');
  if (!password.value) {
    errorText.value = '请填写登录密钥密码。';
    return;
  }

  isSubmitting.value = true;
  try {
    await loginWithPhonePassword(normalized, password.value);
    handleReset();
  } catch (err: any) {
    errorText.value = humanizeError(err) || '账户或安全码校验未通过';
  } finally {
    isSubmitting.value = false;
  }
}

async function handleRegister() {
  errorText.value = null;
  const normalized = phone.value.replace(/\D/g, '');

  if (!password.value) {
    errorText.value = '请设定灵阁登录安全密码。';
    return;
  }

  if (!validatePasswordStrength(password.value)) {
    errorText.value = '密码强度未达准：须包含字母、数字、特殊符号任意两类组合，长度 8-32 位，不可含空格。';
    return;
  }

  if (password.value !== confirmPassword.value) {
    errorText.value = '两次设定密码前后不一致，请重新校对。';
    return;
  }

  isSubmitting.value = true;
  try {
    await registerWithPhonePassword(normalized, password.value, confirmPassword.value);
    handleReset();
  } catch (err: any) {
    errorText.value = humanizeError(err) || '安全注册同修账号失败';
  } finally {
    isSubmitting.value = false;
  }
}

function handleWeChatEntry() {
  mode.value = 'wechat_loading';
  setTimeout(() => {
    errorText.value = '通知：微信快捷同修接口被官方系统保留中，请选用「手机验证/密码」快捷注册登录。';
    mode.value = 'options';
  }, 1800);
}

function showSupportScene() {
  state.contactServiceModalVisible = true;
  state.contactServiceScene = 'default';
  state.contactServiceContext = `忘记密码：绑定的手机号为 ${phone.value || '未输入'}`;
}
</script>

<template>
  <transition name="fade">
    <div
      v-if="state.authPromptVisible"
      class="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4"
    >
      <div class="bg-white rounded-3xl w-full max-w-sm p-6 border border-brand-paper shadow-2xl relative text-left">
        <!-- Close button helper -->
        <button
          @click="handleClose"
          class="absolute top-4 right-4 text-brand-secondary/50 hover:text-brand-ink-strong cursor-pointer p-1.5 rounded-full hover:bg-gray-100 border-none bg-transparent outline-none transition-colors"
        >
          <X :size="16" />
        </button>

        <!-- Dynamic Context Alert -->
        <div class="mb-4 pr-6 select-none" v-if="state.authPromptReason">
          <div class="bg-brand-primary/10 border border-brand-primary/20 rounded-xl px-3 py-2 flex items-center gap-2">
            <ShieldCheck :size="14" class="text-brand-primary shrink-0" />
            <span class="font-sans text-[11px] font-extrabold text-brand-primary-strong">
              前置鉴章 · {{ loginActionText }}
            </span>
          </div>
        </div>

        <!-- Typography Heading -->
        <div class="mb-5 select-none">
          <h2 class="font-serif text-[18px] font-black text-brand-ink-strong flex items-center gap-1.5 leading-tight">
            <span>绑定同修灵元</span>
          </h2>
          <p class="font-sans text-[11px] text-brand-secondary mt-1 leading-relaxed">
            易如反掌同修阁通过统一的安全验证，保障您在本平台的全部奇门卦象与积分财产云端安全同步。
          </p>
        </div>

        <!-- System Error display -->
        <transition name="shrink">
          <div
            v-if="errorText"
            class="mb-4 bg-amber-50 border border-amber-200/55 text-zinc-700/90 rounded-xl px-3.5 py-2.5 text-[11px] font-sans leading-normal flex items-start gap-2 animate-fadeIn"
          >
            <AlertCircle :size="14" class="text-brand-gold-fixed shrink-0 mt-0.5" />
            <span>{{ errorText }}</span>
          </div>
        </transition>

        <!-- STATE 1: OPTIONS CHOICE -->
        <div v-if="mode === 'options'" class="space-y-3.5 pt-1">
          <button
            @click="handleWeChatEntry()"
            class="w-full bg-[#07C160] hover:bg-[#06B054] text-white py-3 px-4 rounded-xl font-sans text-[13px] font-bold flex items-center justify-center gap-2 cursor-pointer border-none shadow-sm active:scale-[0.99] transition-all outline-none"
          >
            <!-- Custom WeChat SVG Icon -->
            <svg class="w-5 h-5 fill-current" viewBox="0 0 24 24">
              <path d="M8.3 2C4 2 1 4.7 1 8c0 1.9 1.1 3.5 2.8 4.6l-.7 2c-.1.3 0 .5.3.4l2.4-1.2c.8.2 1.6.3 2.5.3 4.3 0 7.7-2.7 7.7-6s-3.4-6-7.7-6zm8.8 6.5c-.3 0-.5.1-.7.2.7.7 1.1 1.7 1.1 2.8 0 2.2-2.1 4-4.6 4-.5 0-.9-.1-1.3-.2l1.6.8c.2.1.3.4.2.6l-.4 1.3 1.5-.8c.5.1 1 .2 1.5.2 3.6 0 6.5-2.2 6.5-5s-2.9-4.9-6.5-4.9zm-4.3-1.3c0-.4-.4-.8-.8-.8s-.8.4-.8.8.4.8.8.8.8-.4.8-.8zm4.5 0c0-.4-.4-.8-.8-.8s-.8.4-.8.8.4.8.8.8.8-.4.8-.8zm-8 4c0-.3-.3-.6-.6-.6s-.6.3-.6.6.3.6.6.6.6-.3.6-.6zm3.5 0c0-.3-.3-.6-.6-.6s-.6.3-.6.6.3.6.6.6.6-.3.6-.6z"/>
            </svg>
            <span>微信扫码极速快捷注册</span>
          </button>

          <div class="relative py-2 select-none text-center">
            <span class="absolute inset-x-0 top-1/2 -translate-y-1/2 h-[1px] bg-zinc-100"></span>
            <span class="relative bg-white font-sans text-[10px] text-zinc-400 font-bold px-3">或使用手机安全登录</span>
          </div>

          <button
            @click="mode = 'phone'"
            class="w-full bg-brand-paper/50 hover:bg-brand-paper border border-gray-150 py-3.5 px-4 rounded-xl font-sans text-[12.5px] font-extrabold text-brand-ink-strong flex items-center justify-center gap-2 cursor-pointer shadow-sm active:scale-[0.99] transition-all outline-none"
          >
            <Phone :size="15" class="text-brand-primary" />
            <span>大陆手机账户安全绑定 / 注册</span>
          </button>
        </div>

        <!-- STATE 2: PHONE INPUT -->
        <div v-else-if="mode === 'phone'" class="space-y-4">
          <div class="space-y-1.5">
            <span class="font-sans text-[11px] font-bold text-brand-secondary block">手机号（11位中国大陆号）</span>
            <div class="relative flex items-center">
              <input
                v-model="phone"
                type="tel"
                :maxlength="maxPhoneLength"
                placeholder="请输入您的手机号..."
                class="w-full bg-brand-paper/40 px-4 py-3 rounded-2xl border border-gray-150 outline-none font-sans text-[13px] text-brand-ink pl-10"
                @keyup.enter="handleNextStep()"
              />
              <Phone :size="14" class="absolute left-3.5 text-brand-secondary/60" />
            </div>
          </div>

          <div class="flex gap-2">
            <button
              @click="mode = 'options'"
              class="flex-1 bg-brand-paper hover:bg-zinc-100 text-brand-secondary border border-gray-150 py-3 rounded-2xl cursor-pointer font-sans text-[12.5px] font-bold outline-none"
            >
              返回
            </button>
            <button
              @click="handleNextStep()"
              :disabled="isCheckingPhone"
              class="flex-2 bg-brand-primary hover:bg-brand-primary/95 text-white border-none py-3 rounded-2xl cursor-pointer font-sans text-[12.5px] font-bold shadow-md active:scale-[0.98] transition-all flex items-center justify-center gap-1.5 outline-none"
            >
              <Loader2 v-if="isCheckingPhone" class="animate-spin text-white" :size="14" />
              <span>验证并下一步</span>
              <ArrowRight v-if="!isCheckingPhone" :size="14" />
            </button>
          </div>
        </div>

        <!-- STATE 3: INTERACTIVE LOGIN -->
        <div v-else-if="mode === 'login'" class="space-y-4">
          <p class="font-sans text-[10.5px] text-brand-secondary/80 select-none">
            该手机号 <strong>{{ phone }}</strong> 在本灵阁已完成注册，请输入密令登录。
          </p>

          <div class="space-y-1.5">
            <span class="font-sans text-[11px] font-bold text-brand-secondary block">同修登录密钥</span>
            <div class="relative flex items-center">
              <input
                v-model="password"
                :type="passwordVisible ? 'text' : 'password'"
                placeholder="请输入登录密钥密码..."
                class="w-full bg-brand-paper/40 px-4 py-3 rounded-2xl border border-gray-150 outline-none font-sans text-[13px] text-brand-ink pl-10 pr-10"
                @keyup.enter="handleLogin()"
              />
              <Lock :size="14" class="absolute left-3.5 text-brand-secondary/60" />
              <button
                type="button"
                @click="passwordVisible = !passwordVisible"
                class="absolute right-3.5 border-none bg-transparent cursor-pointer text-brand-secondary/50 hover:text-brand-ink outline-none"
              >
                <Eye v-if="passwordVisible" :size="14" />
                <EyeOff v-else :size="14" />
              </button>
            </div>
          </div>

          <div class="flex items-center justify-between font-sans text-[11px] select-none text-brand-secondary">
            <button @click="mode = 'phone'" class="text-brand-primary hover:underline bg-transparent border-none cursor-pointer outline-none font-bold">更换登录号码</button>
            <button @click="mode = 'forgot_password'" class="text-zinc-400 hover:text-brand-primary cursor-pointer bg-transparent border-none outline-none font-bold">忘记密码？</button>
          </div>

          <div class="flex gap-2.5 pt-1">
            <button
              @click="mode = 'phone'"
              class="flex-1 bg-brand-paper hover:bg-zinc-100 text-brand-secondary border border-gray-150 py-3 rounded-2xl cursor-pointer font-sans text-[12.5px] font-bold outline-none"
            >
              返回
            </button>
            <button
              @click="handleLogin()"
              :disabled="isSubmitting"
              class="flex-2 bg-brand-primary hover:bg-brand-primary/95 text-white border-none py-3 rounded-2xl cursor-pointer font-sans text-[12.5px] font-bold shadow-md active:scale-[0.98] transition-all flex items-center justify-center gap-1 outline-none"
            >
              <Loader2 v-if="isSubmitting" class="animate-spin text-white" :size="14" />
              <span>鉴章并登录灵台</span>
            </button>
          </div>
        </div>

        <!-- STATE 4: NEW ACCOUNT REGISTRATION -->
        <div v-else-if="mode === 'register'" class="space-y-4">
          <div class="bg-amber-50 rounded-xl px-3.5 py-2.5 select-none border border-amber-100">
            <p class="font-sans text-[10.5px] text-zinc-600 leading-normal">
              同修缘起：大陆手机 <strong>{{ phone }}</strong> 是本灵台初呈绑定。我们将自然为您创设专属同修档案，并赠送 <strong>50 灵币积分</strong> 礼。
            </p>
          </div>

          <div class="space-y-3">
            <div class="space-y-1.5">
              <span class="font-sans text-[11px] font-bold text-brand-secondary block">设定同修安全密码</span>
              <div class="relative flex items-center">
                <input
                  v-model="password"
                  :type="passwordVisible ? 'text' : 'password'"
                  placeholder="确保字母+数字任意两类，至少8位..."
                  class="w-full bg-brand-paper/40 px-4 py-3 rounded-2xl border border-gray-150 outline-none font-sans text-[13px] text-brand-ink pl-10 pr-10"
                />
                <Lock :size="14" class="absolute left-3.5 text-brand-secondary/60" />
                <button
                  type="button"
                  @click="passwordVisible = !passwordVisible"
                  class="absolute right-3.5 border-none bg-transparent cursor-pointer text-brand-secondary/50 hover:text-brand-ink outline-none"
                >
                  <Eye v-if="passwordVisible" :size="14" />
                  <EyeOff v-else :size="14" />
                </button>
              </div>
            </div>

            <div class="space-y-1.5">
              <span class="font-sans text-[11px] font-bold text-brand-secondary block">再次输入密码以确印</span>
              <div class="relative flex items-center">
                <input
                  v-model="confirmPassword"
                  type="password"
                  placeholder="确保二次录入完全匹配..."
                  class="w-full bg-brand-paper/40 px-4 py-3 rounded-2xl border border-gray-150 outline-none font-sans text-[13px] text-brand-ink pl-10"
                />
                <Key :size="14" class="absolute left-3.5 text-brand-secondary/61" />
              </div>
            </div>
          </div>

          <div class="flex gap-2 pb-1">
            <button
              @click="mode = 'phone'"
              class="flex-1 bg-brand-paper hover:bg-zinc-100 text-brand-secondary border border-gray-150 py-3 rounded-2xl cursor-pointer font-sans text-[12px] font-bold outline-none"
            >
              返回更换
            </button>
            <button
              @click="handleRegister()"
              :disabled="isSubmitting"
              class="flex-2 bg-brand-primary hover:bg-brand-primary/95 text-white border-none py-3 rounded-2xl cursor-pointer font-sans text-[12px] font-bold shadow-md active:scale-[0.98] transition-all flex items-center justify-center gap-1 outline-none"
            >
              <Loader2 v-if="isSubmitting" class="animate-spin text-white" :size="14" />
              <span>同意修册并绑定</span>
            </button>
          </div>
        </div>

        <!-- STATE 5: FORGOT PASSWORD -->
        <div v-else-if="mode === 'forgot_password'" class="space-y-4 pt-1">
          <div class="bg-slate-50 border border-gray-100 rounded-2xl p-4 flex flex-col items-center text-center">
            <ShieldAlert :size="28" class="text-brand-primary mb-2 shrink-0" />
            <span class="font-serif text-[13px] font-bold text-brand-ink-strong">灵台密寄人工校核</span>
            <p class="font-sans text-[11px] text-brand-secondary/90 leading-relaxed mt-2.5">
              为了同修的账号权益安全，目前并不开放免审查的自主修改密码。需要通过官方客服人员进行手机实信对等。
            </p>
          </div>

          <div class="flex gap-2">
            <button
              @click="mode = 'login'"
              class="flex-1 bg-brand-paper hover:bg-zinc-100 text-brand-secondary border border-gray-150 py-3 rounded-2xl cursor-pointer font-sans text-[12.5px] font-bold outline-none"
            >
              返回
            </button>
            <button
              @click="showSupportScene()"
              class="flex-1 bg-brand-primary hover:bg-brand-primary/95 text-white border-none py-3 rounded-2xl cursor-pointer font-sans text-[12.5px] font-bold shadow-md active:scale-[0.98] transition-all flex items-center justify-center gap-1.5 outline-none"
            >
              <MessageSquare :size="14" />
              <span>呼唤客服校正</span>
            </button>
          </div>
        </div>

        <!-- STATE 6: WECHAT LOADING POPUP (Mock placeholder state) -->
        <div v-else-if="mode === 'wechat_loading'" class="flex flex-col items-center justify-center py-10 select-none">
          <Loader2 class="animate-spin text-emerald-500 mb-4" :size="32" />
          <span class="font-serif text-[13.5px] font-bold text-brand-ink-strong">启动微信极速通道中...</span>
          <span class="font-sans text-[10.5px] text-zinc-400 mt-1.5 animate-pulse">正在连入安全微商接口，寻配凭证</span>
        </div>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.25s ease-out;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
.shrink-enter-active, .shrink-leave-active {
  transition: all 0.2s ease-in-out;
}
.shrink-enter-from, .shrink-leave-to {
  transform: scaleY(0);
  opacity: 0;
}
.animate-fadeIn {
  animation: fadeIn 0.2s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
