<script setup lang="ts">
import { computed, ref, onMounted } from 'vue';
import {
  User, Coins, ShieldCheck, HelpCircle, History, LogOut, ChevronRight,
  Sparkles, AlertCircle, Copy, Check, Users, Info, Settings, Lock
} from 'lucide-vue-next';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';

const emit = defineEmits<{
  (e: 'navigate-to', view: string): void;
  (e: 'logout'): void;
}>();

const { state, logout, bootstrapApp, openCustomerServiceModal } = useEaseWiseApp();

const copied = ref(false);
const toast = ref<string | null>(null);

const user = computed(() => state.user);
const points = computed(() => state.points?.balance ?? 0);
const isRegistered = computed(() => !!state.accessToken);

onMounted(() => {
  void bootstrapApp();
});

function showToast(msg: string): void {
  toast.value = msg;
  window.setTimeout(() => {
    toast.value = null;
  }, 2200);
}

function handleCopyUserId(): void {
  if (!user.value?.id) return;
  const uid = user.value.id;
  if (typeof navigator !== 'undefined' && navigator.clipboard) {
    navigator.clipboard.writeText(uid).then(() => {
      copied.value = true;
      setTimeout(() => copied.value = false, 2000);
    }).catch(() => fallbackCopy(uid));
  } else {
    fallbackCopy(uid);
  }
}

function fallbackCopy(text: string): void {
  try {
    const el = document.createElement('textarea');
    el.value = text;
    el.setAttribute('readonly', '');
    el.style.position = 'absolute';
    el.style.left = '-9999px';
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
    copied.value = true;
    setTimeout(() => copied.value = false, 2000);
  } catch (e) {
    showToast('拷贝识别号失败，可长按文本复制。');
  }
}

function handleLogout(): void {
  logout();
  emit('logout');
}

function handleClaimPoints(): void {
  emit('navigate-to', 'points-claim');
}

function handleRecharge(): void {
  emit('navigate-to', 'recharge');
}

function openPointsHelp(): void {
  openCustomerServiceModal('points_insufficient', '个人中心：了解积分额度及结算');
}

function handleModifyPassword(): void {
  if (!isRegistered.value) {
    state.openAuthModal('修改密码');
    return;
  }
  showToast('如需修改账户密码，请联系专属在线客服人工核验并重置。');
}
</script>

<template>
  <div class="pt-4 pb-32 max-w-md mx-auto px-margin-mobile relative text-left">

    <transition name="fade">
      <div v-if="toast" class="fixed top-4 left-1/2 -translate-x-1/2 z-50 bg-brand-ink-strong text-white px-4 py-2.5 rounded-full font-sans text-[12.5px] shadow-lg font-medium flex items-center gap-2 max-w-[85%] whitespace-nowrap">
        <Sparkles :size="14" class="text-brand-accent shrink-0" />
        <span>{{ toast }}</span>
      </div>
    </transition>

    <section class="mb-4">
      <div class="bg-white rounded-2xl p-5 border border-brand-paper shadow-sm relative overflow-hidden">
        <div class="absolute -top-12 -right-12 text-brand-primary/[0.025] font-serif font-black text-[150px] pointer-events-none select-none">
          印
        </div>

        <div class="flex items-center gap-4 relative z-10">
          <div class="w-14 h-14 rounded-full bg-brand-primary/10 border-2 border-brand-primary/30 flex items-center justify-center text-brand-primary shrink-0 select-none text-[22px] font-serif">
            {{ user?.name ? user.name.slice(0, 1) : '易' }}
          </div>
          <div class="min-w-0 flex-1 space-y-1">
            <h2 class="font-serif text-[17px] font-black text-brand-ink-strong truncate">
              {{ user?.name || '易理用户' }}
            </h2>
            <div class="flex items-center gap-1 text-[11px] text-brand-secondary">
              <span class="truncate">标识：{{ user?.id ? user.id.slice(0, 12) + '...' : '未登录游客' }}</span>
              <button
                v-if="user?.id"
                @click="handleCopyUserId"
                class="p-1 hover:bg-gray-100 rounded text-brand-primary cursor-pointer select-none outline-none border-none bg-transparent"
                title="复制完整识别号"
              >
                <component :is="copied ? Check : Copy" :size="11" />
              </button>
            </div>
          </div>

          <div class="shrink-0 select-none">
            <button
              v-if="!isRegistered"
              @click="state.openAuthModal('个人中心登录')"
              class="bg-brand-primary hover:bg-brand-primary/95 text-white py-1.5 px-3.5 rounded-xl font-sans text-[11.5px] font-black shadow-sm active:scale-95 transition-all outline-none border-none cursor-pointer"
            >
              登入账号
            </button>
            <span v-else class="px-2.5 py-1 bg-brand-primary/10 text-brand-primary-strong text-[9px] font-extrabold rounded border border-brand-primary/20">
              已成功登录
            </span>
          </div>
        </div>
      </div>
    </section>

    <!-- Balance stats cards -->
    <section class="grid grid-cols-2 gap-3 mb-4">
      <div class="bg-white rounded-2xl p-4 border border-brand-paper shadow-sm text-left relative overflow-hidden select-none">
        <div class="flex items-center justify-between mb-2">
          <span class="text-[11px] text-brand-secondary font-bold">易理积分余额</span>
          <button @click="openPointsHelp" class="text-brand-secondary/80 hover:text-brand-primary cursor-pointer outline-none border-none bg-transparent">
            <HelpCircle :size="13" />
          </button>
        </div>
        <div class="flex items-baseline gap-1">
          <span class="font-serif text-[26px] font-black text-brand-primary-strong">{{ points }}</span>
          <span class="text-[11px] text-brand-secondary font-bold">分</span>
        </div>
        <button
          @click="handleRecharge"
          class="mt-3 w-full bg-brand-primary/10 hover:bg-brand-primary/15 text-brand-primary-strong border-none py-1.5 rounded-xl cursor-pointer font-sans text-[11px] font-extrabold shadow-sm active:scale-[0.97] transition-all flex items-center justify-center gap-1 outline-none"
        >
          <Coins :size="11" />
          <span>获取额度积分</span>
        </button>
      </div>

      <div class="bg-white rounded-2xl p-4 border border-brand-paper shadow-sm text-left relative overflow-hidden select-none">
        <div class="flex items-center justify-between mb-2">
          <span class="text-[11px] text-brand-secondary font-bold">推荐大使奖励</span>
          <span class="px-1.5 py-0.5 bg-emerald-100 text-emerald-800 rounded text-[8px] font-extrabold uppercase tracking-wide">推广特权</span>
        </div>
        <div class="flex items-baseline gap-1">
          <span class="font-serif text-[26px] font-black text-emerald-700">0.00</span>
          <span class="text-[11px] text-brand-secondary font-bold">元</span>
        </div>
        <button
          @click="emit('navigate-to', 'ambassador')"
          class="mt-3 w-full bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border-none py-1.5 rounded-xl cursor-pointer font-sans text-[11px] font-extrabold shadow-sm active:scale-[0.97] transition-all flex items-center justify-center gap-1 outline-none"
        >
          <Users :size="11" />
          <span>查看推广大使</span>
        </button>
      </div>
    </section>

    <!-- Action links section -->
    <section class="bg-white rounded-2xl p-2 border border-brand-paper shadow-sm mb-4">
      <div class="space-y-0.5">
        <button
          v-for="item in [
            { name: '往期数字奇门报告', icon: History, action: () => emit('navigate-to', 'phone-analysis') },
            { name: '往期四柱八字报告', icon: ShieldCheck, action: () => emit('navigate-to', 'bazi') },
            { name: '每日积分额度领取', icon: Sparkles, action: handleClaimPoints },
            { name: '了解系统核心及卦术背景', icon: Info, action: () => emit('navigate-to', 'system-intro') },
            { name: '修改账户登录密码', icon: Settings, action: handleModifyPassword }
          ]"
          :key="item.name"
          @click="item.action"
          class="w-full bg-transparent hover:bg-zinc-50 border-none p-3.5 flex justify-between items-center cursor-pointer rounded-xl transition-all outline-none group select-none"
        >
          <div class="flex items-center gap-3 text-brand-ink-strong">
            <component :is="item.icon" :size="16" class="text-brand-secondary/80 group-hover:text-brand-primary" />
            <span class="font-sans text-[12.5px] font-extrabold">{{ item.name }}</span>
          </div>
          <ChevronRight :size="14" class="text-zinc-300 group-hover:translate-x-0.5 transition-transform" />
        </button>
      </div>
    </section>

    <button
      v-if="isRegistered"
      @click="handleLogout"
      class="w-full bg-red-50 hover:bg-red-100 text-red-600 border-none py-3 rounded-2xl cursor-pointer font-sans text-[12px] font-extrabold shadow-sm active:scale-[0.985] transition-all flex items-center justify-center gap-1.5 outline-none select-none"
    >
      <LogOut :size="14" />
      <span>注销当前账户登录</span>
    </button>
  </div>
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
</style>
