<script setup lang="ts">
import { computed, ref } from 'vue';
import {
  AlertCircle,
  ArrowLeft,
  BookOpen,
  Check,
  Clock,
  Compass,
  Hash,
  MessageSquare,
  PenTool,
  RefreshCw,
  Sparkles,
} from 'lucide-vue-next';

const emit = defineEmits<{
  (e: 'back-to-home'): void;
  (e: 'navigate-to-tab', tab: string, params?: Record<string, string>): void;
}>();

type CastingMethod = 'number' | 'text' | 'time';
type ViewState = 'input' | 'animating' | 'result';
type LineValue = 0 | 1;

type Trigram = {
  number: number;
  name: string;
  nature: string;
  symbol: string;
  lines: [LineValue, LineValue, LineValue];
  element: string;
};

type HexagramResult = {
  upper: Trigram;
  lower: Trigram;
  lines: LineValue[];
  name: string;
};

const viewState = ref<ViewState>('input');
const castingMethod = ref<CastingMethod>('number');
const toast = ref<string | null>(null);
const inputNum1 = ref('');
const inputNum2 = ref('');
const inputText1 = ref('');
const inputText2 = ref('');
const selectHourZhi = ref('辰');
const questionAspect = ref('综合');
const animProgress = ref(0);
const animStatusText = ref('正在感应太极气场...');

const originalHexagram = ref<HexagramResult | null>(null);
const mutualHexagram = ref<HexagramResult | null>(null);
const transformedHexagram = ref<HexagramResult | null>(null);
const movingLineNum = ref(1);
const subjectTrigram = ref<Trigram | null>(null);
const objectTrigram = ref<Trigram | null>(null);
const relationshipType = ref('');
const relationshipTone = ref('');
const relationshipInterpretation = ref('');

const hourZhis = [
  { zhi: '子', time: '23:00-01:00', index: 1 },
  { zhi: '丑', time: '01:00-03:00', index: 2 },
  { zhi: '寅', time: '03:00-05:00', index: 3 },
  { zhi: '卯', time: '05:00-07:00', index: 4 },
  { zhi: '辰', time: '07:00-09:00', index: 5 },
  { zhi: '巳', time: '09:00-11:00', index: 6 },
  { zhi: '午', time: '11:00-13:00', index: 7 },
  { zhi: '未', time: '13:00-15:00', index: 8 },
  { zhi: '申', time: '15:00-17:00', index: 9 },
  { zhi: '酉', time: '17:00-19:00', index: 10 },
  { zhi: '戌', time: '19:00-21:00', index: 11 },
  { zhi: '亥', time: '21:00-23:00', index: 12 },
];

const questionAspects = ['综合', '财运', '感情', '事业', '出行', '寻物'];

const trigrams: Record<number, Trigram> = {
  1: { number: 1, name: '乾', nature: '天', symbol: '☰', lines: [1, 1, 1], element: '金' },
  2: { number: 2, name: '兑', nature: '泽', symbol: '☱', lines: [1, 1, 0], element: '金' },
  3: { number: 3, name: '离', nature: '火', symbol: '☲', lines: [1, 0, 1], element: '火' },
  4: { number: 4, name: '震', nature: '雷', symbol: '☳', lines: [1, 0, 0], element: '木' },
  5: { number: 5, name: '巽', nature: '风', symbol: '☴', lines: [0, 1, 1], element: '木' },
  6: { number: 6, name: '坎', nature: '水', symbol: '☵', lines: [0, 1, 0], element: '水' },
  7: { number: 7, name: '艮', nature: '山', symbol: '☶', lines: [0, 0, 1], element: '土' },
  8: { number: 8, name: '坤', nature: '地', symbol: '☷', lines: [0, 0, 0], element: '土' },
};

const hexagramNames: Record<string, string> = {
  '1-1': '乾为天', '1-2': '天泽履', '1-3': '天火同人', '1-4': '天雷无妄', '1-5': '天风姤', '1-6': '天水讼', '1-7': '天山遁', '1-8': '天地否',
  '2-1': '泽天夬', '2-2': '兑为泽', '2-3': '泽火革', '2-4': '泽雷随', '2-5': '泽风大过', '2-6': '泽水困', '2-7': '泽山咸', '2-8': '泽地萃',
  '3-1': '火天大有', '3-2': '火泽睽', '3-3': '离为火', '3-4': '火雷噬嗑', '3-5': '火风鼎', '3-6': '火水未济', '3-7': '火山旅', '3-8': '火地晋',
  '4-1': '雷天大壮', '4-2': '雷泽归妹', '4-3': '雷火丰', '4-4': '震为雷', '4-5': '雷风恒', '4-6': '雷水解', '4-7': '雷山小过', '4-8': '雷地豫',
  '5-1': '风天小畜', '5-2': '风泽中孚', '5-3': '风火家人', '5-4': '风雷益', '5-5': '巽为风', '5-6': '风水涣', '5-7': '风山渐', '5-8': '风地观',
  '6-1': '水天需', '6-2': '水泽节', '6-3': '水火既济', '6-4': '水雷屯', '6-5': '水风井', '6-6': '坎为水', '6-7': '水山蹇', '6-8': '水地比',
  '7-1': '山天大畜', '7-2': '山泽损', '7-3': '山火贲', '7-4': '山雷颐', '7-5': '山风蛊', '7-6': '山水蒙', '7-7': '艮为山', '7-8': '山地剥',
  '8-1': '地天泰', '8-2': '地泽临', '8-3': '地火明夷', '8-4': '地雷复', '8-5': '地风升', '8-6': '地水师', '8-7': '地山谦', '8-8': '坤为地',
};

const methodCards = [
  { key: 'number' as const, title: '报数起卦', desc: '输入两组心中吉数', icon: Hash },
  { key: 'text' as const, title: '汉字起卦', desc: '以两字笔画取象', icon: PenTool },
  { key: 'time' as const, title: '时间起卦', desc: '以当前时机成卦', icon: Clock },
];

const resultAdvice = computed(() => {
  if (!relationshipType.value) return '';
  if (relationshipType.value === '用生体' || relationshipType.value === '体用比和') {
    return '当前气机较顺，适合顺势推进。可以先做小范围验证，再逐步放大行动。';
  }
  if (relationshipType.value === '体克用') {
    return '此象重在主动掌控。事情并非无阻，但适合明确目标、拆解步骤、稳步推进。';
  }
  if (relationshipType.value === '体生用') {
    return '此象有付出之意。宜先评估成本和精力，不要因投入过多而忽略自己的节奏。';
  }
  return '外部压力较强，宜先守后动。把问题拆小，等条件更清晰时再做关键决定。';
});

function showToast(message: string): void {
  toast.value = message;
  window.setTimeout(() => {
    toast.value = null;
  }, 2400);
}

function trigramByLines(lines: LineValue[]): Trigram {
  return Object.values(trigrams).find((item) => item.lines.every((line, index) => line === lines[index])) || trigrams[1];
}

function hexagramName(upper: Trigram, lower: Trigram): string {
  return hexagramNames[`${upper.number}-${lower.number}`] || `${upper.name}${lower.name}卦`;
}

function numberToTrigram(value: number): Trigram {
  const key = value % 8 || 8;
  return trigrams[key];
}

function safePositiveInteger(value: string): number | null {
  const parsed = Number.parseInt(value, 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : null;
}

function charScore(value: string): number {
  const char = value.trim().charAt(0);
  if (!char) return 0;
  const common: Record<string, number> = {
    梅: 11,
    花: 7,
    易: 8,
    数: 13,
    财: 10,
    情: 11,
    事: 8,
    问: 6,
    家: 10,
    人: 2,
    心: 4,
    行: 6,
    吉: 6,
    凶: 4,
    成: 6,
    败: 8,
  };
  return common[char] || (char.charCodeAt(0) % 13) + 3;
}

function currentHourBranchIndex(): number {
  const hour = new Date().getHours();
  const branch = Math.floor((hour + 1) / 2) % 12;
  return branch + 1;
}

function buildHexagram(upper: Trigram, lower: Trigram): HexagramResult {
  const lines = [...lower.lines, ...upper.lines];
  return {
    upper,
    lower,
    lines,
    name: hexagramName(upper, lower),
  };
}

function calculateMutual(lines: LineValue[]): HexagramResult {
  const lower = trigramByLines([lines[1], lines[2], lines[3]]);
  const upper = trigramByLines([lines[2], lines[3], lines[4]]);
  return buildHexagram(upper, lower);
}

function calculateTransformed(lines: LineValue[], movingLine: number): HexagramResult {
  const transformed = [...lines] as LineValue[];
  const index = movingLine - 1;
  transformed[index] = transformed[index] === 1 ? 0 : 1;
  const lower = trigramByLines([transformed[0], transformed[1], transformed[2]]);
  const upper = trigramByLines([transformed[3], transformed[4], transformed[5]]);
  return buildHexagram(upper, lower);
}

function calculateRelationship(subject: string, object: string): void {
  if (subject === object) {
    relationshipType.value = '体用比和';
    relationshipTone.value = 'text-emerald-700 bg-emerald-50 border-emerald-100';
    relationshipInterpretation.value = '体卦与用卦同气相求，内外同频，适合稳健推进。';
    return;
  }
  const generates: Record<string, string> = { 水: '木', 木: '火', 火: '土', 土: '金', 金: '水' };
  const controls: Record<string, string> = { 金: '木', 木: '土', 土: '水', 水: '火', 火: '金' };
  if (generates[object] === subject) {
    relationshipType.value = '用生体';
    relationshipTone.value = 'text-brand-primary bg-indigo-50 border-indigo-100';
    relationshipInterpretation.value = '外部条件生助自身，事情容易得到资源、时机或他人帮助。';
    return;
  }
  if (generates[subject] === object) {
    relationshipType.value = '体生用';
    relationshipTone.value = 'text-amber-700 bg-amber-50 border-amber-100';
    relationshipInterpretation.value = '自身生助事体，代表投入与消耗增加，需要守住节奏。';
    return;
  }
  if (controls[subject] === object) {
    relationshipType.value = '体克用';
    relationshipTone.value = 'text-blue-700 bg-blue-50 border-blue-100';
    relationshipInterpretation.value = '自身能制约事体，有掌控空间，但需要持续推进。';
    return;
  }
  relationshipType.value = '用克体';
  relationshipTone.value = 'text-rose-700 bg-rose-50 border-rose-100';
  relationshipInterpretation.value = '事体对自身形成压力，当前宜谨慎观察，避免急进。';
}

function resolveInputNumbers(): { first: number; second: number; hourIndex: number } | null {
  const selectedHour = hourZhis.find((item) => item.zhi === selectHourZhi.value)?.index || currentHourBranchIndex();
  if (castingMethod.value === 'number') {
    const first = safePositiveInteger(inputNum1.value);
    const second = safePositiveInteger(inputNum2.value);
    if (!first || !second) {
      showToast('请输入两组大于零的正整数。');
      return null;
    }
    return { first, second, hourIndex: selectedHour };
  }
  if (castingMethod.value === 'text') {
    const first = charScore(inputText1.value);
    const second = charScore(inputText2.value);
    if (!first || !second) {
      showToast('请输入两个用于起卦的汉字。');
      return null;
    }
    return { first, second, hourIndex: selectedHour };
  }
  const now = new Date();
  return {
    first: now.getFullYear() + now.getMonth() + 1 + now.getDate(),
    second: now.getHours() + now.getMinutes() + now.getDate(),
    hourIndex: currentHourBranchIndex(),
  };
}

function performCasting(): void {
  const input = resolveInputNumbers();
  if (!input) return;
  const upper = numberToTrigram(input.first);
  const lower = numberToTrigram(input.second);
  const movingLine = (input.first + input.second + input.hourIndex) % 6 || 6;
  const original = buildHexagram(upper, lower);
  originalHexagram.value = original;
  mutualHexagram.value = calculateMutual(original.lines);
  transformedHexagram.value = calculateTransformed(original.lines, movingLine);
  movingLineNum.value = movingLine;

  if (movingLine <= 3) {
    objectTrigram.value = lower;
    subjectTrigram.value = upper;
  } else {
    objectTrigram.value = upper;
    subjectTrigram.value = lower;
  }
  calculateRelationship(subjectTrigram.value.element, objectTrigram.value.element);
  runCastingAnimation();
}

function runCastingAnimation(): void {
  viewState.value = 'animating';
  animProgress.value = 0;
  animStatusText.value = '正在感应太极八卦气场...';
  const timer = window.setInterval(() => {
    animProgress.value = Math.min(100, animProgress.value + 12);
    if (animProgress.value > 75) {
      animStatusText.value = '爻象定局，显化体用生克...';
    } else if (animProgress.value > 45) {
      animStatusText.value = '九宫流转，推演本互变卦...';
    } else if (animProgress.value > 20) {
      animStatusText.value = '灵机初动，取数成象...';
    }
    if (animProgress.value >= 100) {
      window.clearInterval(timer);
      window.setTimeout(() => {
        viewState.value = 'result';
      }, 350);
    }
  }, 160);
}

function resetCasting(): void {
  viewState.value = 'input';
  animProgress.value = 0;
}
</script>

<template>
  <div class="min-h-screen bg-brand-paper pb-28">
    <transition name="fade-slide">
      <div
        v-if="toast"
        class="fixed top-4 left-1/2 -translate-x-1/2 z-50 bg-brand-ink-strong text-white px-4 py-2.5 rounded-full font-sans text-[13px] shadow-lg font-medium flex items-center gap-2 max-w-[90%] whitespace-nowrap"
      >
        <AlertCircle :size="15" class="text-brand-accent shrink-0" />
        <span>{{ toast }}</span>
      </div>
    </transition>

    <header class="sticky top-0 z-20 bg-brand-paper/95 backdrop-blur border-b border-white/80">
      <div class="max-w-md mx-auto px-margin-mobile py-3 flex items-center justify-between">
        <button
          class="h-9 rounded-lg bg-white border border-gray-100 px-3 text-brand-secondary font-sans text-[12px] font-bold flex items-center justify-center gap-1.5 shadow-sm cursor-pointer"
          @click="viewState === 'result' ? resetCasting() : emit('back-to-home')"
        >
          <ArrowLeft :size="14" class="text-brand-ink-strong" />
          <span>{{ viewState === 'result' ? '重新起卦' : '返回首页' }}</span>
        </button>
        <div class="text-center">
          <h1 class="font-serif text-[17.5px] font-black text-brand-ink-strong leading-none">梅花易数精研</h1>
          <p class="font-sans text-[10.5px] text-brand-secondary mt-1">前端原型 · 后续接入正式业务</p>
        </div>
        <button
          class="w-9 h-9 rounded-lg bg-white border border-gray-100 flex items-center justify-center shadow-sm cursor-pointer"
          @click="resetCasting"
        >
          <RefreshCw :size="16" class="text-brand-secondary" />
        </button>
      </div>
    </header>

    <main class="max-w-md mx-auto px-margin-mobile pt-4">
      <section v-if="viewState === 'input'" class="space-y-4">
        <section class="bg-white rounded-2xl p-4.5 border border-gray-100 shadow-sm relative overflow-hidden text-left font-sans">
          <div class="absolute -right-3 -top-3 w-16 h-16 bg-brand-primary/5 rounded-full"></div>
          <div class="relative flex items-center gap-2">
            <span class="relative flex h-2.5 w-2.5 shrink-0">
              <span class="absolute inline-flex h-full w-full animate-ping rounded-full bg-brand-primary/50"></span>
              <span class="relative inline-flex h-2.5 w-2.5 rounded-full bg-brand-primary"></span>
            </span>
            <h2 class="font-serif text-[16px] font-black text-brand-gold-fixed leading-snug">梅花易数起卦测算</h2>
          </div>
          <p class="font-sans text-[11px] text-brand-secondary leading-relaxed mt-2">
            先吸收 AI Studio 的页面设计作为原型；正式计费、历史记录与报告生成会在后续业务开发中接入。
          </p>
        </section>

        <section class="bg-white rounded-2xl border border-gray-100 p-4 shadow-sm space-y-4">
          <div class="grid grid-cols-3 gap-2">
            <button
              v-for="method in methodCards"
              :key="method.key"
              type="button"
              class="rounded-xl border p-2.5 text-center transition-all"
              :class="castingMethod === method.key ? 'border-brand-primary bg-brand-primary/5 text-brand-primary' : 'border-gray-100 bg-brand-paper/60 text-brand-secondary'"
              @click="castingMethod = method.key"
            >
              <component :is="method.icon" :size="16" class="mx-auto mb-1" />
              <span class="block font-serif text-[12px] font-black">{{ method.title }}</span>
              <span class="block font-sans text-[9px] mt-0.5">{{ method.desc }}</span>
            </button>
          </div>

          <div v-if="castingMethod === 'number'" class="grid grid-cols-2 gap-3">
            <label class="space-y-1">
              <span class="font-sans text-[11px] font-bold text-brand-secondary">第一组数</span>
              <input v-model="inputNum1" inputmode="numeric" placeholder="如 18" class="w-full h-11 rounded-xl bg-brand-paper border border-transparent px-3 text-[14px] font-bold outline-none focus:border-brand-primary" />
            </label>
            <label class="space-y-1">
              <span class="font-sans text-[11px] font-bold text-brand-secondary">第二组数</span>
              <input v-model="inputNum2" inputmode="numeric" placeholder="如 27" class="w-full h-11 rounded-xl bg-brand-paper border border-transparent px-3 text-[14px] font-bold outline-none focus:border-brand-primary" />
            </label>
          </div>

          <div v-else-if="castingMethod === 'text'" class="grid grid-cols-2 gap-3">
            <label class="space-y-1">
              <span class="font-sans text-[11px] font-bold text-brand-secondary">第一字</span>
              <input v-model="inputText1" maxlength="2" placeholder="梅" class="w-full h-11 rounded-xl bg-brand-paper border border-transparent px-3 text-[14px] font-bold outline-none focus:border-brand-primary" />
            </label>
            <label class="space-y-1">
              <span class="font-sans text-[11px] font-bold text-brand-secondary">第二字</span>
              <input v-model="inputText2" maxlength="2" placeholder="花" class="w-full h-11 rounded-xl bg-brand-paper border border-transparent px-3 text-[14px] font-bold outline-none focus:border-brand-primary" />
            </label>
          </div>

          <div v-else class="rounded-xl bg-brand-primary/5 border border-brand-primary/15 px-3 py-3 text-left">
            <p class="font-serif text-[13px] font-black text-brand-ink-strong">以当前时间自动起卦</p>
            <p class="font-sans text-[11px] text-brand-secondary leading-relaxed mt-1">点击下方按钮后，将以当前年月日时生成本卦、互卦与变卦。</p>
          </div>

          <div class="space-y-2">
            <div class="flex items-center justify-between gap-3">
              <span class="font-sans text-[11px] font-bold text-brand-secondary">时辰</span>
              <div class="flex-1 overflow-x-auto no-scrollbar">
                <div class="flex gap-1.5 justify-end min-w-max">
                  <button
                    v-for="hour in hourZhis"
                    :key="hour.zhi"
                    type="button"
                    class="h-8 px-2.5 rounded-lg text-[11px] font-bold border"
                    :class="selectHourZhi === hour.zhi ? 'bg-brand-primary text-white border-brand-primary' : 'bg-brand-paper text-brand-secondary border-transparent'"
                    @click="selectHourZhi = hour.zhi"
                  >
                    {{ hour.zhi }}
                  </button>
                </div>
              </div>
            </div>
            <div class="flex items-center justify-between gap-3">
              <span class="font-sans text-[11px] font-bold text-brand-secondary">主题</span>
              <div class="flex-1 overflow-x-auto no-scrollbar">
                <div class="flex gap-1.5 justify-end min-w-max">
                  <button
                    v-for="aspect in questionAspects"
                    :key="aspect"
                    type="button"
                    class="h-8 px-2.5 rounded-lg text-[11px] font-bold border"
                    :class="questionAspect === aspect ? 'bg-brand-primary text-white border-brand-primary' : 'bg-brand-paper text-brand-secondary border-transparent'"
                    @click="questionAspect = aspect"
                  >
                    {{ aspect }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>

        <button
          class="w-full h-12 rounded-xl bg-brand-primary hover:bg-brand-primary-strong text-white font-sans text-[13px] font-bold shadow-md transition-all active:scale-[0.985] flex items-center justify-center gap-1.5"
          @click="performCasting"
        >
          <Sparkles :size="15" fill="currentColor" />
          <span>进入深度梅花推演</span>
        </button>
      </section>

      <section v-else-if="viewState === 'animating'" class="py-14 flex flex-col justify-center min-h-[65vh]">
        <div class="bg-white rounded-2xl p-6 border border-gray-150/75 shadow-sm space-y-6 text-center">
          <div class="relative w-28 h-28 mx-auto flex items-center justify-center select-none">
            <div class="absolute inset-0 bg-brand-primary/5 rounded-full blur-md animate-pulse"></div>
            <div class="absolute inset-3 border border-brand-primary/20 rounded-full animate-spin [animation-duration:8s]"></div>
            <Compass :size="42" class="text-brand-primary meihua-sway" />
          </div>
          <div>
            <p class="font-serif text-[17px] font-black text-brand-ink-strong">一念起卦中</p>
            <p class="font-sans text-[12px] text-brand-secondary mt-2">{{ animStatusText }}</p>
          </div>
          <div class="h-2 rounded-full bg-brand-paper overflow-hidden">
            <div class="h-full bg-brand-primary transition-all duration-200" :style="{ width: `${animProgress}%` }"></div>
          </div>
        </div>
      </section>

      <section v-else class="space-y-4">
        <section class="bg-white rounded-2xl p-4 border border-gray-100 shadow-sm">
          <div class="flex items-center justify-between gap-3 mb-3">
            <div>
              <p class="font-sans text-[10px] font-black tracking-wide text-brand-secondary">MEIHUA RESULT</p>
              <h2 class="font-serif text-[17px] font-black text-brand-ink-strong mt-0.5">梅花易数定盘报告</h2>
            </div>
            <div class="rounded-xl bg-brand-primary/10 text-brand-primary p-2.5">
              <BookOpen :size="20" />
            </div>
          </div>

          <div class="grid grid-cols-3 gap-2">
            <div
              v-for="item in [
                { label: '本卦', value: originalHexagram },
                { label: '互卦', value: mutualHexagram },
                { label: '变卦', value: transformedHexagram },
              ]"
              :key="item.label"
              class="rounded-xl bg-brand-paper/70 border border-gray-100 px-2 py-3 text-center"
            >
              <span class="font-sans text-[10px] font-bold text-brand-secondary">{{ item.label }}</span>
              <span class="block font-serif text-[22px] font-black text-brand-primary leading-none mt-1">{{ item.value?.upper.symbol }}{{ item.value?.lower.symbol }}</span>
              <span class="block font-serif text-[12px] font-black text-brand-ink-strong mt-1">{{ item.value?.name }}</span>
            </div>
          </div>
        </section>

        <section class="bg-white rounded-2xl p-4 border border-gray-100 shadow-sm space-y-3">
          <div class="flex items-center gap-2">
            <MessageSquare :size="16" class="text-brand-primary" />
            <h3 class="font-serif text-[15px] font-black text-brand-ink-strong">体用生克</h3>
          </div>
          <div class="grid grid-cols-2 gap-2">
            <div class="rounded-xl bg-brand-paper/70 border border-gray-100 p-3">
              <span class="font-sans text-[10px] font-bold text-brand-secondary">体卦</span>
              <p class="font-serif text-[16px] font-black text-brand-ink-strong mt-1">{{ subjectTrigram?.name }}为{{ subjectTrigram?.nature }} · {{ subjectTrigram?.element }}</p>
            </div>
            <div class="rounded-xl bg-brand-paper/70 border border-gray-100 p-3">
              <span class="font-sans text-[10px] font-bold text-brand-secondary">用卦</span>
              <p class="font-serif text-[16px] font-black text-brand-ink-strong mt-1">{{ objectTrigram?.name }}为{{ objectTrigram?.nature }} · {{ objectTrigram?.element }}</p>
            </div>
          </div>
          <div class="rounded-xl border p-3" :class="relationshipTone">
            <div class="flex items-center justify-between gap-3">
              <span class="font-serif text-[16px] font-black">{{ relationshipType }}</span>
              <span class="font-sans text-[11px] font-black">动爻 {{ movingLineNum }} 爻</span>
            </div>
            <p class="font-sans text-[12px] leading-relaxed mt-2">{{ relationshipInterpretation }}</p>
          </div>
        </section>

        <section class="bg-white rounded-2xl p-4 border border-gray-100 shadow-sm">
          <div class="flex items-center gap-2 mb-2">
            <Check :size="16" class="text-brand-primary" />
            <h3 class="font-serif text-[15px] font-black text-brand-ink-strong">行动锦囊</h3>
          </div>
          <p class="font-sans text-[12px] text-brand-secondary leading-relaxed">{{ resultAdvice }}</p>
          <p class="font-sans text-[10px] text-brand-secondary/80 leading-relaxed mt-3">
            当前为前端原型结果，仅用于产品设计体验；后续会接入正式知识库、计费、记录与 AI 解读链路。
          </p>
        </section>
      </section>
    </main>
  </div>
</template>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translate(-50%, -20px);
}
</style>
