<script setup lang="ts">
import { ref, computed } from 'vue';
import { 
  ArrowLeft, Coins, Award, Users, Share2, Check, Sparkles, 
  TrendingUp, Users2, ShieldCheck, Landmark, CheckCircle2,
  Gift, Calculator, HelpCircle
} from 'lucide-vue-next';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';

// Emits to communicate with parent
const emit = defineEmits<{
  (e: 'close'): void;
}>();

const copied = ref(false);
const showApplyPlaceholder = ref(false);
const { openCustomerServiceModal } = useEaseWiseApp();

// Interactive Calculator states
// We divide the calculator into two versions: "partner" and "ambassador"
const calcVersion = ref<'partner' | 'ambassador'>('partner');

// Sub-tier selection for the "Ambassador" version
const selectedAmbassadorTier = ref<'normal' | 'vip' | 'svip'>('normal');

// Input values for calculation (Annual estimates)
const directUsersCount = ref(50);                      // 直属推荐人脉数
const avgAnnualDirectSpend = ref(300);                  // 平均直属推荐年消费额

const normalAmbassadorPerformance = ref(30000);         // 旗下推广大使推广充值金额
const vipAmbassadorPerformance = ref(20000);            // 旗下 VIP 推广大使推广充值金额
const svipAmbassadorPerformance = ref(10000);           // 旗下 SVIP 推广大使推广充值金额

// Rates mapping for ambassador tiers
const tierRates = {
  normal: 0.10, // 普通
  vip: 0.25,    // VIP
  svip: 0.40    // SVIP
};

const asNumber = (value: number | string) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
};

// Computed Earnings (Annual basis: "年收益")
const directAnnualPerformance = computed(() => {
  return asNumber(directUsersCount.value) * asNumber(avgAnnualDirectSpend.value);
});

const ambassadorAnnualEarn = computed(() => {
  const rate = tierRates[selectedAmbassadorTier.value];
  return Math.round(directAnnualPerformance.value * rate);
});

const partnerDirectAnnualEarn = computed(() => {
  return Math.round(directAnnualPerformance.value * 0.15);
});

const partnerTeamManagementAnnualEarn = computed(() => {
  return Math.round(teamPerformanceTotal.value * 0.15);
});

const teamPerformanceTotal = computed(() => {
  return (
    asNumber(normalAmbassadorPerformance.value) +
    asNumber(vipAmbassadorPerformance.value) +
    asNumber(svipAmbassadorPerformance.value) +
    directAnnualPerformance.value
  );
});

const teamBonusTotal = computed(() => {
  return Math.round(
    asNumber(normalAmbassadorPerformance.value) * 0.15 +
    asNumber(vipAmbassadorPerformance.value) * 0.10 +
    asNumber(svipAmbassadorPerformance.value) * 0.05 +
    directAnnualPerformance.value * 0.05
  );
});

const partnerPersonalTeamBonus = computed(() => {
  if (!teamPerformanceTotal.value) {
    return 0;
  }

  return Math.round((directAnnualPerformance.value / teamPerformanceTotal.value) * teamBonusTotal.value);
});

const partnerTotalAnnualEarn = computed(() => {
  return partnerDirectAnnualEarn.value + partnerTeamManagementAnnualEarn.value + partnerPersonalTeamBonus.value;
});

// Format currency
const formatCurrency = (val: number) => {
  return new Intl.NumberFormat('zh-CN', { style: 'currency', currency: 'CNY', maximumFractionDigits: 0 }).format(val);
};

// Simple sharing summary designed to copy directly for H5 forwards
const H5SummaryLink = computed(() => {
  return `【易如反掌·起盘评测】合伙与推广说明书。推广大使直属提成10%/25%/40%，推广订单完成后7天自动结算至推广余额；创始合伙人统一招商签约，收益测算按直属15% + 团队15% + 团队奖金，合伙人推荐服务返点55%。\n官方咨询微信号: yirufanzhang888。详见个人中心推广合伙说明。`;
});

const copyManualText = () => {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(H5SummaryLink.value);
    copied.value = true;
    setTimeout(() => copied.value = false, 2000);
  } else {
    // Fallback if inside restricted webview
    const input = document.createElement('textarea');
    input.value = H5SummaryLink.value;
    document.body.appendChild(input);
    input.select();
    try {
      document.execCommand('copy');
      copied.value = true;
      setTimeout(() => copied.value = false, 2000);
    } catch (err) {
      console.error('Fallback copy failed', err);
    }
    document.body.removeChild(input);
  }
};

const handleContactSupport = () => {
  openCustomerServiceModal('promotion_consulting');
};

const handleApplyJoin = () => {
  showApplyPlaceholder.value = true;
};
</script>

<template>
  <div class="fixed inset-0 z-[120] bg-brand-paper w-full h-full flex flex-col overflow-hidden font-sans text-left">
    <!-- H5 Dynamic Header -->
    <header class="bg-white border-b border-gray-100 flex items-center justify-between px-4 py-3.5 sticky top-0 z-10 shadow-xs shrink-0">
      <button 
        @click="emit('close')"
        class="flex items-center gap-1 text-brand-secondary hover:text-brand-ink-strong transition-colors cursor-pointer outline-none text-[14px]"
      >
        <ArrowLeft :size="18" />
        <span class="font-semibold">返回</span>
      </button>
      <div class="text-center absolute left-1/2 -translate-x-1/2">
        <h1 class="font-serif font-black text-[15px] text-brand-ink-strong tracking-wide">
          合伙与推广说明书
        </h1>
      </div>
      <button 
        @click="copyManualText"
        class="p-2 text-brand-primary bg-indigo-50/50 hover:bg-brand-primary/5 rounded-full transition-colors cursor-pointer outline-none relative"
        title="分享大纲"
      >
        <Check v-if="copied" :size="18" class="text-green-600" />
        <Share2 v-else :size="18" />
      </button>
    </header>

    <!-- Scrollable Main Flow Page (One direct downward H5 scrollable page) -->
    <div class="flex-1 overflow-y-auto no-scrollbar pb-24 bg-gray-50/30">
      
      <!-- 1. H5 Master Hero Banner -->
      <section class="relative bg-brand-ink-strong text-white py-10 px-5 overflow-hidden text-center">
        <!-- Ambient grids and lights -->
        <div class="absolute inset-0 bg-[radial-gradient(circle_at_bottom_right,rgba(99,102,241,0.18),transparent_70%)] pointer-events-none"></div>
        <div class="absolute inset-0 bg-[linear-gradient(to_bottom,transparent,rgba(15,17,23,0.3))] pointer-events-none"></div>
        <div class="absolute -right-12 -top-12 w-32 h-32 bg-amber-500/5 rounded-full blur-2xl pointer-events-none"></div>
        
        <div class="relative z-10 space-y-2.5 max-w-sm mx-auto">
          <div class="inline-flex items-center gap-1 px-3 py-0.5 bg-brand-primary/20 border border-brand-primary/45 rounded-full text-brand-accent text-[10px] font-black tracking-widest uppercase">
            👑 易如反掌 · 创富生态联盟
          </div>
          <h2 class="text-[25px] font-serif font-black tracking-wide text-amber-100">
            商业定价与合伙提成全案
          </h2>
        </div>
      </section>

      <!-- Sequential Page Container (H5 Flow) -->
      <div class="p-4 max-w-md mx-auto space-y-6">

        <!-- SECTION A: 积分核心定价(Basic Pricing) -->
        <div class="space-y-4">
          <div class="flex items-center gap-2 pb-1 border-b border-gray-200">
            <span class="w-1 h-4.5 bg-brand-primary rounded-full"></span>
            <h3 class="text-[14.5px] font-black text-brand-ink-strong font-serif">一、核心计价标准</h3>
          </div>

          <!-- Base Rule intro -->
          <div class="bg-white rounded-2xl p-4 border border-gray-150/60 shadow-xs space-y-2.5">
            <p class="text-[12.5px] text-brand-secondary leading-relaxed font-sans">
              本产品的核心记号代币为<strong>平台积分</strong>。
            </p>
            
            <div class="grid grid-cols-2 gap-2.5 pt-1">
              <div class="bg-brand-paper p-3 rounded-xl border border-gray-100 text-left">
                <span class="text-[9px] font-bold text-brand-secondary uppercase block">常规原价</span>
                <span class="text-[13.5px] font-black text-brand-ink-strong block mt-0.5">1 元 = 50 积分</span>
                <span class="text-[8.5px] text-brand-secondary/80 block mt-0.5">普通小额充值</span>
              </div>
              <div class="bg-indigo-50/40 p-3 rounded-xl border border-brand-primary/10 text-left">
                <span class="text-[9px] font-bold text-brand-primary uppercase block">常规大额优惠</span>
                <span class="text-[13.5px] font-black text-brand-primary block mt-0.5">1 元 = 100 积分</span>
                <span class="text-[8.5px] text-brand-secondary block mt-0.5">高额大礼包回馈</span>
              </div>
            </div>
            
            <p class="text-[10.5px] text-slate-400 leading-tight pt-0.5">
              平均每一次功能使用成本约为 1~2 元，客户体验流畅，高性价比，极易复购。
            </p>
          </div>
        </div>

        <!-- SECTION B: 用户身份结构说明 (4 tiers simplified) -->
        <div class="space-y-4">
          <div class="flex items-center gap-2 pb-1 border-b border-gray-200">
            <span class="w-1 h-4.5 bg-brand-primary rounded-full"></span>
            <h3 class="text-[14.5px] font-black text-brand-ink-strong font-serif">二、线上系统四维身份界定</h3>
          </div>

          <p class="text-[12px] text-brand-secondary leading-relaxed font-sans">
            线上各级身份对应不同分佣与结算规则，推荐客户永久锚定，无须二次引流：
          </p>

          <div class="border border-gray-150 rounded-2xl bg-white overflow-hidden shadow-xs">
            <table class="w-full table-fixed text-center border-collapse">
              <thead>
                <tr class="bg-gray-50/80 text-[9.5px] font-bold text-brand-secondary border-b border-gray-150">
                  <th class="py-2 px-1 w-1/3">身份层级</th>
                  <th class="py-2 px-1 w-1/3">销售推广分佣比例</th>
                  <th class="py-2 px-1 w-1/3">结算说明</th>
                </tr>
              </thead>
              <tbody class="text-[11px]">
                <tr class="border-b border-gray-100">
                  <td class="py-2.5 px-1 font-extrabold text-brand-ink">普通用户</td>
                  <td class="py-2.5 px-1 text-brand-secondary font-black">—</td>
                  <td class="py-2.5 px-2 text-brand-secondary font-black">—</td>
                </tr>
                <tr class="border-b border-gray-100 bg-gray-50/20">
                  <td class="py-2.5 px-1 font-bold text-amber-800">推广大使</td>
                  <td class="py-2.5 px-1 text-emerald-600 font-extrabold text-[12px]">10% 直属提成</td>
                  <td rowspan="3" class="py-2 px-2 text-left align-middle text-[10px] text-brand-secondary leading-snug border-l border-gray-100">
                    推广提成以 7 天为 standard。订单完成后 7 天自动结算至推广余额，达最低提现金额后可随时提现。
                  </td>
                </tr>
                <tr class="border-b border-gray-100">
                  <td class="py-2.5 px-1 font-extrabold text-amber-600">VIP 推广大使</td>
                  <td class="py-2.5 px-1 text-emerald-600 font-black text-[12px]">25% 直属提成</td>
                </tr>
                <tr class="bg-purple-500/[0.04]">
                  <td class="py-2.5 px-1 font-black text-purple-700">SVIP 推广大使</td>
                  <td class="py-2.5 px-1 text-red-600 font-black text-[12px]">40% 直属提成</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- SECTION C: 开通机制 -->
        <div class="space-y-4">
          <div class="flex items-center gap-2 pb-1 border-b border-gray-200">
            <span class="w-1 h-4.5 bg-brand-primary rounded-full"></span>
            <h3 class="text-[14.5px] font-black text-brand-ink-strong font-serif">三、开通机制</h3>
          </div>

          <div class="bg-white rounded-2xl p-4.5 border border-gray-150/60 shadow-xs space-y-3">
            <div class="flex items-center gap-1.5 text-brand-primary">
              <Award :size="16" />
              <h4 class="text-[13px] font-bold">1. 开通审核</h4>
            </div>

            <p class="text-[11.5px] text-brand-secondary leading-relaxed">
              任何注册用户仅需在个人后台点击<span class="font-bold text-brand-ink-strong">「申请成为推广大使」</span>，签署推广协议后，由客服审核开通（非自动开通）。
            </p>
            <div class="p-2.5 rounded-lg bg-slate-50 text-[11px] text-brand-ink-strong font-medium flex justify-between items-center">
              <span>开通结果：</span>
              <span class="text-emerald-600 font-extrabold text-[12.5px]">审核通过后解锁对应身份权益与结算能力</span>
            </div>
          </div>
        </div>

        <!-- SECTION D: 创始合伙人战略共建 -->
        <div class="space-y-4">
          <div class="flex items-center gap-2 pb-1 border-b border-gray-200">
            <span class="w-1 h-4.5 bg-brand-primary rounded-full"></span>
            <h3 class="text-[14.5px] font-black text-brand-ink-strong font-serif">四、关于创始合伙人战略共建</h3>
          </div>

          <p class="text-[12px] text-brand-secondary leading-relaxed font-sans">
            创始合伙人由公司统一招商签约；合同年费固定为 <strong class="text-brand-ink-strong">29,800 元/年</strong>，详情请咨询客服。
          </p>

          <div class="bg-amber-500/[0.03] rounded-xl p-3 border border-amber-500/10 space-y-2 text-[11px] text-brand-secondary font-sans">
            <div class="flex justify-between font-bold text-brand-ink-strong">
              <span>🛡️ 首批抢先专享：</span>
              <span class="text-red-650 text-red-600 font-black">名额有限期权确权</span>
            </div>
            <p class="leading-relaxed mt-1 border-t border-dashed border-amber-500/15 pt-2">
              首批50名专享公司 <strong>5% 的合规期权池份额</strong>，后续均走正式的 <strong>工商变更登记确权</strong>，确保投资合伙人依法依规享有核心业务分润红利。
            </p>
          </div>

          <!-- Top 6 Privileges List -->
          <div class="bg-white rounded-2xl p-4.5 border border-gray-150/60 shadow-xs space-y-3.5">
            <h4 class="text-[13px] font-black text-brand-ink-strong font-serif mb-1">创始合伙人享有六大顶级专享权</h4>
            
            <div class="space-y-4">
              <!-- Item 1 -->
              <div class="flex gap-2.5 items-start">
                <span class="w-5.5 h-5.5 rounded-full bg-slate-900 text-amber-300 text-[10.5px] font-black flex items-center justify-center shrink-0">1</span>
                <div>
                  <h5 class="text-[12.5px] font-extrabold text-brand-ink-strong leading-normal">自用账户在服务期间非商品免单</h5>
                  <p class="text-[11px] text-brand-secondary mt-0.5">合伙人自用账户在服务期间所有需要消耗积分的功能、课程均不消耗积分，积分兑换商品规则与普通用户一致。</p>
                </div>
              </div>

              <!-- Item 2 -->
              <div class="flex gap-2.5 items-start">
                <span class="w-5.5 h-5.5 rounded-full bg-slate-900 text-amber-300 text-[10.5px] font-black flex items-center justify-center shrink-0">2</span>
                <div>
                  <h5 class="text-[12.5px] font-extrabold text-brand-ink-strong leading-normal">55% 直属充值现金直返</h5>
                  <p class="text-[11px] text-brand-secondary mt-0.5 leading-relaxed">
                    直接推荐的下属人脉在系统产生的所有消费，一律无条件给予 <strong>55% 现金返还</strong>，推广订单完成后按规则结算至推广余额。
                  </p>
                </div>
              </div>

              <!-- Item 3 -->
              <div class="flex gap-2.5 items-start">
                <span class="w-5.5 h-5.5 rounded-full bg-slate-900 text-amber-300 text-[10.5px] font-black flex items-center justify-center shrink-0">3</span>
                <div>
                  <h5 class="text-[12.5px] font-extrabold text-brand-ink-strong leading-normal">工商确权的期权分红红利</h5>
                  <p class="text-[11px] text-brand-secondary mt-0.5 leading-relaxed">
                    作为核心业务伙伴，依法登记期权份额，并走正式的 <strong>工商变更与确权登记</strong> 流程，依照公司章程及红利规定享受持续稳定的年度持股分红派息。
                  </p>
                </div>
              </div>

              <!-- Item 4 -->
              <div class="flex gap-2.5 items-start">
                <span class="w-5.5 h-5.5 rounded-full bg-slate-900 text-amber-300 text-[10.5px] font-black flex items-center justify-center shrink-0">4</span>
                <div>
                  <h5 class="text-[12.5px] font-extrabold text-brand-ink-strong leading-normal">15% 团队管理业绩提额</h5>
                  <p class="text-[11px] text-brand-secondary mt-0.5 leading-relaxed">
                    合伙人作为团队管理人，统一享受其名下管理的所有推广大使产生的推广充值流水总额 <strong>15% 的管理提成</strong>。
                  </p>
                </div>
              </div>

              <!-- Item 5 -->
              <div class="flex gap-2.5 items-start">
                <span class="w-5.5 h-5.5 rounded-full bg-slate-900 text-amber-300 text-[10.5px] font-black flex items-center justify-center shrink-0">5</span>
                <div>
                  <h5 class="text-[12.5px] font-extrabold text-brand-ink-strong leading-normal">合伙人推荐服务返点 55%</h5>
                  <p class="text-[11px] text-brand-secondary mt-0.5">
                    成功推荐同行或下属开通加盟创始合伙人生态卡，立刻获取缴费费用的 <strong>55% 服务推荐返金（即单笔直返 16,390 元）</strong>，帮助合作人更快回收投入。
                  </p>
                </div>
              </div>

              <!-- Item 6: Team Performance & Bonus Mechanism -->
              <div class="flex gap-2.5 items-start">
                <span class="w-5.5 h-5.5 rounded-full bg-slate-900 text-amber-300 text-[10.5px] font-black flex items-center justify-center shrink-0">6</span>
                <div class="w-full">
                  <h5 class="text-[12.5px] font-extrabold text-brand-ink-strong leading-normal flex items-center justify-between">
                    <span>团队业绩及奖金发放机制</span>
                    <span class="text-[9.5px] bg-indigo-50 border border-indigo-100 text-indigo-700 px-1.5 py-0.5 rounded-md font-bold font-sans">结算方案</span>
                  </h5>
                  <p class="text-[11px] text-brand-secondary mt-0.5 leading-relaxed">
                    团队奖金发放基于创始合伙人所管理的推广团队旗下各类推广大使产生的业绩总和进行计算。
                  </p>

                  <div class="mt-3 text-brand-secondary rounded-xl border border-indigo-100/50 bg-indigo-50/[0.12] p-3.5 space-y-4 font-sans text-[11.5px]">
                    <div class="space-y-1.5">
                      <div class="text-[11.5px] text-indigo-950 font-extrabold flex items-center gap-1.5">
                        <span class="w-1.5 h-3 bg-indigo-600 rounded-full"></span>
                        <span>公式一：业绩总额计算</span>
                      </div>
                      <div class="bg-white px-3 py-2.5 rounded-xl border border-indigo-100/60 shadow-xs">
                        <div class="font-mono text-[10px] text-indigo-950 font-black leading-tight break-all">
                          业绩总额 = 推广大使业绩 + VIP 推广大使业绩 + SVIP 推广大使业绩 + 直属推荐人脉消费额
                        </div>
                        <div class="text-[9.5px] text-slate-500 border-t border-dashed border-indigo-50 mt-2.5 pt-2 leading-relaxed">
                          📌 <span class="font-extrabold text-amber-800">备注：</span>直属推荐人脉消费额同样计入团队业绩总额。
                        </div>
                      </div>
                    </div>

                    <div class="space-y-1.5">
                      <div class="text-[11.5px] text-indigo-950 font-extrabold flex items-center gap-1.5">
                        <span class="w-1.5 h-3 bg-indigo-600 rounded-full"></span>
                        <span>公式二：奖金总额计算</span>
                      </div>
                      <div class="bg-white px-3 py-2.5 rounded-xl border border-indigo-100/60 shadow-xs">
                        <div class="font-mono text-[10px] text-indigo-950 font-black leading-normal break-all">
                          奖金总额 = 推广大使充值 × 15% + VIP 推广大使充值 × 10% + SVIP 推广大使充值 × 5% + 直属推荐人脉消费额 × 5%
                        </div>
                      </div>
                    </div>

                    <div class="space-y-1.5">
                      <div class="text-[11.5px] text-indigo-950 font-extrabold flex items-center gap-1.5">
                        <span class="w-1.5 h-3 bg-indigo-600 rounded-full"></span>
                        <span>公式三：个人奖金分配</span>
                      </div>
                      <div class="bg-white px-3 py-2.5 rounded-xl border border-indigo-100/60 shadow-xs">
                        <div class="font-mono text-[10px] text-indigo-950 font-black leading-normal">
                          个人奖金 =（个人推广充值金额 / 业绩总额）× 奖金总额
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Dynamic Sandbox calculator -->
        <div class="bg-gradient-to-br from-slate-900 to-slate-950 text-white rounded-2xl p-4.5 border border-amber-500/25 shadow-sm space-y-4">
          
          <!-- Header and Tab Selection -->
          <div class="flex flex-col gap-2 border-b border-white/10 pb-3">
            <div class="flex justify-between items-center">
              <div class="flex items-center gap-1.5">
                <Calculator :size="15" class="text-amber-400" />
                <span class="text-[13.5px] font-serif font-black text-amber-500">分成收益计算器</span>
              </div>
              <span class="text-[8.5px] font-mono text-slate-400">年化预估测算系统</span>
            </div>
            
            <!-- Tabs for Version selection -->
            <div class="grid grid-cols-2 gap-1 bg-black/40 p-1 rounded-xl border border-white/5 text-[11px] font-bold mt-1">
              <button 
                @click="calcVersion = 'partner'"
                :class="calcVersion === 'partner' ? 'bg-amber-500 text-slate-950 font-black shadow-xs' : 'text-slate-300 hover:text-white'"
                class="py-1.5 rounded-lg transition-all outline-none cursor-pointer"
              >
                💼 创始合伙人版
              </button>
              <button 
                @click="calcVersion = 'ambassador'"
                :class="calcVersion === 'ambassador' ? 'bg-indigo-600 text-white font-black shadow-xs' : 'text-slate-300 hover:text-white'"
                class="py-1.5 rounded-lg transition-all outline-none cursor-pointer"
              >
                📣 推广大使版
              </button>
            </div>
          </div>

          <!-- Content Panel A: Partner Version -->
          <div v-if="calcVersion === 'partner'" class="space-y-4 font-sans text-left">
            <p class="text-[11px] text-slate-300 leading-relaxed bg-white/5 p-2 rounded-lg border border-white/5">
              💡 <strong>公式</strong>：直属充值金额 × 15% + 旗下团队业绩总额 × 15% + 团队奖金。
            </p>

            <!-- Parameter 1: Direct users count -->
            <div class="space-y-1">
              <div class="flex justify-between text-[11px] text-slate-350">
                <span class="font-bold">1. 直属推荐人脉数：</span>
                <span class="text-amber-400 font-extrabold font-mono">{{ directUsersCount }} 人</span>
              </div>
              <div class="flex items-center gap-2">
                <input 
                  type="range" v-model.number="directUsersCount" min="2" max="500" step="1" 
                  class="flex-1 accent-amber-500 h-1 bg-slate-800 rounded-lg outline-none cursor-pointer"
                />
                <span class="text-[9px] font-mono text-slate-400 bg-black/25 px-1.5 py-0.5 rounded w-10 text-center">{{ directUsersCount }}人</span>
              </div>
            </div>

            <!-- Parameter 2: Avg annual spend -->
            <div class="space-y-1">
              <div class="flex justify-between text-[11px] text-slate-350">
                <span class="font-bold">2. 直属推荐人脉消费额：</span>
                <span class="text-amber-400 font-extrabold font-mono">{{ avgAnnualDirectSpend }} 元/年</span>
              </div>
              <div class="flex items-center gap-2">
                <input 
                  type="range" v-model.number="avgAnnualDirectSpend" min="50" max="2500" step="10" 
                  class="flex-1 accent-amber-500 h-1 bg-slate-800 rounded-lg outline-none cursor-pointer"
                />
                <span class="text-[9px] font-mono text-slate-400 bg-black/25 px-1.5 py-0.5 rounded w-11 text-center font-bold">{{ avgAnnualDirectSpend }}元</span>
              </div>
            </div>

            <!-- Parameter 3: Normal ambassador performance -->
            <div class="space-y-1">
              <div class="flex justify-between text-[11px] text-slate-350">
                <span class="font-bold">3. 旗下推广大使推广充值：</span>
                <span class="text-amber-400 font-extrabold font-mono">{{ normalAmbassadorPerformance }} 元/年</span>
              </div>
              <div class="flex items-center gap-2">
                <input
                  type="range" v-model.number="normalAmbassadorPerformance" min="0" max="200000" step="1000"
                  class="flex-1 accent-amber-500 h-1 bg-slate-800 rounded-lg outline-none cursor-pointer"
                />
                <span class="text-[9px] font-mono text-slate-400 bg-black/25 px-1.5 py-0.5 rounded w-14 text-center font-bold">{{ normalAmbassadorPerformance }}元</span>
              </div>
            </div>

            <!-- Parameter 4: VIP ambassador performance -->
            <div class="space-y-1">
              <div class="flex justify-between text-[11px] text-slate-350">
                <span class="font-bold">4. 旗下 VIP 推广大使推广充值：</span>
                <span class="text-amber-400 font-extrabold font-mono">{{ vipAmbassadorPerformance }} 元/年</span>
              </div>
              <div class="flex items-center gap-2">
                <input
                  type="range" v-model.number="vipAmbassadorPerformance" min="0" max="200000" step="1000"
                  class="flex-1 accent-amber-500 h-1 bg-slate-800 rounded-lg outline-none cursor-pointer"
                />
                <span class="text-[9px] font-mono text-slate-400 bg-black/25 px-1.5 py-0.5 rounded w-14 text-center font-bold">{{ vipAmbassadorPerformance }}元</span>
              </div>
            </div>

            <!-- Parameter 5: SVIP ambassador performance -->
            <div class="space-y-1">
              <div class="flex justify-between text-[11px] text-slate-350">
                <span class="font-bold">5. 旗下 SVIP 推广大使推广充值：</span>
                <span class="text-amber-400 font-extrabold font-mono">{{ svipAmbassadorPerformance }} 元/年</span>
              </div>
              <div class="flex items-center gap-2">
                <input
                  type="range" v-model.number="svipAmbassadorPerformance" min="0" max="200000" step="1000"
                  class="flex-1 accent-amber-500 h-1 bg-slate-800 rounded-lg outline-none cursor-pointer"
                />
                <span class="text-[9px] font-mono text-slate-400 bg-black/25 px-1.5 py-0.5 rounded w-14 text-center font-bold">{{ svipAmbassadorPerformance }}元</span>
              </div>
              <p class="text-[9.5px] text-slate-400 leading-snug">
                合伙人的个人直推金额 {{ formatCurrency(directAnnualPerformance) }} 同步计入 SVIP 推广大使推广充值业绩。
              </p>
            </div>

            <!-- Calculations Breakdown for Partner -->
            <div class="bg-black/35 p-3.5 rounded-xl border border-white/5 grid grid-cols-2 gap-3 text-center mt-3">
              <div class="border-r border-white/10 pr-1">
                <span class="text-[8.5px] text-slate-400 block uppercase">直属充值收益 (15%)</span>
                <span class="text-[13.5px] font-extrabold text-emerald-400 block mt-1 font-mono">
                  {{ formatCurrency(partnerDirectAnnualEarn) }} <span class="text-[9px] text-slate-400">/年</span>
                </span>
              </div>
              <div class="pl-1">
                <span class="text-[8.5px] text-slate-400 block uppercase">团队管理提成 (15%)</span>
                <span class="text-[13.5px] font-extrabold text-emerald-400 block mt-1 font-mono">
                  {{ formatCurrency(partnerTeamManagementAnnualEarn) }} <span class="text-[9px] text-slate-400">/年</span>
                </span>
              </div>
              <div class="col-span-2 grid grid-cols-2 gap-2 pt-2 border-t border-white/10">
                <div>
                  <span class="text-[8.5px] text-slate-400 block uppercase">个人团队奖金分成</span>
                  <span class="text-[12px] font-extrabold text-amber-200 block mt-1 font-mono">{{ formatCurrency(partnerPersonalTeamBonus) }}</span>
                </div>
                <div>
                  <span class="text-[8.5px] text-slate-400 block uppercase">团队奖金总额</span>
                  <span class="text-[12px] font-extrabold text-amber-200 block mt-1 font-mono">{{ formatCurrency(teamBonusTotal) }}</span>
                </div>
              </div>
              <div class="col-span-2 pt-2 border-t border-white/10">
                <span class="text-[8.5px] text-slate-400 block uppercase">团队业绩总额</span>
                <span class="text-[12px] font-extrabold text-amber-200 block mt-1 font-mono">{{ formatCurrency(teamPerformanceTotal) }}</span>
              </div>
            </div>

            <!-- Cumulative Total Annual Output -->
            <div class="text-center pt-3 border-t border-white/10 mt-1">
              <p class="text-[9px] text-slate-450 uppercase tracking-widest leading-none font-bold">合伙人预计被动年化收入</p>
              <p class="text-[25px] font-black text-amber-300 tracking-tight mt-1 font-serif">
                {{ formatCurrency(partnerTotalAnnualEarn) }} <span class="text-xs font-sans font-normal text-slate-300">/ 年</span>
              </p>
              <p class="text-[8.5px] text-slate-400 mt-1 leading-normal text-center max-w-[90%] mx-auto">
                ※ 已包含直属收益、团队管理收益与个人团队奖金分成。
              </p>
            </div>
          </div>

          <!-- Content Panel B: Ambassador Version -->
          <div v-else class="space-y-4 font-sans text-left">
            <p class="text-[11px] text-indigo-200 bg-slate-850 p-2.5 rounded-lg border border-indigo-500/10 leading-relaxed bg-white/5">
              💡 <strong>公式</strong>：(直属推荐人脉数 × 平均直推年均消费额) × 大使层级提成比例。
            </p>

            <!-- Level selection small tags: 3 small tags -->
            <div class="space-y-1.5">
              <label class="text-[10.5px] text-slate-350 font-bold">已选推广大使等级比例：</label>
              <div class="grid grid-cols-3 gap-1.5 mt-1 font-sans text-[10.5px] font-extrabold">
                <button 
                  @click="selectedAmbassadorTier = 'normal'"
                  :class="selectedAmbassadorTier === 'normal' ? 'bg-indigo-600 text-white border-transparent' : 'bg-slate-800 text-slate-300 border-white/5 hover:bg-slate-750'"
                  class="py-1.5 rounded-lg border text-center transition-all cursor-pointer outline-none font-sans"
                >
                  普通 (10%)
                </button>
                <button 
                  @click="selectedAmbassadorTier = 'vip'"
                  :class="selectedAmbassadorTier === 'vip' ? 'bg-indigo-600 text-white border-transparent' : 'bg-slate-800 text-slate-300 border-white/5 hover:bg-slate-750'"
                  class="py-1.5 rounded-lg border text-center transition-all cursor-pointer outline-none font-sans"
                >
                  VIP (25%)
                </button>
                <button 
                  @click="selectedAmbassadorTier = 'svip'"
                  :class="selectedAmbassadorTier === 'svip' ? 'bg-indigo-600 text-white border-transparent' : 'bg-slate-800 text-slate-300 border-white/5 hover:bg-slate-750'"
                  class="py-1.5 rounded-lg border text-center transition-all cursor-pointer outline-none font-sans"
                >
                  SVIP (40%)
                </button>
              </div>
            </div>

            <!-- Parameter 1: Direct users count -->
            <div class="space-y-1">
              <div class="flex justify-between text-[11px] text-slate-300">
                <span class="font-bold">直属推荐人脉数：</span>
                <span class="text-indigo-350 text-indigo-400 font-extrabold font-mono">{{ directUsersCount }} 人</span>
              </div>
              <div class="flex items-center gap-2">
                <input 
                  type="range" v-model.number="directUsersCount" min="2" max="500" step="1" 
                  class="flex-1 accent-indigo-500 h-1 bg-slate-800 rounded-lg outline-none cursor-pointer"
                />
                <span class="text-[9px] font-mono text-slate-400 bg-black/25 px-1.5 py-0.5 rounded w-10 text-center">{{ directUsersCount }}人</span>
              </div>
            </div>

            <!-- Parameter 2: Avg annual spend -->
            <div class="space-y-1">
              <div class="flex justify-between text-[11px] text-slate-300">
                <span class="font-bold">平均直推人脉年消费额：</span>
                <span class="text-indigo-350 text-indigo-400 font-extrabold font-mono">{{ avgAnnualDirectSpend }} 元/年</span>
              </div>
              <div class="flex items-center gap-2">
                <input 
                  type="range" v-model.number="avgAnnualDirectSpend" min="50" max="2500" step="10" 
                  class="flex-1 accent-indigo-500 h-1 bg-slate-800 rounded-lg outline-none cursor-pointer"
                />
                <span class="text-[9px] font-mono text-slate-400 bg-black/25 px-1.5 py-0.5 rounded w-11 text-center font-bold">{{ avgAnnualDirectSpend }}元</span>
              </div>
            </div>

            <!-- Cumulative Total for Ambassador -->
            <div class="text-center pt-3 border-t border-white/10 mt-3 bg-black/20 p-3 rounded-xl border border-white/5">
              <p class="text-[9px] text-slate-450 uppercase tracking-widest leading-none font-bold">大使预计被动年化收入</p>
              <p class="text-[25px] font-black text-indigo-400 tracking-tight mt-1 font-serif">
                {{ formatCurrency(ambassadorAnnualEarn) }} <span class="text-xs font-sans font-normal text-slate-300">/ 年</span>
              </p>
              <p class="text-[8.5px] text-slate-450 mt-1">
                （当前计算基于已选择提成比例：<strong class="text-indigo-300 font-bold font-mono">{{ tierRates[selectedAmbassadorTier] * 105 ? tierRates[selectedAmbassadorTier] * 100 : 0 }}%</strong>）
              </p>
            </div>
          </div>

        </div>
      </div>

    </div>

    <transition name="slide">
      <div
        v-if="showApplyPlaceholder"
        class="absolute inset-0 z-[140] bg-brand-paper flex flex-col text-left"
      >
        <header class="bg-white border-b border-gray-100 flex items-center justify-between px-4 py-3.5 sticky top-0 z-10 shadow-xs shrink-0">
          <button
            @click="showApplyPlaceholder = false"
            class="flex items-center gap-1 text-brand-secondary hover:text-brand-ink-strong transition-colors cursor-pointer outline-none text-[14px]"
          >
            <ArrowLeft :size="18" />
            <span class="font-semibold">返回</span>
          </button>
          <h2 class="font-serif font-black text-[15px] text-brand-ink-strong tracking-wide">
            申请加入
          </h2>
          <div class="w-12"></div>
        </header>

        <main class="flex-1 flex items-center justify-center px-6 text-center">
          <div class="space-y-2">
            <p class="font-serif text-[20px] font-black text-brand-ink-strong">申请加入页面待设计</p>
            <p class="font-sans text-[12px] text-brand-secondary leading-relaxed">
              这里先保留跳转占位，后续可替换为正式申请页面。
            </p>
          </div>
        </main>
      </div>
    </transition>

    <!-- Sticky H5 Actions Footer -->
    <div class="absolute bottom-0 inset-x-0 border-t border-gray-150/60 bg-white p-3.5 max-w-md mx-auto z-15 shadow-2xl shrink-0">
      <div class="grid grid-cols-3 gap-2 w-full">
        <button
          @click="emit('close')"
          class="px-2 py-2.5 bg-brand-paper hover:bg-gray-100 text-brand-ink text-[11px] font-extrabold rounded-lg outline-none cursor-pointer border border-gray-200"
        >
          返回个人中心
        </button>
        <button
          @click="handleContactSupport"
          class="px-2 py-2.5 bg-slate-900 border border-slate-800 text-amber-300 text-[11px] font-black rounded-lg outline-none cursor-pointer hover:bg-slate-800 shadow-sm"
        >
          联系客服
        </button>
        <button
          @click="handleApplyJoin"
          class="px-2 py-2.5 bg-slate-900 border border-slate-800 text-amber-300 text-[11px] font-black rounded-lg outline-none cursor-pointer hover:bg-slate-800 shadow-sm"
        >
          申请加入
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Disable native scrollbar styles inside nested modal previews */
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

.slide-enter-active, .slide-leave-active {
  transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.25s ease;
}

.slide-enter-from, .slide-leave-to {
  transform: translateY(100%);
  opacity: 0.95;
}
</style>
