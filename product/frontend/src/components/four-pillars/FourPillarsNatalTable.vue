<script setup lang="ts">
import { computed, ref } from 'vue';
import { CalendarDays, ChevronDown, ChevronUp, Info, UserRound, X } from 'lucide-vue-next';
import type { FourPillarsChartDisplay, FourPillarsDisplayPillar, FourPillarsPillarKey, FourPillarsShenShaDetail } from '../../types/api';

const props = defineProps<{
  chartDisplay: FourPillarsChartDisplay | null;
  elementCounts?: Array<{ element: string; value: number }>;
  strengthLabel?: string;
  favorableElements?: string[];
  unfavorableElements?: string[];
}>();

const pillarKeys: FourPillarsPillarKey[] = ['year', 'month', 'day', 'hour'];
const MAX_SHEN_SHA_ROWS = 3;
const LIFE_STAGE_NAMES = new Set(['长生', '沐浴', '冠带', '临官', '帝旺', '衰', '病', '死', '墓', '绝', '胎', '养']);

type ShenShaCellItem = {
  name: string;
  meaning: string;
  category: string;
};

const shenShaExpanded = ref(false);
const infoModalOpen = ref(false);
const SHEN_SHA_NAME_ORDER: Record<string, number> = {
  天乙贵人: 10,
  太极贵人: 20,
  福星贵人: 30,
  天德贵人: 40,
  月德贵人: 41,
  天德合: 42,
  月德合: 43,
  文昌: 50,
  国印贵人: 51,
  金舆: 60,
  禄神: 61,
  天喜: 70,
  红鸾: 71,
  童子: 72,
  天医: 80,
  华盖: 90,
  将星: 100,
  桃花: 110,
  驿马: 120,
  孤辰: 130,
  寡宿: 131,
  魁罡: 140,
  天赦: 150,
  羊刃: 200,
  飞刃: 201,
  亡神: 210,
  劫煞: 211,
  灾煞: 212,
  元辰: 213,
  勾煞: 214,
  绞煞: 215,
  五鬼: 216,
  阴阳差错: 220,
  长生: 800,
  沐浴: 801,
  冠带: 802,
  临官: 803,
  帝旺: 804,
  衰: 805,
  病: 806,
  死: 807,
  墓: 808,
  绝: 809,
  胎: 810,
  养: 811,
  空亡: 900,
  墓库: 910,
};
const SHEN_SHA_CATEGORY_ORDER: Record<string, number> = {
  support: 10,
  talent: 20,
  wealth: 30,
  relationship: 40,
  spiritual: 45,
  movement: 50,
  health: 55,
  risk: 60,
  life_stage: 80,
  structure: 90,
};

const pillars = computed<FourPillarsDisplayPillar[]>(() => {
  const rawPillars = props.chartDisplay?.pillars;
  if (!rawPillars) return [];
  return pillarKeys.map((key) => rawPillars[key]).filter(Boolean);
});

const hasOverflowingShenSha = computed(() => pillars.value.some((pillar) => shenShaRows(pillar).length > MAX_SHEN_SHA_ROWS));
const profile = computed(() => props.chartDisplay?.profile ?? null);
const structureLabel = computed(() => profile.value?.structure_label || (profile.value?.gender_label === '女命' ? '坤造' : '乾造'));
function pad2(value: string | number): string {
  return String(value).padStart(2, '0');
}

const compactLunarDate = computed(() => {
  const raw = profile.value?.lunar_date || profile.value?.lunar_full_text || '';
  if (!raw) return '-';
  const match = raw.match(/(\d{4})年(?:闰)?(\d{1,2})月(\d{1,2})(?:日)?\s*([子丑寅卯辰巳午未申酉戌亥][时時])?/u);
  if (match) {
    return `${match[1]}-${pad2(match[2])}-${pad2(match[3])}${match[4] ? ` ${match[4].replace('時', '时')}` : ''}`;
  }
  return raw.replace(/^农历\s*/, '').replace(/年/g, '-').replace(/月/g, '-').replace(/日/g, ' ').replace(/\s+/g, ' ').trim();
});
const solarDateText = computed(() => {
  const raw = profile.value?.solar_datetime_text || '';
  const match = raw.match(/^(\d{4})-(\d{1,2})-(\d{1,2})/u);
  if (!match) return raw || '-';
  return `${match[1]}年${Number(match[2])}月${Number(match[3])}日`;
});
const trueSolarTimeText = computed(() => {
  const explicit = String(profile.value?.true_solar_time_text || '').trim();
  if (explicit && explicit !== '未校准') return explicit;
  const effective = String(profile.value?.effective_birth_datetime || '').trim();
  const match = effective.match(/^(\d{4})-(\d{2})-(\d{2})[T\s](\d{2}):(\d{2})/u);
  if (match) return `${match[1]}-${match[2]}-${match[3]} ${match[4]}:${match[5]}`;
  return '按默认北京真太阳时校准';
});
const maxElementCount = computed(() => Math.max(1, ...((props.elementCounts || []).map((item) => Number(item.value) || 0))));
const basicInfoRows = computed(() => [
  { label: '姓名', value: profile.value?.name || '未填写' },
  { label: '性别', value: `${profile.value?.gender_label || '-'} · ${structureLabel.value}` },
  { label: '公历', value: solarDateText.value },
  { label: '农历', value: profile.value?.lunar_date || '-' },
  { label: '生肖', value: profile.value?.zodiac || '-' },
  { label: '出生地区', value: profile.value?.birth_place || '未填写' },
  { label: '出生节气', value: profile.value?.solar_term_context || '-' },
  { label: '星座', value: profile.value?.constellation || '-' },
  { label: '星宿', value: profile.value?.xiu || '-' },
]);
const professionalInfoRows = computed(() => [
  { label: '真太阳时', value: trueSolarTimeText.value },
  { label: '胎元', value: profile.value?.tai_yuan || '-' },
  { label: '空亡', value: profile.value?.empty_branches_text || profile.value?.pillar_xun_kong_text || '-' },
  { label: '命宫', value: profile.value?.ming_gong || '-' },
  { label: '胎息', value: profile.value?.tai_xi || '-' },
  { label: '身宫', value: profile.value?.shen_gong || '-' },
  { label: '命卦', value: profile.value?.life_gua || '-' },
]);
const chartInfoRows = computed(() => [...basicInfoRows.value, ...professionalInfoRows.value]);
const boneWeight = computed(() => profile.value?.bone_weight ?? null);
const boneWeightParts = computed(() => {
  const parts = boneWeight.value?.parts || {};
  return [
    { label: '年', value: parts.year },
    { label: '月', value: parts.month },
    { label: '日', value: parts.day },
    { label: '时', value: parts.hour },
  ].filter((item) => typeof item.value === 'number');
});
const boneWeightVerse = computed(() => {
  const explicit = String(boneWeight.value?.verse || '').trim();
  if (explicit) return explicit;
  if (boneWeight.value?.total_qian === 41) {
    return '此命推来事不同，为人能干亦凡庸，中年还有逍遥福，不比前时运未通';
  }
  return '';
});
const boneWeightVerseLines = computed(() => {
  const verse = boneWeightVerse.value;
  if (!verse) return [];
  const clauses = verse.split(/[，,]/u).map((item) => item.trim()).filter(Boolean);
  if (clauses.length === 4) {
    return [`${clauses[0]}，${clauses[1]}`, `${clauses[2]}，${clauses[3]}`];
  }
  return [verse];
});
const favorableText = computed(() => (props.favorableElements || []).filter(Boolean).join('、') || '-');
const unfavorableText = computed(() => (props.unfavorableElements || []).filter(Boolean).join('、') || '-');

function elementTextClass(element: string | null | undefined): string {
  const value = String(element || '');
  if (value === '木') return 'text-[#059669]';
  if (value === '火') return 'text-[#E11D48]';
  if (value === '土') return 'text-[#78350F]';
  if (value === '金') return 'text-[#CA8A04]';
  if (value === '水') return 'text-[#2563EB]';
  return 'text-brand-ink-strong';
}

function elementBgClass(element: string | null | undefined): string {
  const value = String(element || '');
  if (value === '木') return 'bg-[#ECFDF5] border-[#A7F3D0]';
  if (value === '火') return 'bg-[#FFF1F2] border-[#FECDD3]';
  if (value === '土') return 'bg-[#FFFBEB] border-[#FCD34D]';
  if (value === '金') return 'bg-[#FFF7DA] border-[#F4D27A]';
  if (value === '水') return 'bg-[#EFF6FF] border-[#BFDBFE]';
  return 'bg-white border-slate-100';
}

function elementDotClass(element: string | null | undefined): string {
  const value = String(element || '');
  if (value === '木') return 'bg-[#10B981] border-[#ECFDF5]';
  if (value === '火') return 'bg-[#FB7185] border-[#FFF1F2]';
  if (value === '土') return 'bg-[#D97706] border-[#FFFBEB]';
  if (value === '金') return 'bg-[#D69E2E] border-[#FFF7DA]';
  if (value === '水') return 'bg-[#3B82F6] border-[#EFF6FF]';
  return 'bg-[#CBD5E1] border-white';
}

function cellText(value: string | null | undefined): string {
  return String(value || '').trim() || '-';
}

function elementFromNaYin(value: string | null | undefined): string {
  const text = cellText(value);
  const matched = text.match(/[木火土金水](?!.*[木火土金水])/u);
  return matched?.[0] || '';
}

function getShenShaToneScore(item: ShenShaCellItem): number {
  const text = `${item.category}${item.name}${item.meaning}`;
  if (/[贵人德福喜禄昌合赦喜医昌印舆]/u.test(text)) return 0;
  if (/[煞亡劫灾孤寡空刃鬼差错]/u.test(text)) return 2;
  return 1;
}

function shenShaRows(pillar: FourPillarsDisplayPillar): ShenShaCellItem[] {
  const details = Array.isArray(pillar.shen_sha_details) ? pillar.shen_sha_details : [];
  const detailByName = new Map<string, FourPillarsShenShaDetail>();
  details.forEach((item) => {
    if (item?.name && !detailByName.has(item.name)) {
      detailByName.set(item.name, item);
    }
  });
  const names = Array.isArray(pillar.shen_sha) && pillar.shen_sha.length
    ? pillar.shen_sha
    : details.map((item) => item.name);
  const rows = [...new Set(names.map((item) => String(item || '').trim()).filter(Boolean))].map((name) => {
    const detail = detailByName.get(name);
    return {
      name,
      meaning: String(detail?.meaning || ''),
      category: String(detail?.category || ''),
    };
  }).filter((item) => item.category !== 'life_stage' && !LIFE_STAGE_NAMES.has(item.name));
  return sortShenShaRows(rows);
}

function sortShenShaRows(rows: ShenShaCellItem[]): ShenShaCellItem[] {
  return rows
    .map((item, index) => ({ ...item, index }))
    .sort((left, right) => {
      const toneDelta = getShenShaToneScore(left) - getShenShaToneScore(right);
      if (toneDelta !== 0) return toneDelta;
      const nameDelta = (SHEN_SHA_NAME_ORDER[left.name] ?? 500) - (SHEN_SHA_NAME_ORDER[right.name] ?? 500);
      if (nameDelta !== 0) return nameDelta;
      const categoryDelta = (SHEN_SHA_CATEGORY_ORDER[left.category] ?? 99) - (SHEN_SHA_CATEGORY_ORDER[right.category] ?? 99);
      if (categoryDelta !== 0) return categoryDelta;
      return left.index - right.index;
    })
    .map(({ index: _index, ...item }) => item);
}

function visibleShenShaRows(pillar: FourPillarsDisplayPillar): ShenShaCellItem[] {
  const rows = shenShaRows(pillar);
  if (shenShaExpanded.value) return rows;
  if (rows.length > MAX_SHEN_SHA_ROWS) return rows.slice(0, 2);
  return rows;
}
</script>

<template>
  <section class="rounded-xl bg-white shadow-sm overflow-hidden">
    <div v-if="chartDisplay" class="space-y-1.5">
      <div class="mx-2 mt-2 rounded-lg bg-[#F8FAFF] px-2 py-1.5 flex items-center gap-1.5 text-[10.5px] leading-none">
        <span class="font-serif h-9 min-w-[56px] rounded-lg font-black text-white bg-[#2563EB] shrink-0 flex items-center justify-center gap-1 px-1.5">
          <UserRound :size="12" class="shrink-0" />
          <span class="flex flex-col items-start justify-center gap-0.5 text-[9.5px] leading-none">
            <span>{{ chartDisplay.profile.gender_label }}</span>
            <span>{{ structureLabel }}</span>
          </span>
        </span>
        <div class="min-w-0 flex-1 flex items-center gap-1">
          <CalendarDays :size="12" class="shrink-0 text-[#334155]" />
          <div class="min-w-0 flex-1 space-y-0.5">
            <p class="font-mono text-[10.5px] text-[#334155] truncate">
              公历 {{ chartDisplay.profile.solar_datetime_text }}
            </p>
            <p class="font-mono text-[10.5px] text-[#334155] truncate">
              农历 {{ compactLunarDate }}
            </p>
          </div>
        </div>
        <button
          type="button"
          class="shrink-0 h-7 px-1.5 rounded-lg bg-white border border-[#D8E3F5] text-[#1D4ED8] font-sans text-[9.5px] font-black flex items-center gap-0.5 shadow-sm"
          @click="infoModalOpen = true"
        >
          <Info :size="10" />
          更多命盘信息
        </button>
      </div>

      <div class="mx-2 mb-2 rounded-lg bg-white overflow-hidden">
        <div class="overflow-x-auto no-scrollbar">
          <table class="w-full min-w-[320px] table-fixed border-collapse text-center select-text">
            <thead>
              <tr class="bg-[#EAF1FF]">
                <th class="w-[14%] py-1.5 px-1 font-sans text-[10px] font-bold text-[#64748B]">柱别</th>
                <th
                  v-for="pillar in pillars"
                  :key="`${pillar.key}-head`"
                  class="w-[21.5%] py-1.5 px-1 font-serif text-[12px] font-black text-[#1D4ED8]"
                >
                  <span class="block leading-none">{{ pillar.label }}</span>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr class="bg-[#F8FAFF]">
                <td class="natal-row-label">主星</td>
                <td v-for="pillar in pillars" :key="`${pillar.key}-stem-god`" class="natal-cell natal-god">
                  {{ cellText(pillar.stem_ten_god) }}
                </td>
              </tr>
              <tr class="bg-white">
                <td class="natal-row-label">天干</td>
                <td v-for="pillar in pillars" :key="`${pillar.key}-stem`" class="natal-cell">
                  <span class="natal-glyph-wrap" :title="pillar.stem_element">
                    <span class="natal-stem-branch" :class="[elementTextClass(pillar.stem_element), elementBgClass(pillar.stem_element)]">
                      <span class="natal-glyph-text">{{ pillar.stem }}</span>
                    </span>
                    <span class="natal-element-dot" :class="elementDotClass(pillar.stem_element)" aria-hidden="true"></span>
                  </span>
                </td>
              </tr>
              <tr class="bg-white">
                <td class="natal-row-label">地支</td>
                <td v-for="pillar in pillars" :key="`${pillar.key}-branch`" class="natal-cell">
                  <span class="natal-glyph-wrap" :title="pillar.branch_element">
                    <span class="natal-stem-branch" :class="[elementTextClass(pillar.branch_element), elementBgClass(pillar.branch_element)]">
                      <span class="natal-glyph-text">{{ pillar.branch }}</span>
                    </span>
                    <span class="natal-element-dot" :class="elementDotClass(pillar.branch_element)" aria-hidden="true"></span>
                  </span>
                </td>
              </tr>
              <tr class="bg-[#F8FAFF]">
                <td class="natal-row-label">藏干</td>
                <td v-for="pillar in pillars" :key="`${pillar.key}-hidden`" class="natal-cell natal-hidden-cell">
                  <span
                    v-for="(item, index) in pillar.hidden_stems"
                    :key="`${pillar.key}-${item.stem}`"
                    class="natal-hidden-item"
                  >
                    <span class="natal-hidden-glyph" :class="elementTextClass(item.element)">{{ item.stem }}</span>
                    <span>{{ item.ten_god || pillar.branch_ten_gods[index] || '-' }}</span>
                  </span>
                  <span v-if="!pillar.hidden_stems.length" class="text-[10px] text-[#94A3B8]">-</span>
                </td>
              </tr>
              <tr class="bg-white">
                <td class="natal-row-label">地势</td>
                <td v-for="pillar in pillars" :key="`${pillar.key}-dishi`" class="natal-cell natal-text">{{ cellText(pillar.di_shi) }}</td>
              </tr>
              <tr class="bg-[#F8FAFF]">
                <td class="natal-row-label">自坐</td>
                <td v-for="pillar in pillars" :key="`${pillar.key}-sitting`" class="natal-cell natal-text">{{ cellText(pillar.self_sitting) }}</td>
              </tr>
              <tr class="bg-white">
                <td class="natal-row-label">旬空</td>
                <td v-for="pillar in pillars" :key="`${pillar.key}-xunkong`" class="natal-cell natal-text">{{ cellText(pillar.xun_kong) }}</td>
              </tr>
              <tr class="bg-[#F8FAFF]">
                <td class="natal-row-label">纳音</td>
                <td v-for="pillar in pillars" :key="`${pillar.key}-nayin`" class="natal-cell natal-text">
                  <span class="natal-nayin" :class="[elementTextClass(elementFromNaYin(pillar.na_yin)), elementBgClass(elementFromNaYin(pillar.na_yin))]">
                    {{ cellText(pillar.na_yin) }}
                  </span>
                </td>
              </tr>
              <tr class="bg-white">
                <td class="natal-row-label text-center">
                  <span class="block text-inherit">神煞</span>
                  <button
                    v-if="hasOverflowingShenSha"
                    type="button"
                    class="natal-shen-sha-toggle cursor-pointer outline-none hover:bg-indigo-50/20"
                    :aria-label="shenShaExpanded ? '收起神煞' : '展开神煞'"
                    :title="shenShaExpanded ? '收起神煞详情' : '展开神煞详情'"
                    @click="shenShaExpanded = !shenShaExpanded"
                  >
                    <ChevronUp v-if="shenShaExpanded" :size="10" />
                    <ChevronDown v-else :size="10" />
                  </button>
                </td>
                <td v-for="pillar in pillars" :key="`${pillar.key}-shen-sha`" class="natal-cell natal-shen-sha-cell">
                  <div v-if="shenShaRows(pillar).length" class="flex flex-col items-center justify-center gap-1 w-full">
                    <div class="natal-shen-sha-stack">
                      <span
                        v-for="item in visibleShenShaRows(pillar)"
                        :key="`${pillar.key}-${item.name}`"
                        class="natal-text block"
                        :title="item.meaning || item.name"
                      >
                        {{ item.name }}
                      </span>
                    </div>
                    <span v-if="!shenShaExpanded && shenShaRows(pillar).length > MAX_SHEN_SHA_ROWS" class="text-[9.5px] font-bold text-slate-400 mt-0.5 block whitespace-nowrap">
                      +{{ shenShaRows(pillar).length - 2 }} 更多
                    </span>
                  </div>
                  <span v-else class="text-[10px] text-[#94A3B8]">-</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <Teleport to="body">
        <transition name="fade-slide">
          <div v-if="infoModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/35 px-4 py-8" @click.self="infoModalOpen = false">
            <div class="w-full max-w-[360px] max-h-[80vh] overflow-hidden rounded-2xl bg-white border border-[#D8E3F5] shadow-2xl flex flex-col">
              <div class="shrink-0 px-4 py-3 border-b border-[#E2E8F0] flex items-center justify-between gap-3 bg-[#F8FAFF]">
                <div>
                  <p class="font-sans text-[10px] font-black tracking-wide text-[#64748B]">MORE CHART INFO</p>
                  <h3 class="font-serif text-[16px] font-black text-[#1D4ED8] mt-0.5">更多命盘信息</h3>
                </div>
                <button type="button" class="w-8 h-8 rounded-lg bg-white border border-[#D8E3F5] flex items-center justify-center text-[#64748B]" @click="infoModalOpen = false">
                  <X :size="15" />
                </button>
              </div>
              <div class="overflow-y-auto px-4 py-3 space-y-4">
                <section>
                  <div class="natal-info-grid">
                    <div v-for="item in chartInfoRows" :key="`chart-${item.label}`" class="natal-info-item">
                      <span class="natal-info-label">{{ item.label }}</span>
                      <span class="natal-info-value">{{ item.value }}</span>
                    </div>
                  </div>
                </section>

                <section>
                  <h4 class="natal-info-section-title">五行能量</h4>
                  <div class="space-y-2">
                    <div v-for="item in props.elementCounts || []" :key="`element-${item.element}`" class="natal-element-bar-row">
                      <span class="natal-element-bar-label" :class="elementTextClass(item.element)">{{ item.element }}</span>
                      <div class="natal-element-bar-track">
                        <div
                          class="natal-element-bar-fill"
                          :class="elementDotClass(item.element)"
                          :style="{ width: `${Math.max(6, Math.round((Number(item.value) || 0) / maxElementCount * 100))}%` }"
                        ></div>
                      </div>
                      <span class="natal-element-bar-value">{{ item.value }}</span>
                    </div>
                  </div>
                  <div class="natal-info-grid mt-3">
                    <div class="natal-info-item natal-info-item-wide">
                      <span class="natal-info-label">旺衰初判</span>
                      <span class="natal-info-value">{{ props.strengthLabel || '-' }}</span>
                    </div>
                    <div class="natal-info-item">
                      <span class="natal-info-label">喜用候选</span>
                      <span class="natal-info-value">{{ favorableText }}</span>
                    </div>
                    <div class="natal-info-item">
                      <span class="natal-info-label">忌神候选</span>
                      <span class="natal-info-value">{{ unfavorableText }}</span>
                    </div>
                  </div>
                </section>

                <section>
                  <h4 class="natal-info-section-title">袁天罡称骨</h4>
                  <div v-if="boneWeight" class="rounded-xl bg-[#F8FAFF] border border-[#D8E3F5] p-3 space-y-3">
                    <div class="flex items-center justify-between gap-3">
                      <div>
                        <span class="block font-serif text-[18px] font-black text-[#1D4ED8]">{{ boneWeight.total_label }}</span>
                        <span class="block font-sans text-[9.5px] font-bold text-[#64748B] mt-0.5">
                          总骨重 {{ boneWeight.total_qian }} 钱
                        </span>
                      </div>
                      <span class="font-sans text-[10px] font-bold text-[#64748B] text-right leading-snug">
                        {{ boneWeight.year_ganzhi }}年<br />
                        {{ boneWeight.lunar_month }}月{{ boneWeight.lunar_day }}日 · {{ boneWeight.hour_branch }}时
                      </span>
                    </div>

                    <div v-if="boneWeightParts.length" class="grid grid-cols-4 gap-1.5">
                      <div v-for="item in boneWeightParts" :key="`bone-${item.label}`" class="rounded-lg bg-white border border-[#E2E8F0] px-1.5 py-1.5 text-center">
                        <span class="block font-sans text-[9px] font-black text-[#94A3B8]">{{ item.label }}骨</span>
                        <span class="block font-serif text-[12px] font-black text-[#334155] mt-0.5">{{ item.value }}钱</span>
                      </div>
                    </div>

                    <div class="rounded-xl bg-white border border-[#E2E8F0] p-2.5">
                      <span class="block font-sans text-[9.5px] font-black text-[#94A3B8]">格局</span>
                      <p class="font-serif text-[12px] font-black text-brand-ink-strong leading-relaxed mt-1">
                        {{ boneWeight.fate_pattern || boneWeight.summary }}
                      </p>
                    </div>

                    <div v-if="boneWeightVerse" class="rounded-xl bg-white border border-[#E2E8F0] p-2.5">
                      <span class="block font-sans text-[9.5px] font-black text-[#94A3B8]">称骨歌诀</span>
                      <div class="font-serif text-[12px] font-bold text-[#1E293B] leading-relaxed mt-1 space-y-0.5">
                        <p v-for="line in boneWeightVerseLines" :key="line">{{ line }}</p>
                      </div>
                    </div>

                    <p class="font-sans text-[10px] text-[#64748B] leading-relaxed">称骨为传统资料展示，不作为命盘好坏判断依据。</p>
                  </div>
                  <p v-else class="font-sans text-[11px] text-[#64748B] rounded-xl bg-[#F8FAFF] border border-[#D8E3F5] p-3">称骨资料暂未匹配。</p>
                </section>
              </div>
            </div>
          </div>
        </transition>
      </Teleport>

    </div>

    <div v-else class="p-4">
      <p class="font-sans text-[11px] text-[#1D4ED8] font-bold tracking-wide">NATAL CHART</p>
      <p class="font-sans text-[13px] text-brand-secondary mt-2">排盘表正在准备，当前报告会先显示旧版命盘摘要。</p>
    </div>
  </section>
</template>

<style scoped>
.natal-row-label {
  font-family: inherit;
  font-size: 10px;
  font-weight: 800;
  line-height: 1.25;
  color: #1D4ED8;
  background: rgba(234, 241, 255, 0.8);
  padding: 6px 3px;
  vertical-align: middle;
}

.natal-cell {
  padding: 5px 3px;
  text-align: center;
  vertical-align: middle;
}

.natal-god {
  font-family: serif;
  font-size: 11px;
  font-weight: 900;
  color: #1D4ED8;
}

.natal-glyph-wrap {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  vertical-align: middle;
}

.natal-stem-branch {
  width: 30px;
  height: 30px;
  border-radius: 999px;
  border-width: 1px;
  display: grid;
  place-items: center;
  font-family: "Noto Serif SC", "Noto Serif CJK SC", "Source Han Serif SC", "Songti SC", serif;
  font-size: 17px;
  font-weight: 900;
  line-height: 1;
  letter-spacing: 0;
  text-shadow: 0 0 0 currentColor;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.58), 0 1px 2px rgba(15, 23, 42, 0.05);
}

.natal-glyph-text {
  display: block;
  width: 100%;
  text-align: center;
  transform: translateY(-0.5px);
}

.natal-element-dot {
  position: absolute;
  top: 50%;
  right: -4px;
  width: 8px;
  height: 8px;
  border: 1.5px solid;
  border-radius: 999px;
  transform: translateY(-50%);
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.12);
}

.natal-hidden-cell {
  padding: 5px 3px;
}

.natal-hidden-item {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  border: 1px solid #D8E3F5;
  margin: 1px;
  padding: 2px 3px;
  border-radius: 5px;
  background: #FFFFFF;
  color: #64748B;
  font-size: 9px;
  font-weight: 700;
  line-height: 1.2;
  white-space: nowrap;
}

.natal-hidden-glyph {
  font-family: "Noto Serif SC", "Noto Serif CJK SC", "Source Han Serif SC", "Songti SC", serif;
  font-size: 10px;
  font-weight: 900;
  line-height: 1;
  text-shadow: 0 0 0 currentColor;
}

.natal-text {
  font-family: inherit;
  font-size: 10.5px;
  font-weight: 800;
  line-height: 1.25;
  color: #334155;
}

.natal-nayin {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  max-width: 100%;
  min-height: 20px;
  border-width: 1px;
  border-radius: 999px;
  padding: 2px 5px;
  font-size: 10px;
  font-weight: 900;
  line-height: 1.1;
  white-space: nowrap;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.48);
}

.natal-shen-sha-toggle {
  width: 18px;
  height: 14px;
  margin: 3px auto 0;
  border: 1px solid #BFDBFE;
  border-radius: 999px;
  color: #1D4ED8;
  background: #FFFFFF;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.natal-shen-sha-cell {
  padding: 4px 2px;
  vertical-align: middle;
}

.natal-shen-sha-stack {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  width: 100%;
}

.natal-info-section-title {
  margin-bottom: 8px;
  font-family: "Noto Serif SC", "Noto Serif CJK SC", "Source Han Serif SC", "Songti SC", serif;
  font-size: 13px;
  font-weight: 900;
  line-height: 1.2;
  color: #1D4ED8;
}

.natal-info-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.natal-info-item {
  min-width: 0;
  border: 1px solid #E2E8F0;
  border-radius: 10px;
  background: #FFFFFF;
  padding: 7px 8px;
}

.natal-info-item-wide {
  grid-column: 1 / -1;
}

.natal-info-label {
  display: block;
  font-size: 9.5px;
  font-weight: 800;
  line-height: 1.2;
  color: #94A3B8;
}

.natal-info-value {
  display: block;
  margin-top: 4px;
  font-size: 11px;
  font-weight: 800;
  line-height: 1.35;
  color: #334155;
  word-break: break-word;
}

.natal-element-bar-row {
  display: grid;
  grid-template-columns: 22px minmax(0, 1fr) 24px;
  align-items: center;
  gap: 8px;
}

.natal-element-bar-label {
  font-family: "Noto Serif SC", "Noto Serif CJK SC", "Source Han Serif SC", "Songti SC", serif;
  font-size: 13px;
  font-weight: 900;
  line-height: 1;
  text-align: center;
}

.natal-element-bar-track {
  height: 8px;
  overflow: hidden;
  border-radius: 999px;
  background: #E2E8F0;
}

.natal-element-bar-fill {
  height: 100%;
  border-width: 0;
  border-radius: inherit;
}

.natal-element-bar-value {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
  font-size: 11px;
  font-weight: 900;
  line-height: 1;
  color: #64748B;
  text-align: right;
}

.no-scrollbar::-webkit-scrollbar {
  display: none;
}

.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
