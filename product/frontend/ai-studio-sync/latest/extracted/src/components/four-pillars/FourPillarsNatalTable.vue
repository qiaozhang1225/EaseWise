<script setup lang="ts">
import { computed, ref } from 'vue';
import { CalendarDays, ChevronDown, ChevronUp, UserRound } from 'lucide-vue-next';
import type { FourPillarsChartDisplay, FourPillarsDisplayPillar, FourPillarsPillarKey, FourPillarsShenShaDetail } from '../../types/api';

const props = defineProps<{
  chartDisplay: FourPillarsChartDisplay | null;
  score?: number | null;
  elementSummary?: string;
}>();

const pillarKeys: FourPillarsPillarKey[] = ['year', 'month', 'day', 'hour'];
const MAX_SHEN_SHA_ROWS = 3;

type ShenShaCellItem = {
  name: string;
  meaning: string;
  category: string;
};

const shenShaExpanded = ref(false);
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

function shenShaToneClass(item: ShenShaCellItem): string {
  const name = item.name.trim();
  const category = item.category || '';
  
  const positiveShenSha = [
    '天乙贵人', '太极贵人', '福星贵人', '天德贵人', '月德贵人', 
    '天德合', '月德合', '文昌', '国印贵人', '金舆', '禄神', '天喜', 
    '红鸾', '天医', '天赦', '将星', '华盖'
  ];
  
  const cautionShenSha = [
    '孤辰', '寡宿', '羊刃', '飞刃', '亡神', '劫煞', 
    '灾煞', '元辰', '勾煞', '绞煞', '五鬼', '阴阳差错', 
    '空亡', '童子', '魁罡'
  ];

  if (positiveShenSha.some(p => name.includes(p))) {
    return 'shen-sha-positive';
  }
  if (cautionShenSha.some(c => name.includes(c))) {
    return 'shen-sha-caution';
  }
  
  const text = `${category}${name}${item.meaning}`;
  if (/[贵人德福喜禄昌合]/u.test(text)) return 'shen-sha-positive';
  if (/[煞亡劫灾孤寡空刃]/u.test(text)) return 'shen-sha-caution';
  
  return 'shen-sha-neutral';
}

function getShenShaToneScore(item: ShenShaCellItem): number {
  const tone = shenShaToneClass(item);
  if (tone === 'shen-sha-positive') return 1;
  if (tone === 'shen-sha-neutral') return 2;
  return 3;
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
  const rows = [...new Set(names.map((nameItem) => String(nameItem || '').trim()).filter(Boolean))].map((name) => {
    const detail = detailByName.get(name);
    return {
      name,
      meaning: String(detail?.meaning || ''),
      category: String(detail?.category || ''),
    };
  });
  const diShi = String(pillar.di_shi || '').trim();
  if (diShi && !rows.some((item) => item.name === diShi)) {
    rows.push({
      name: diShi,
      meaning: '十二长生地势',
      category: 'life_stage',
    });
  }
  return sortShenShaRows(rows);
}

function sortShenShaRows(rows: ShenShaCellItem[]): ShenShaCellItem[] {
  return [...rows]
    .map((item, index) => ({ ...item, index }))
    .sort((left, right) => {
      const toneLeft = getShenShaToneScore(left);
      const toneRight = getShenShaToneScore(right);
      if (toneLeft !== toneRight) return toneLeft - toneRight;

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
  if (shenShaExpanded.value) {
    return rows;
  }
  if (rows.length > MAX_SHEN_SHA_ROWS) {
    return rows.slice(0, 2);
  }
  return rows;
}
</script>

<template>
  <section class="rounded-xl bg-white shadow-sm overflow-hidden select-text text-left">
    <div v-if="chartDisplay" class="space-y-1.5">
      <div class="mx-2 mt-2 bg-[#F8FAFF] px-2.5 py-1.5 flex items-center gap-2 text-[10.5px] leading-none rounded-lg">
        <span class="font-serif px-1.5 py-0.5 rounded-md font-black text-white bg-[#2563EB] shrink-0 text-[9.5px] flex items-center gap-1">
          <UserRound :size="10" />
          {{ chartDisplay.profile.gender_label }}
        </span>
        <span class="font-mono text-[#334155] truncate">
          <CalendarDays :size="10" class="inline -mt-0.5 mr-0.5" />
          公历 {{ chartDisplay.profile.solar_datetime_text }}
        </span>
        <span class="ml-auto font-serif text-[#64748B] shrink-0">
          生肖 {{ chartDisplay.profile.zodiac || '-' }}
        </span>
        <div v-if="score !== null && score !== undefined" class="shrink-0 rounded-md bg-[#1D4ED8] text-white px-1.5 py-1 text-center leading-none">
          <p class="font-mono text-[12px] leading-none font-black">{{ score ?? '--' }}分</p>
        </div>
      </div>

      <div class="mx-2 mb-2 rounded-lg bg-white overflow-hidden border border-gray-100">
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
                    <span class="natal-stem-branch" :class="[elementTextClass(pillar.stem_element), elementBgClass(pillar.stem_element)]">{{ pillar.stem }}</span>
                    <span class="natal-element-dot" :class="elementDotClass(pillar.stem_element)" aria-hidden="true"></span>
                  </span>
                </td>
              </tr>
              <tr class="bg-white">
                <td class="natal-row-label">地支</td>
                <td v-for="pillar in pillars" :key="`${pillar.key}-branch`" class="natal-cell">
                  <span class="natal-glyph-wrap" :title="pillar.branch_element">
                    <span class="natal-stem-branch" :class="[elementTextClass(pillar.branch_element), elementBgClass(pillar.branch_element)]">{{ pillar.branch }}</span>
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
                    @click="shenShaExpanded = !shenShaExpanded"
                    class="natal-shen-sha-toggle cursor-pointer outline-none hover:bg-indigo-50/20"
                    :title="shenShaExpanded ? '收起神煞详情' : '展开神煞详情'"
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
                    <!-- Indicator for remaining hidden Shen Sha -->
                    <span
                      v-if="!shenShaExpanded && shenShaRows(pillar).length > MAX_SHEN_SHA_ROWS"
                      class="text-[9.5px] font-bold text-slate-400 mt-0.5 block whitespace-nowrap"
                    >
                      +{{ shenShaRows(pillar).length - 2 }} 更多
                    </span>
                  </div>
                  <span v-else class="text-[10px] text-[#94A3B8]">-</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-if="props.elementSummary" class="natal-element-summary">
          {{ props.elementSummary }}
        </p>
      </div>
    </div>

    <div v-else class="p-4">
      <p class="font-sans text-[11px] text-[#1D4ED8] font-bold tracking-wide">NATAL CHART</p>
      <p class="font-sans text-[13px] text-brand-secondary mt-2">排盘表正在准备，并同步您的生辰八字天盘格局。</p>
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
  padding-right: 5px;
}

.natal-stem-branch {
  width: 30px;
  height: 30px;
  border-radius: 999px;
  border-width: 1px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-family: "Noto Serif SC", "Noto Serif CJK SC", "Source Han Serif SC", "Songti SC", serif;
  font-size: 17px;
  font-weight: 900;
  line-height: 1;
  letter-spacing: 0;
  text-shadow: 0 0 0 currentColor;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.58), 0 1px 2px rgba(15, 23, 42, 0.05);
}

.natal-element-dot {
  position: absolute;
  top: 50%;
  right: 0;
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
  vertical-align: top;
}

.natal-shen-sha-stack {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  width: 100%;
}

.natal-shen-sha-item {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 90%;
  max-width: 68px;
  border: 1.5px solid;
  border-radius: 4px;
  padding: 2px 3px;
  font-size: 9.5px;
  font-weight: 800;
  line-height: 1.1;
  word-break: keep-all;
  white-space: nowrap;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
}

.natal-shen-sha-item.shen-sha-positive {
  background: #ECFDF5;
  border-color: #A7F3D0;
  color: #047857;
}

.natal-shen-sha-item.shen-sha-neutral {
  background: #EFF6FF;
  border-color: #BFDBFE;
  color: #1D4ED8;
}

.natal-shen-sha-item.shen-sha-caution {
  background: #F8FAFC;
  border-color: #E2E8F0;
  color: #64748B;
}

.natal-element-summary {
  border-top: 1px solid #E2E8F0;
  background: #F8FAFF;
  padding: 6px 8px;
  font-size: 10.5px;
  font-weight: 700;
  line-height: 1.45;
  color: #475569;
  text-align: left;
}

.no-scrollbar::-webkit-scrollbar {
  display: none;
}

.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
