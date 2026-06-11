<script setup lang="ts">
import { computed } from 'vue';
import { CalendarDays, UserRound } from 'lucide-vue-next';
import type { FourPillarsChartDisplay, FourPillarsDisplayPillar, FourPillarsPillarKey } from '../../types/api';

const props = defineProps<{
  chartDisplay: FourPillarsChartDisplay | null;
  score?: number | null;
  elementSummary?: string;
}>();

const pillarKeys: FourPillarsPillarKey[] = ['year', 'month', 'day', 'hour'];

const pillars = computed<FourPillarsDisplayPillar[]>(() => {
  const rawPillars = props.chartDisplay?.pillars;
  if (!rawPillars) return [];
  return pillarKeys.map((key) => rawPillars[key]).filter(Boolean);
});

function elementTextClass(element: string | null | undefined): string {
  const value = String(element || '');
  if (value === '木') return 'text-emerald-600';
  if (value === '火') return 'text-rose-600';
  if (value === '土') return 'text-amber-800';
  if (value === '金') return 'text-slate-700';
  if (value === '水') return 'text-blue-600';
  return 'text-brand-ink-strong';
}

function elementBgClass(element: string | null | undefined): string {
  const value = String(element || '');
  if (value === '木') return 'bg-emerald-50 border-emerald-100';
  if (value === '火') return 'bg-rose-50 border-rose-100';
  if (value === '土') return 'bg-amber-50 border-amber-100';
  if (value === '金') return 'bg-slate-100 border-slate-200';
  if (value === '水') return 'bg-blue-50 border-blue-100';
  return 'bg-white border-slate-100';
}

function cellText(value: string | null | undefined): string {
  return String(value || '').trim() || '-';
}
</script>

<template>
  <section class="rounded-xl bg-white shadow-sm overflow-hidden">
    <div v-if="chartDisplay" class="space-y-1.5">
      <div class="mx-2 mt-2 rounded-lg bg-[#F8FAFF] px-2.5 py-1.5 flex items-center gap-2 text-[10.5px] leading-none">
        <span class="font-serif px-1.5 py-0.5 rounded-md font-black text-white bg-[#2563EB] shrink-0 text-[9.5px] flex items-center gap-1">
          <UserRound :size="10" />
          {{ chartDisplay.profile.gender_label }}
        </span>
        <span class="font-mono text-[#334155] truncate">
          <CalendarDays :size="10" class="inline -mt-0.5 mr-0.5" />
          公历 {{ chartDisplay.profile.solar_datetime_text }}
        </span>
        <span class="ml-auto font-serif text-[#64748B] shrink-0">
          生肖{{ chartDisplay.profile.zodiac || '-' }}
        </span>
        <div v-if="score !== null && score !== undefined" class="shrink-0 rounded-md bg-[#1D4ED8] text-white px-1.5 py-1 text-center leading-none">
          <p class="font-mono text-[12px] leading-none font-black">{{ score ?? '--' }}分</p>
        </div>
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
                  <span class="natal-stem-branch" :class="[elementTextClass(pillar.stem_element), elementBgClass(pillar.stem_element)]">{{ pillar.stem }}</span>
                  <span class="natal-sub">{{ pillar.stem_element }}</span>
                </td>
              </tr>
              <tr class="bg-white">
                <td class="natal-row-label">地支</td>
                <td v-for="pillar in pillars" :key="`${pillar.key}-branch`" class="natal-cell">
                  <span class="natal-stem-branch" :class="[elementTextClass(pillar.branch_element), elementBgClass(pillar.branch_element)]">{{ pillar.branch }}</span>
                  <span class="natal-sub">{{ pillar.branch_element }}</span>
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
                    <span class="font-serif font-black" :class="elementTextClass(item.element)">{{ item.stem }}</span>
                    <span>{{ item.ten_god || pillar.branch_ten_gods[index] || '-' }}</span>
                  </span>
                  <span v-if="!pillar.hidden_stems.length" class="text-[10px] text-[#94A3B8]">-</span>
                </td>
              </tr>
              <tr class="bg-white">
                <td class="natal-row-label">纳音</td>
                <td v-for="pillar in pillars" :key="`${pillar.key}-nayin`" class="natal-cell natal-text">{{ cellText(pillar.na_yin) }}</td>
              </tr>
              <tr class="bg-white">
                <td class="natal-row-label">地势</td>
                <td v-for="pillar in pillars" :key="`${pillar.key}-dishi`" class="natal-cell natal-text">{{ cellText(pillar.di_shi) }}</td>
              </tr>
              <tr class="bg-[#F8FAFF]">
                <td class="natal-row-label">旬空</td>
                <td v-for="pillar in pillars" :key="`${pillar.key}-xunkong`" class="natal-cell natal-text">{{ cellText(pillar.xun_kong) }}</td>
              </tr>
              <tr class="bg-white">
                <td class="natal-row-label">自坐</td>
                <td v-for="pillar in pillars" :key="`${pillar.key}-sitting`" class="natal-cell natal-text">{{ cellText(pillar.self_sitting) }}</td>
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

.natal-stem-branch {
  width: 28px;
  height: 28px;
  border-radius: 999px;
  border-width: 1px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-family: serif;
  font-size: 16px;
  font-weight: 900;
  line-height: 1;
}

.natal-sub {
  display: block;
  margin-top: 2px;
  font-family: inherit;
  font-size: 9px;
  font-weight: 700;
  color: #64748B;
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

.natal-text {
  font-family: inherit;
  font-size: 10.5px;
  font-weight: 800;
  line-height: 1.25;
  color: #334155;
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
