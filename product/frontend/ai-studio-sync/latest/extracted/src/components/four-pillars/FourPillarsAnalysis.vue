<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import {
  ArrowLeft, RefreshCw, Sparkles, Lock, UnlockKeyhole, CalendarDays,
  MapPin, Compass, TrendingUp, Shield, Heart, HeartPulse, User, Users, BookOpen,
  Loader2, Search, X, Check
} from 'lucide-vue-next';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';
import { getFourPillarsReview, listFourPillarsBirthLocations, resolveFourPillarsInput } from '../../lib/api';
import FourPillarsNatalTable from './FourPillarsNatalTable.vue';
import type { FourPillarsAspect, Gender } from '../../types/api';

const emit = defineEmits<{
  (e: 'back-to-home'): void;
  (e: 'navigate-to-tab', tab: string, params?: Record<string, string>): void;
}>();

const {
  state, isGuestUser, fourPillarsBasePointsCost, fourPillarsAspectUnlockPointsCost,
  submitFourPillarsReviewStream, streamUnlockFourPillarsAspect, generateFourPillarsLuckCycle,
  generateFourPillarsLuckYear, requestRegisteredUser, openCustomerServiceModal, humanizeError
} = useEaseWiseApp();

const viewState = ref<'input' | 'waiting' | 'result' | 'error'>('input');
const activeBranch = ref<'chart' | 'luck'>('chart');
const isSubmitting = ref(false);
const errorMessage = ref('');

// Input forms & Pickers
const gender = ref<Gender>('male');
const birthDate = ref('1990-01-01');
const birthTime = ref('12:00');
const birthPlace = ref('北京市东城区');
const profileName = ref('');
const selectHourZhi = ref('辰');

// Manual-wheel integrated date time state
const yearVal = ref(1990);
const monthVal = ref(1);
const dayVal = ref(1);
const hourVal = ref(12);
const minuteVal = ref(0);

// Calendar mode handling (公历 vs 农历)
const isLunarCalendar = ref(false);

// Bottom drawer states
const showDatePickerDrawer = ref(false);
const showLocationPickerDrawer = ref(false);

// Locations Database
interface DetailedLocation {
  id: string;
  name: string;
  longitude: number;
  latitude: number;
  timezone: string;
  offsetMinutes: number;
}

const LOCATIONS_DB: DetailedLocation[] = [
  { id: 'cn-110101', name: '北京市东城区', longitude: 116.41, latitude: 39.90, timezone: 'Asia/Shanghai', offsetMinutes: -14 },
  { id: 'cn-310101', name: '上海市黄浦区', longitude: 121.47, latitude: 31.23, timezone: 'Asia/Shanghai', offsetMinutes: 6 },
  { id: 'cn-440106', name: '广东省广州市天河区', longitude: 113.26, latitude: 23.13, timezone: 'Asia/Shanghai', offsetMinutes: -27 },
  { id: 'cn-440304', name: '广东省深圳市福田区', longitude: 114.05, latitude: 22.54, timezone: 'Asia/Shanghai', offsetMinutes: -24 },
  { id: 'cn-330102', name: '浙江省杭州市上城区', longitude: 120.15, latitude: 30.28, timezone: 'Asia/Shanghai', offsetMinutes: 1 },
  { id: 'cn-320102', name: '江苏省南京市玄武区', longitude: 118.78, latitude: 32.04, timezone: 'Asia/Shanghai', offsetMinutes: -5 },
  { id: 'cn-510104', name: '四川省成都市锦江区', longitude: 104.06, latitude: 30.67, timezone: 'Asia/Shanghai', offsetMinutes: -64 },
  { id: 'cn-420102', name: '湖北省武汉市江岸区', longitude: 114.30, latitude: 30.58, timezone: 'Asia/Shanghai', offsetMinutes: -23 },
  { id: 'cn-610103', name: '陕西省西安市碑林区', longitude: 108.94, latitude: 34.26, timezone: 'Asia/Shanghai', offsetMinutes: -44 },
  { id: 'cn-500103', name: '重庆市渝中区', longitude: 106.55, latitude: 29.56, timezone: 'Asia/Shanghai', offsetMinutes: -54 },
  { id: 'cn-430102', name: '湖南省长沙市芙蓉区', longitude: 112.93, latitude: 28.23, timezone: 'Asia/Shanghai', offsetMinutes: -28 },
  { id: 'cn-350102', name: '福建省福州市鼓楼区', longitude: 119.30, latitude: 26.08, timezone: 'Asia/Shanghai', offsetMinutes: -3 },
  { id: 'cn-530102', name: '云南省昆明市五华区', longitude: 102.71, latitude: 25.04, timezone: 'Asia/Shanghai', offsetMinutes: -69 },
  { id: 'cn-230102', name: '黑龙江省哈尔滨市道里区', longitude: 126.63, latitude: 45.75, timezone: 'Asia/Shanghai', offsetMinutes: 27 },
  { id: 'cn-650102', name: '新疆乌鲁木齐市天山区', longitude: 87.61, latitude: 43.82, timezone: 'Asia/Shanghai', offsetMinutes: -130 }
];

const selectedLoc = ref<DetailedLocation>(LOCATIONS_DB[0]);
const locationSearchQuery = ref('');

const filteredLocations = computed(() => {
  const q = locationSearchQuery.value.trim().toLowerCase();
  if (!q) return LOCATIONS_DB;
  return LOCATIONS_DB.filter(l => l.name.toLowerCase().includes(q));
});

// Wheel options lists
const yearsArray = Array.from({ length: 111 }, (_, i) => 1930 + i); // 1930 to 2040
const monthsArray = Array.from({ length: 12 }, (_, i) => 1 + i);
const daysArray = computed(() => {
  const daysInMonth = new Date(yearVal.value, monthVal.value, 0).getDate();
  return Array.from({ length: daysInMonth }, (_, i) => 1 + i);
});
const hoursArray = Array.from({ length: 24 }, (_, i) => i);
const minutesArray = Array.from({ length: 60 }, (_, i) => i);

// Synchronization helpers
function syncToNumeric() {
  const dateParts = birthDate.value.split('-');
  if (dateParts.length === 3) {
    yearVal.value = parseInt(dateParts[0]) || 1990;
    monthVal.value = parseInt(dateParts[1]) || 1;
    dayVal.value = parseInt(dateParts[2]) || 1;
  }
  const timeParts = birthTime.value.split(':');
  if (timeParts.length >= 2) {
    hourVal.value = parseInt(timeParts[0]) || 12;
    minuteVal.value = parseInt(timeParts[1]) || 0;
  }
}

function syncToString() {
  // Guard values
  if (yearVal.value < 1930) yearVal.value = 1930;
  if (yearVal.value > 2040) yearVal.value = 2040;
  if (monthVal.value < 1) monthVal.value = 1;
  if (monthVal.value > 12) monthVal.value = 12;
  const maxD = new Date(yearVal.value, monthVal.value, 0).getDate();
  if (dayVal.value < 1) dayVal.value = 1;
  if (dayVal.value > maxD) dayVal.value = maxD;
  if (hourVal.value < 0) hourVal.value = 0;
  if (hourVal.value > 23) hourVal.value = 23;
  if (minuteVal.value < 0) minuteVal.value = 0;
  if (minuteVal.value > 59) minuteVal.value = 59;

  birthDate.value = `${yearVal.value}-${String(monthVal.value).padStart(2, '0')}-${String(dayVal.value).padStart(2, '0')}`;
  birthTime.value = `${String(hourVal.value).padStart(2, '0')}:${String(minuteVal.value).padStart(2, '0')}`;
}

// True Solar Time calculations & preview
const trueSolarTimePreview = computed(() => {
  const loc = selectedLoc.value;
  if (!loc) return { time: '12:00', offsetText: '' };

  const totalMinutes = hourVal.value * 60 + minuteVal.value + loc.offsetMinutes;
  const wrappedMinutes = (totalMinutes + 1440) % 1440;
  const h = Math.floor(wrappedMinutes / 60);
  const m = Math.floor(wrappedMinutes % 60);

  const offsetString = loc.offsetMinutes >= 0 ? `+${loc.offsetMinutes}分钟` : `${loc.offsetMinutes}分钟`;
  return {
    time: `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`,
    offsetText: `经度 ${loc.longitude}° E (基于中原标准时间校准 ${offsetString})`
  };
});

// Result state
const activeAspect = ref(0);
const activeCycleKey = ref('');
const selectedLuckYear = ref<number | null>(null);
const loadingLuck = ref(false);

const currentReview = computed(() => state.currentFourPillarsReview);
const userPoints = computed(() => state.points?.balance ?? 0);
const reviewScore = computed(() => currentReview.value?.score ?? '--');

onMounted(() => {
  syncToNumeric();
  if (currentReview.value) {
    applyFormFromReview(currentReview.value);
    viewState.value = 'result';
  }
});

function applyFormFromReview(review: any) {
  gender.value = review.gender;
  birthDate.value = review.birth_date;
  birthTime.value = review.birth_time;
  birthPlace.value = review.birth_place || '';
  profileName.value = review.name || '';
  syncToNumeric();
  const found = LOCATIONS_DB.find(l => l.name === birthPlace.value);
  if (found) {
    selectedLoc.value = found;
  }
}

function resetToInput() {
  viewState.value = 'input';
}

function selectLocation(loc: DetailedLocation) {
  selectedLoc.value = loc;
  birthPlace.value = loc.name;
  showLocationPickerDrawer.value = false;
}

async function handleStartAnalysis() {
  const authed = await requestRegisteredUser('四柱八字评测');
  if (!authed) return;

  if (userPoints.value < fourPillarsBasePointsCost.value) {
    openCustomerServiceModal('points_insufficient', `四柱扣费：需要 ${fourPillarsBasePointsCost.value} 积分`);
    return;
  }

  viewState.value = 'waiting';
  try {
    await submitFourPillarsReviewStream({
      gender: gender.value,
      birth_date: birthDate.value,
      birth_time: birthTime.value,
      birth_place: birthPlace.value,
      name: profileName.value || null,
      input_mode: isLunarCalendar.value ? 'lunar' : 'solar',
      calendar_input: { birth_date: birthDate.value, birth_time: birthTime.value },
    }, {
      onComplete: (data) => {
        state.currentFourPillarsReview = data.review;
        viewState.value = 'result';
      },
      onError: (err) => {
        errorMessage.value = err.detail || '推演失败';
        viewState.value = 'error';
      }
    });
  } catch (err: any) {
    errorMessage.value = humanizeError(err);
    viewState.value = 'error';
  }
}

async function handleUnlockAspect(aspect: FourPillarsAspect, index: number) {
  activeAspect.value = index;
  if (aspect.is_unlocked) return;

  const authed = await requestRegisteredUser(`解锁“${aspect.title}”`);
  if (!authed) return;

  if (userPoints.value < fourPillarsAspectUnlockPointsCost.value) {
    openCustomerServiceModal('points_insufficient', `解锁扣费：需要 ${fourPillarsAspectUnlockPointsCost.value} 积分`);
    return;
  }

  try {
    await streamUnlockFourPillarsAspect(currentReview.value!.id, aspect.aspect_key);
  } catch (err: any) {
    openCustomerServiceModal('review_support', humanizeError(err));
  }
}


async function handleGenerateCycle(cycle: any) {
  if (cycle.render_status === 'completed') return;
  const authed = await requestRegisteredUser('大运综评');
  if (!authed) return;

  loadingLuck.value = true;
  try {
    await generateFourPillarsLuckCycle(currentReview.value!.id, cycle.cycle_key);
  } catch (err: any) {
    openCustomerServiceModal('review_support', humanizeError(err));
  } finally {
    loadingLuck.value = false;
  }
}

async function handleGenerateYear(cycle: any, yearItem: any) {
  if (yearItem.render_status === 'completed') return;
  const authed = await requestRegisteredUser('流年评测');
  if (!authed) return;

  loadingLuck.value = true;
  try {
    await generateFourPillarsLuckYear(currentReview.value!.id, cycle.cycle_key, yearItem.year);
  } catch (err: any) {
    openCustomerServiceModal('review_support', humanizeError(err));
  } finally {
    loadingLuck.value = false;
  }
}

const reviewAspects = computed(() => {
  const aspects = currentReview.value?.aspects || [];
  const icons: Record<string, any> = {
    personality: Sparkles, wealth: TrendingUp, career: Shield, marriage: Heart, health: HeartPulse, love: Heart, social: Users, pattern: BookOpen
  };
  return aspects.map(a => ({
    ...a,
    icon: icons[a.aspect_key] || Sparkles,
    tint: 'bg-brand-paper text-brand-secondary',
    textTint: 'text-brand-secondary'
  }));
});

const selectedAspect = computed(() => reviewAspects.value[activeAspect.value] || null);

const luckCycles = computed(() => currentReview.value?.luck_analysis?.cycles || []);
const selectedLuckCycle = computed(() => {
  if (!luckCycles.value.length) return null;
  return luckCycles.value.find(c => c.cycle_key === activeCycleKey.value) || luckCycles.value[0];
});

const selectedLuckYearItem = computed(() => {
  const cycle = selectedLuckCycle.value;
  if (!cycle) return null;
  return cycle.year_items.find(y => y.year === selectedLuckYear.value) || cycle.year_items[0];
});
</script>

<template>
  <div class="pt-4 pb-32 max-w-md mx-auto px-margin-mobile text-left">

    <div v-if="viewState === 'input'" class="space-y-4">
      <div class="bg-white rounded-2xl p-5 border border-gray-150 shadow-sm space-y-4">
        <h2 class="font-serif text-[17px] font-bold text-brand-ink-strong flex items-center gap-1.5">
          <Sparkles :size="18" class="text-brand-primary" />
          <span>四柱八字先天命盘</span>
        </h2>

        <div class="space-y-3.5">
          <div>
            <label class="text-[11px] font-bold text-brand-secondary">命盘姓名</label>
            <input v-model="profileName" placeholder="姓名（可选）" class="w-full bg-brand-paper hover:bg-white text-brand-ink-strong focus:bg-white text-[13.5px] p-3 rounded-xl border border-gray-100 outline-none" />
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="text-[11px] font-bold text-brand-secondary">性别属性</label>
              <div class="grid grid-cols-2 bg-brand-paper p-1 rounded-xl border border-gray-100">
                <button @click="gender = 'male'" class="py-2 text-[12px] font-bold rounded-lg transition-all" :class="gender === 'male' ? 'bg-white text-brand-primary shadow-sm' : 'text-brand-secondary'">男命</button>
                <button @click="gender = 'female'" class="py-2 text-[12px] font-bold rounded-lg transition-all" :class="gender === 'female' ? 'bg-white text-brand-primary shadow-sm' : 'text-brand-secondary'">女命</button>
              </div>
            </div>
            <div>
              <label class="text-[11px] font-bold text-brand-secondary">历法选择</label>
              <div class="grid grid-cols-2 bg-brand-paper p-1 rounded-xl border border-gray-100">
                <button @click="isLunarCalendar = false" :class="['py-2 text-[12px] font-bold rounded-lg transition-all', !isLunarCalendar ? 'bg-white text-brand-primary shadow-sm' : 'text-brand-secondary']">公历</button>
                <button @click="isLunarCalendar = true" :class="['py-2 text-[12px] font-bold rounded-lg transition-all', isLunarCalendar ? 'bg-white text-brand-primary shadow-sm' : 'text-brand-secondary']">农历</button>
              </div>
            </div>
          </div>

          <!-- Manual numeric fields with scroll wheel trigger option -->
          <div class="space-y-1">
            <div class="flex justify-between items-center mb-1">
              <label class="text-[11px] font-bold text-brand-secondary">出生时间 (可直接修改或用滑动轮校对)</label>
              <button @click="showDatePickerDrawer = true" class="text-[10px] text-brand-primary hover:underline font-bold flex items-center gap-0.5">
                <CalendarDays :size="12" />
                滑动选择轮
              </button>
            </div>

            <div class="grid grid-cols-5 gap-1.5">
              <!-- Year -->
              <div class="flex flex-col gap-0.5">
                <input v-model.number="yearVal" type="number" min="1930" max="2040" class="w-full text-center bg-brand-paper border border-gray-100 rounded-xl py-2 px-0.5 text-[12.5px] font-bold text-brand-ink-strong focus:border-brand-primary outline-none" @change="syncToString" />
                <span class="text-[9px] text-zinc-400 text-center">年</span>
              </div>
              <!-- Month -->
              <div class="flex flex-col gap-0.5">
                <input v-model.number="monthVal" type="number" min="1" max="12" class="w-full text-center bg-brand-paper border border-gray-100 rounded-xl py-2 px-0.5 text-[12.5px] font-bold text-brand-ink-strong focus:border-brand-primary outline-none" @change="syncToString" />
                <span class="text-[9px] text-zinc-400 text-center">月</span>
              </div>
              <!-- Day -->
              <div class="flex flex-col gap-0.5">
                <input v-model.number="dayVal" type="number" min="1" max="31" class="w-full text-center bg-brand-paper border border-gray-100 rounded-xl py-2 px-0.5 text-[12.5px] font-bold text-brand-ink-strong focus:border-brand-primary outline-none" @change="syncToString" />
                <span class="text-[9px] text-zinc-400 text-center">日</span>
              </div>
              <!-- Hour -->
              <div class="flex flex-col gap-0.5">
                <input v-model.number="hourVal" type="number" min="0" max="23" class="w-full text-center bg-brand-paper border border-gray-100 rounded-xl py-2 px-0.5 text-[12.5px] font-bold text-brand-ink-strong focus:border-brand-primary outline-none" @change="syncToString" />
                <span class="text-[9px] text-zinc-400 text-center">时</span>
              </div>
              <!-- Minute -->
              <div class="flex flex-col gap-0.5">
                <input v-model.number="minuteVal" type="number" min="0" max="59" class="w-full text-center bg-brand-paper border border-gray-100 rounded-xl py-2 px-0.5 text-[12.5px] font-bold text-brand-ink-strong focus:border-brand-primary outline-none" @change="syncToString" />
                <span class="text-[9px] text-zinc-400 text-center">分</span>
              </div>
            </div>
          </div>

          <!-- Location Picker Button -->
          <div class="space-y-1">
            <label class="text-[11px] font-bold text-brand-secondary">出生城市 (经纬度真太阳时校准)</label>
            <button @click="showLocationPickerDrawer = true" class="w-full flex items-center justify-between bg-brand-paper hover:bg-zinc-50 text-brand-ink-strong text-[13px] font-semibold p-3 rounded-xl border border-gray-100 outline-none text-left transition-colors">
              <span class="flex items-center gap-1.5 text-brand-ink-strong font-bold">
                <MapPin :size="14" class="text-brand-primary" />
                {{ selectedLoc ? selectedLoc.name : '选择出生城市' }}
              </span>
              <span class="text-[11px] text-brand-primary font-bold">点击选择</span>
            </button>
          </div>

          <!-- Location True Solar Time Context Preview Card -->
          <div v-if="selectedLoc" class="bg-brand-primary/5 rounded-xl p-3.5 border border-brand-primary/10 flex items-center justify-between">
            <div class="space-y-0.5">
              <span class="text-[9px] text-brand-primary font-bold uppercase tracking-wider block">真太阳时校准</span>
              <span class="font-serif text-[15px] font-black text-brand-ink-strong block">{{ trueSolarTimePreview.time }}</span>
              <span class="text-[8px] text-brand-secondary block leading-snug">{{ trueSolarTimePreview.offsetText }}</span>
            </div>
            <div class="text-right space-y-0.5 shrink-0">
              <span class="text-[9px] text-brand-secondary block font-bold">校准位置</span>
              <span class="font-serif text-[11px] font-bold text-brand-primary block">{{ selectedLoc.name }}</span>
              <span class="text-[8px] text-brand-secondary block">时区：{{ selectedLoc.timezone }}</span>
            </div>
          </div>

          <button @click="handleStartAnalysis" class="w-full h-11 bg-brand-primary text-white font-sans text-[13px] font-bold rounded-xl shadow-md transition-all active:scale-[0.985] flex items-center justify-center gap-1.5 cursor-pointer mt-2">
            <Sparkles :size="14" />
            <span>立即消耗 {{ fourPillarsBasePointsCost }} 积分推演命盘</span>
          </button>
        </div>
      </div>
    </div>

    <div v-else-if="viewState === 'waiting'" class="py-16 text-center space-y-6">
      <div class="relative w-20 h-20 mx-auto flex items-center justify-center">
        <Loader2 class="w-16 h-16 text-brand-primary animate-spin" />
        <Sparkles class="absolute text-brand-primary" :size="20" />
      </div>
      <div class="space-y-1">
        <h3 class="font-serif text-[17px] font-bold text-brand-ink-strong">五行命理盘局测算中</h3>
        <p class="font-sans text-[11px] text-brand-secondary">AI 正在根据真太阳时和六十甲子精排八字神煞，请稍候...</p>
      </div>
    </div>

    <div v-else-if="viewState === 'error'" class="py-12 text-center space-y-4">
      <h3 class="text-sm font-bold text-red-600">推演未成功</h3>
      <p class="text-xs text-brand-secondary">{{ errorMessage }}</p>
      <button @click="resetToInput" class="px-5 py-2.5 bg-brand-primary text-white rounded-xl text-xs font-bold">返回修改</button>
    </div>

    <div v-else-if="viewState === 'result' && currentReview" class="space-y-4">
      <div class="bg-white rounded-xl p-4 border border-gray-100 shadow-sm flex items-center justify-between">
        <div>
          <h3 class="font-serif font-bold text-brand-ink-strong text-base">盘主: {{ profileName || '生辰盘主' }}</h3>
          <p class="font-sans text-[11px] text-brand-secondary mt-1">性别：{{ gender === 'male' ? '男命（乾造）' : '女命（坤造）' }} · 生日：{{ birthDate }} {{ birthTime }}</p>
        </div>
        <div class="text-center bg-brand-primary/10 text-brand-primary px-3.5 py-1.5 rounded-full shrink-0">
          <span class="text-xs font-bold">综合评分</span>
          <span class="block text-2xl font-black font-serif leading-none mt-1">{{ reviewScore }}</span>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-2 bg-white border border-gray-150 p-1 rounded-xl">
        <button @click="activeBranch = 'chart'" class="py-2.5 rounded-lg text-[11px] font-bold transition-all" :class="activeBranch === 'chart' ? 'bg-brand-primary text-white' : 'text-brand-secondary'">命盘分析</button>
        <button @click="activeBranch = 'luck'" class="py-2.5 rounded-lg text-[11px] font-bold transition-all" :class="activeBranch === 'luck' ? 'bg-brand-primary text-white' : 'text-brand-secondary'">运势分析</button>
      </div>

      <div v-if="activeBranch === 'chart'" class="space-y-4">
        <!-- Natal Chart Display Table -->
        <FourPillarsNatalTable :chart-display="currentReview.chart_display" />

        <div class="bg-white rounded-xl border border-gray-100 p-4.5 shadow-sm space-y-2">
          <h4 class="font-serif text-[14px] font-bold text-brand-primary-strong">综合评述</h4>
          <p class="font-serif text-[15px] font-bold text-brand-ink-strong leading-snug">{{ currentReview.summary?.title }}</p>
          <p class="font-sans text-[12.5px] leading-relaxed text-brand-secondary whitespace-pre-wrap">{{ currentReview.summary?.overview || currentReview.summary?.comprehensive_text }}</p>
        </div>

        <!-- 12 Aspects grid -->
        <div class="bg-white rounded-xl p-4 border border-gray-100 shadow-sm space-y-3">
          <h4 class="font-serif text-[13px] font-bold text-brand-secondary">十二大专项分析</h4>
          <div class="grid grid-cols-3 gap-1.5">
            <button
              v-for="(aspect, idx) in reviewAspects"
              :key="aspect.aspect_key"
              @click="handleUnlockAspect(aspect, idx)"
              class="h-[54px] rounded-lg border px-1.5 flex flex-col items-center justify-center gap-1 transition-all"
              :class="idx === activeAspect ? 'bg-brand-primary/10 text-brand-primary border-brand-primary' : 'bg-brand-paper/50 border-gray-100 text-brand-secondary'"
            >
              <span class="font-sans text-[11px] font-bold truncate">{{ aspect.short_title || aspect.title }}</span>
              <span class="text-[9px]">{{ aspect.is_unlocked ? `${aspect.score || ''}分` : '锁' }}</span>
            </button>
          </div>

          <div v-if="selectedAspect" class="mt-2.5 p-3 rounded-lg bg-brand-paper/40 border border-gray-100">
            <div class="flex justify-between items-center pb-2 border-b border-gray-100">
              <span class="font-serif text-[13.5px] font-bold text-brand-ink-strong">{{ selectedAspect.short_title || selectedAspect.title }}</span>
              <span class="text-xs font-bold text-brand-primary">{{ selectedAspect.is_unlocked ? `${selectedAspect.score}分` : '未解锁' }}</span>
            </div>
            <p v-if="selectedAspect.is_unlocked" class="font-sans text-[12.5px] leading-relaxed mt-2 text-brand-secondary whitespace-pre-wrap">
              {{ selectedAspect.content }}
            </p>
            <div v-else class="py-4 text-center space-y-2">
              <p class="text-xs text-brand-secondary">支付 {{ fourPillarsAspectUnlockPointsCost }} 积分即可流式解锁此项运势</p>
              <button @click="handleUnlockAspect(selectedAspect, activeAspect)" class="px-5 py-2 bg-brand-primary text-white text-xs font-bold rounded-lg flex items-center gap-1 mx-auto">
                <UnlockKeyhole :size="12" />
                <span>立即解锁</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="space-y-4">
        <!-- Luck Cycles Selectors -->
        <div class="bg-white rounded-xl p-4 border border-gray-100 shadow-sm space-y-4">
          <div class="flex justify-between items-center">
            <h3 class="font-serif text-[14px] font-bold text-brand-primary-strong">流年大运十神演变</h3>
            <span class="text-[10px] text-brand-secondary font-mono">选择大运与流年查看详情</span>
          </div>

          <div class="flex gap-2 overflow-x-auto pb-2">
            <button
              v-for="cycle in luckCycles"
              :key="cycle.cycle_key"
              @click="activeCycleKey = cycle.cycle_key; selectedLuckYear = null"
              class="px-3.5 py-2 rounded-lg border text-center font-sans text-xs font-bold shrink-0 transition-colors"
              :class="cycle.cycle_key === selectedLuckCycle?.cycle_key ? 'bg-brand-primary text-white border-brand-primary' : 'bg-brand-paper text-brand-secondary border-gray-100'"
            >
              <span class="block text-[10px]">{{ cycle.start_age }}岁 - {{ cycle.end_age }}岁</span>
              <span class="block mt-1 font-serif text-[13px] font-black">{{ cycle.display_ganzhi || cycle.ganzhi || '大运' }}</span>
            </button>
          </div>

          <!-- Years row select -->
          <div v-if="selectedLuckCycle" class="flex gap-2 overflow-x-auto pb-2 border-t border-gray-100 pt-2.5">
            <button
              v-for="year in selectedLuckCycle.year_items"
              :key="item => year.year"
              class="w-10 py-1.5 rounded-lg border text-center shrink-0 transition-colors"
              :class="year.year === selectedLuckYear ? 'bg-brand-primary text-white border-brand-primary' : 'bg-brand-paper text-brand-secondary border-transparent'"
              @click="selectedLuckYear = year.year"
            >
              <span class="block text-[8px] font-mono leading-none">{{ year.age }}岁</span>
              <span class="block font-serif text-[13px] font-black mt-1 leading-none">{{ year.ganzhi }}</span>
              <span class="block text-[7px] text-gray-400 mt-1 leading-none">{{ year.year }}</span>
            </button>
          </div>

          <!-- Dynamic Render results -->
          <div v-if="selectedLuckCycle" class="rounded-xl border border-gray-100 p-3 bg-brand-paper/20">
            <div class="flex justify-between items-center border-b border-gray-100 pb-2">
              <span class="font-serif text-[13.5px] font-black text-brand-ink-strong">大运 {{ selectedLuckCycle.display_ganzhi || selectedLuckCycle.ganzhi }} ({{ selectedLuckCycle.start_year }} - {{ selectedLuckCycle.end_year }})</span>
              <button
                v-if="selectedLuckCycle.render_status !== 'completed'"
                @click="handleGenerateCycle(selectedLuckCycle)"
                class="px-2.5 py-1.5 bg-brand-primary text-white text-[11px] font-bold rounded-lg border-none"
              >
                生成大运综评
              </button>
            </div>
            <p v-if="selectedLuckCycle.render_status === 'completed'" class="text-[12.5px] leading-relaxed text-brand-secondary mt-2.5 whitespace-pre-wrap">
              {{ selectedLuckCycle.render?.result?.verdict || selectedLuckCycle.render?.result?.title }}
            </p>
            <p v-else class="text-xs text-brand-secondary mt-2.5">点击上方按钮，生成大运十年气运总析及行动建议</p>
          </div>

          <!-- Dynamic Year Render results -->
          <div v-if="selectedLuckCycle && selectedLuckYearItem" class="rounded-xl border border-gray-100 p-3 bg-brand-paper/20">
            <div class="flex justify-between items-center border-b border-gray-100 pb-2">
              <span class="font-serif text-[13.5px] font-black text-brand-ink-strong">流年 {{ selectedLuckYearItem.year }}年 ({{ selectedLuckYearItem.ganzhi }})</span>
              <button
                v-if="selectedLuckYearItem.render_status !== 'completed'"
                @click="handleGenerateYear(selectedLuckCycle, selectedLuckYearItem)"
                class="px-2.5 py-1.5 bg-brand-primary text-white text-[11px] font-bold rounded-lg border-none"
              >
                生成流年精测
              </button>
            </div>
            <p v-if="selectedLuckYearItem.render_status === 'completed'" class="text-[12.5px] leading-relaxed text-brand-secondary mt-2.5 whitespace-pre-wrap">
              {{ selectedLuckYearItem.render?.result?.verdict || selectedLuckYearItem.render?.result?.title }}
            </p>
            <p v-else class="text-xs text-brand-secondary mt-2.5">点击生成该流年对财运、事业、健康及关系磁场触发点</p>
          </div>
        </div>
      </div>
    </div>
    <!-- Date/Time Wheel Picker Drawer -->
    <div v-if="showDatePickerDrawer" class="fixed inset-0 bg-black/40 z-[999] flex items-end transition-opacity" @click="showDatePickerDrawer = false">
      <div class="bg-white w-full max-w-md mx-auto rounded-t-3xl p-5 space-y-4 pb-8" @click.stop>
        <div class="flex justify-between items-center border-b border-gray-100 pb-3">
          <h3 class="font-serif text-sm font-bold text-brand-ink-strong">生辰时间滑动选择轮</h3>
          <button @click="showDatePickerDrawer = false" class="text-gray-400 hover:text-gray-600"><X :size="18" /></button>
        </div>

        <div class="flex gap-1 h-44 relative bg-gray-50 rounded-xl overflow-hidden border border-gray-200">
          <!-- Overlay marker -->
          <div class="absolute left-0 right-0 top-[72px] h-9 border-y border-brand-primary/20 bg-brand-primary/5 pointer-events-none"></div>

          <!-- Year -->
          <div class="flex-1 overflow-y-auto h-full text-center snap-y snap-mandatory no-scrollbar py-[72px]">
            <div v-for="y in yearsArray" :key="y" :class="['py-2 text-[12px] snap-center cursor-pointer font-semibold', yearVal === y ? 'text-brand-primary text-[14px] font-black' : 'text-zinc-400']" @click="yearVal = y; syncToString()">
              {{ y }}年
            </div>
          </div>
          <!-- Month -->
          <div class="flex-1 overflow-y-auto h-full text-center snap-y snap-mandatory no-scrollbar py-[72px]">
            <div v-for="m in monthsArray" :key="m" :class="['py-2 text-[12px] snap-center cursor-pointer font-semibold', monthVal === m ? 'text-brand-primary text-[14px] font-black' : 'text-zinc-400']" @click="monthVal = m; syncToString()">
              {{ m }}月
            </div>
          </div>
          <!-- Day -->
          <div class="flex-1 overflow-y-auto h-full text-center snap-y snap-mandatory no-scrollbar py-[72px]">
            <div v-for="d in daysArray" :key="d" :class="['py-2 text-[12px] snap-center cursor-pointer font-semibold', dayVal === d ? 'text-brand-primary text-[14px] font-black' : 'text-zinc-400']" @click="dayVal = d; syncToString()">
              {{ d }}日
            </div>
          </div>
          <!-- Hour -->
          <div class="flex-1 overflow-y-auto h-full text-center snap-y snap-mandatory no-scrollbar py-[72px]">
            <div v-for="h in hoursArray" :key="h" :class="['py-2 text-[12px] snap-center cursor-pointer font-semibold', hourVal === h ? 'text-brand-primary text-[14px] font-black' : 'text-zinc-400']" @click="hourVal = h; syncToString()">
              {{ h }}时
            </div>
          </div>
          <!-- Minute -->
          <div class="flex-1 overflow-y-auto h-full text-center snap-y snap-mandatory no-scrollbar py-[72px]">
            <div v-for="m in minutesArray" :key="m" :class="['py-2 text-[12px] snap-center cursor-pointer font-semibold', minuteVal === m ? 'text-brand-primary text-[14px] font-black' : 'text-zinc-400']" @click="minuteVal = m; syncToString()">
              {{ m }}分
            </div>
          </div>
        </div>

        <button @click="showDatePickerDrawer = false" class="w-full py-3 bg-brand-primary text-white rounded-xl text-xs font-bold shadow-md cursor-pointer">
          确定生辰
        </button>
      </div>
    </div>

    <!-- Location Picker Drawer (Bottom Sheet) -->
    <div v-if="showLocationPickerDrawer" class="fixed inset-0 bg-black/40 z-[999] flex items-end transition-opacity" @click="showLocationPickerDrawer = false">
      <div class="bg-white w-full max-w-md mx-auto rounded-t-3xl p-5 space-y-4 pb-8 h-[75vh] flex flex-col" @click.stop>
        <div class="flex justify-between items-center border-b border-gray-100 pb-3 shrink-0">
          <div>
            <h3 class="font-serif text-sm font-bold text-brand-ink-strong">出生城市定位</h3>
            <p class="text-[10px] text-brand-secondary mt-0.5">选择具体市/区以校准真太阳时(True Solar Time)</p>
          </div>
          <button @click="showLocationPickerDrawer = false" class="text-gray-400 hover:text-gray-600"><X :size="18" /></button>
        </div>

        <!-- Search Bar -->
        <div class="relative shrink-0">
          <Search :size="14" class="absolute left-3.5 top-1/2 -translate-y-1/2 text-brand-secondary" />
          <input v-model="locationSearchQuery" placeholder="输入城市、区县进行精确搜索..." class="w-full bg-zinc-50 text-[12px] pl-9 pr-8 py-2.5 rounded-xl border border-gray-100 outline-none focus:bg-white focus:border-brand-primary" />
          <button v-if="locationSearchQuery" @click="locationSearchQuery = ''" class="absolute right-3.5 top-1/2 -translate-y-1/2 text-zinc-400"><X :size="14" /></button>
        </div>

        <!-- Locations list -->
        <div class="flex-1 overflow-y-auto no-scrollbar space-y-1 pr-1">
          <div v-for="loc in filteredLocations" :key="loc.id" :class="['p-3 rounded-xl flex items-center justify-between cursor-pointer transition-colors border', selectedLoc.id === loc.id ? 'bg-brand-primary/5 border-brand-primary/20' : 'hover:bg-zinc-50 border-transparent']" @click="selectLocation(loc)">
            <div>
              <span class="text-[12.5px] font-bold text-brand-ink-strong block">{{ loc.name }}</span>
              <span class="text-[10px] text-brand-secondary block mt-0.5">经度：{{ loc.longitude }}° E · 纬度：{{ loc.latitude }}° N · 时区：{{ loc.timezone }}</span>
            </div>
            <Check v-if="selectedLoc.id === loc.id" :size="16" class="text-brand-primary" />
          </div>
          <div v-if="!filteredLocations.length" class="text-center py-12 text-xs text-brand-secondary">
            没有搜索到该出生地城市，请输入主要市/区名称
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.picker-wheel-item {
  scroll-snap-align: center;
}
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
