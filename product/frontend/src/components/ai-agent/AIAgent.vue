<script setup lang="ts">
import { computed, ref, onMounted, watch, nextTick } from 'vue';
import {
  Send, Mic, Bot, User, Trash2, Smartphone, AlertCircle, Sparkle
} from 'lucide-vue-next';
import { EASEWISE_STORAGE_KEYS } from '../../constants/storage';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';

interface Message {
  id: string;
  role: 'assistant' | 'user';
  content: string;
  source?: string;
  timestamp: string;
  chips?: string[];
}

const { bootstrapApp, isRegisteredUser, requestRegisteredUser } = useEaseWiseApp();
const isLoggedIn = computed(() => isRegisteredUser.value);
const input = ref('');
const messages = ref<Message[]>([]);
const chatScrollContainerRef = ref<HTMLDivElement | null>(null);

const scrollToBottom = () => {
  nextTick(() => {
    if (chatScrollContainerRef.value) {
      chatScrollContainerRef.value.scrollTo({
        top: chatScrollContainerRef.value.scrollHeight,
        behavior: 'smooth',
      });
    }
  });
};

const initDefaultMessages = () => {
  const initialText = '您好，我是您的「易如反掌」专属决策助手。今日值神为青龙守护，【丙戌年 癸巳月 己未日】，己未大溪水，宜心气沉稳行事。\n\n检测到您昨日对号码尾号 8829 的评测已经封存（综合评分: 85），目前该名格正处于“生门”繁茂兑宫位。您想深入探究下该号段的财源偏旺期、或者直接听听近期的行动指导吗？';
  const initMsg: Message = {
    id: '1',
    role: 'assistant',
    content: initialText,
    source: 'DeepSeek-R1 (大黄历规则融合版)',
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    chips: ['生门在这里代表什么？', '帮我解读手机号分析结论', '今天适合求财或签合同吗？']
  };
  messages.value = [initMsg];
};

const syncChat = () => {
  if (isLoggedIn.value) {
    const stored = localStorage.getItem(EASEWISE_STORAGE_KEYS.agentConversation);
    if (stored) {
      try {
        messages.value = JSON.parse(stored);
      } catch (e) {
        initDefaultMessages();
      }
    } else {
      initDefaultMessages();
    }
  } else {
    messages.value = [];
  }
};

watch(isLoggedIn, () => {
  syncChat();
}, { immediate: true });

watch(messages, (newVal) => {
  if (isLoggedIn.value && newVal.length > 0) {
    localStorage.setItem(EASEWISE_STORAGE_KEYS.agentConversation, JSON.stringify(newVal));
  }
  scrollToBottom();
}, { deep: true });

onMounted(() => {
  void bootstrapApp();
  syncChat();
  scrollToBottom();
});

const handleSend = (textToSend?: string) => {
  const query = (textToSend || input.value).trim();
  if (!query) return;

  const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const userMsg: Message = {
    id: Date.now().toString(),
    role: 'user',
    content: query,
    timestamp
  };

  messages.value.push(userMsg);
  input.value = '';

  // Simulated responses mapping
  setTimeout(() => {
    let replyContent = '';
    let source = '易如反掌·大数理模型';

    if (query.includes('生门') || query.includes('代表什么')) {
      replyContent = '在奇门遁甲中，“生门”属艮土之格，高悬于兑金位。这预示着“号里逢土金相生，连绵不断”。对你而言，近期适宜求谋固定财产、长线投资、撰写论文或者对长者行拜问。在壬申今日，申子三合引水，利于财富的吸入与沉淀。';
      source = 'DeepSeek-R1 (奇门命盘模块)';
    } else if (query.includes('解读') || query.includes('手机号')) {
      replyContent = '正在为您抓取【尾号 8829】的命理断案... 盘面正逢“青龙得位”良局，其主求财易得、长辈青睐。但针对壬申日气运，天蓬休门有暗引，需要小心偏财过于贪恋导致的对冲损耗。';
      source = '易如反掌·大数理模型 (号段微调)';
    } else if (query.includes('求财') || query.includes('合同')) {
      replyContent = '今日己未，值神青龙逢黄道吉。因你号中巽木得气，宜进行商务报告沟通与设计规划撰写。如果是涉及大额偏财风险投资，建议推迟1-2日再做重大转账决断，保持防线坚固。';
      source = '大黄历规则兜底算引';
    } else {
      replyContent = `已收到您的咨询：“${query}”。根据奇门今日中盘局势，己未日气场厚重。建议以稳守本职，防微杜渐为主，配合此号码所藏天任文昌星进行文案与学术进修，自然能迎刃而解。`;
    }

    const assistantMsg: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: replyContent,
      source,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      chips: ['我该如何具体开运？', '尾号生门是什么位置？', '有什么彭祖百忌需要小心？']
    };

    messages.value.push(assistantMsg);
  }, 1200);
};

const handleLogin = async () => {
  await requestRegisteredUser('智能体对话');
};

const handleClearChat = () => {
  if (window.confirm('您确定要清空与智能体的所有聊天记录吗？')) {
    localStorage.removeItem(EASEWISE_STORAGE_KEYS.agentConversation);
    initDefaultMessages();
  }
};

const quickQueries = [
  '帮我解读最近一条手机号评测内容',
  '今天适合办理什么求财事务？',
  '我目前面临难关，下一步如何趋吉避凶？'
];
</script>

<template>
  <div class="flex flex-col h-[calc(100dvh-82px)] md:h-[calc(100vh-82px)] max-w-md mx-auto w-full bg-brand-paper overflow-hidden overscroll-none">
    <transition name="fade" mode="out-in">
      <!-- State 1: Login Gate UI -->
      <div
        v-if="!isLoggedIn"
        key="login-gate"
        class="flex-1 px-margin-mobile flex flex-col items-center justify-center text-center space-y-6 pb-6"
      >
        <div class="w-16 h-16 rounded-full bg-brand-primary/10 flex items-center justify-center text-brand-primary border border-brand-primary/20">
          <Bot :size="34" />
        </div>

        <div class="space-y-2 max-w-[90%]">
          <h2 class="font-serif text-[20px] font-bold text-brand-ink-strong leading-tight">易如反掌 · 智能体决策助手</h2>
          <p class="font-sans text-[13px] text-brand-secondary leading-relaxed">
            为提供定制的奇门排盘和黄历沟通服务，智能体需要关联您的手机测算历史与资产。未登录状态无法启用连续对话功能。
          </p>
        </div>

        <div class="bg-white p-4 rounded-xl border border-gray-100 max-w-[95%] text-left space-y-2 flex items-start gap-2 font-sans text-[13px] text-brand-secondary">
          <AlertCircle :size="16" class="text-brand-primary shrink-0 mt-0.5" />
          <div>
            <span class="font-bold text-brand-ink-strong">安全声明: </span>
            <span>您的聊天内容、测算手机号完全处于安全加密沙盒中，外部小人难窥，仅用于给予高定制开运决策建议。</span>
          </div>
        </div>

        <button
          @click="handleLogin"
          class="w-full py-3.5 bg-brand-primary text-white rounded-xl font-sans text-[13px] font-bold shadow-sm hover:bg-brand-primary-strong active:scale-[0.98] transition-all cursor-pointer outline-none flex items-center justify-center gap-2"
        >
          <Smartphone :size="16" />
          <span>登录后开启智能体对话</span>
        </button>
      </div>

      <!-- State 2: Active chat view -->
      <div
        v-else
        key="chat-active"
        class="flex-grow flex flex-col min-h-0 overflow-hidden"
      >
        <!-- Top context card with copy button and clearing action -->
        <div class="px-margin-mobile pt-3 shrink-0 flex items-center justify-between gap-2">
          <div class="flex-1 bg-white p-3 rounded-xl border border-gray-100/80 flex items-start gap-2.5 shadow-sm">
            <div class="relative mt-0.5 shrink-0">
              <Sparkle :size="16" class="text-brand-gold-fixed animate-spin" style="animation-duration: 4s" fill="currentColor" />
              <span class="absolute -top-1 -right-1 block w-2 h-2 bg-green-500 border-2 border-white rounded-full"></span>
            </div>
            <p class="font-sans text-[11px] text-brand-secondary leading-relaxed font-semibold">
              智能体决策器：今日结合实时大黄历气运为您解读
            </p>
          </div>

          <button
            @click="handleClearChat"
            class="p-3 bg-white hover:bg-gray-50 text-brand-secondary hover:text-red-500 rounded-xl border border-gray-100 shadow-sm transition-all outline-none cursor-pointer"
            title="清空聊天记录"
          >
            <Trash2 :size="16" />
          </button>
        </div>

        <!-- Message logs area -->
        <div ref="chatScrollContainerRef" class="flex-1 min-h-0 overflow-y-auto overscroll-contain px-margin-mobile py-4 pb-4 flex flex-col gap-4.5 no-scrollbar">
          <div
            v-for="msg in messages"
            :key="msg.id"
            class="flex gap-2.5 max-w-[92%] items-start"
            :class="msg.role === 'assistant' ? 'self-start' : 'self-end flex-row-reverse'"
          >
            <!-- Avatar blob -->
            <div class="w-9 h-9 rounded-full flex items-center justify-center shrink-0"
                 :class="msg.role === 'assistant' ? 'bg-white border border-gray-100 text-brand-primary shadow-sm' : 'bg-brand-primary text-white shadow-sm'">
              <Bot v-if="msg.role === 'assistant'" :size="16" />
              <User v-else :size="16" />
            </div>

            <!-- Content wrapper -->
            <div class="flex flex-col gap-1 w-full text-left">
              <!-- Message bubble -->
              <div class="px-3.5 py-2.5 rounded-2xl border font-sans text-[13px] leading-relaxed shadow-sm"
                   :class="msg.role === 'assistant' ? 'bg-white border-gray-100/60 rounded-tl-none text-brand-ink-strong' : 'bg-brand-primary text-white border-transparent rounded-tr-none'">
                <p class="whitespace-pre-wrap">{{ msg.content }}</p>
              </div>

              <!-- Source tag & timestamp for scholarly trust -->
              <div class="flex items-center gap-2 px-1 font-mono text-[10px] text-brand-secondary/60"
                   :class="msg.role === 'assistant' ? 'justify-start' : 'justify-end'">
                <span v-if="msg.role === 'assistant' && msg.source" class="font-bold text-brand-primary bg-brand-primary/5 px-1 rounded-sm scale-90 select-none">
                  {{ msg.source }}
                </span>
                <span>{{ msg.timestamp }}</span>
              </div>

              <!-- Quick click chips appended directly to AI message for layout fluency -->
              <div v-if="msg.role === 'assistant' && msg.chips" class="flex flex-wrap gap-1.5 mt-2">
                <button
                  v-for="chip in msg.chips"
                  :key="chip"
                  @click="handleSend(chip)"
                  class="bg-brand-paper hover:bg-gray-100 text-brand-primary border border-gray-200/50 px-2.5 py-1 rounded-full font-sans text-[10px] font-bold transition-all outline-none shrink-0"
                >
                  {{ chip }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Bottom interaction space -->
        <div class="bg-brand-paper/95 backdrop-blur-sm border-t border-gray-100/80 shrink-0">
          <!-- Quick horizontal scrolling Queries -->
          <div class="px-margin-mobile py-2.5 overflow-x-auto no-scrollbar flex gap-2 w-full">
            <button
              v-for="q in quickQueries"
              :key="q"
              @click="handleSend(q)"
              class="whitespace-nowrap px-3 py-2 bg-white border border-gray-200 rounded-full font-sans text-[11px] text-brand-secondary font-bold hover:border-brand-primary transition-colors cursor-pointer outline-none shadow-sm"
            >
              {{ q }}
            </button>
          </div>

          <!-- Input Field -->
          <div class="px-4 pb-0 flex items-center gap-3">
            <div class="flex-1 bg-white p-1 rounded-2xl flex items-center gap-1.5 border border-gray-100 shadow-sm pr-3">
              <input
                class="bg-transparent border-none focus:ring-0 w-full pl-3 pr-1 py-2 font-sans text-[13px] text-brand-ink-strong outline-none placeholder-gray-400 font-medium"
                placeholder="请输入对起盘结论的追问..."
                type="text"
                v-model="input"
                @keydown.enter="handleSend()"
              />
              <Mic :size="18" class="text-brand-secondary/60 cursor-pointer hover:text-brand-primary shrink-0" />
            </div>
            <button
              @click="handleSend()"
              class="w-11 h-11 rounded-full bg-brand-primary flex items-center justify-center text-white active:scale-95 transition-transform shrink-0 outline-none shadow-md"
            >
              <Send :size="16" fill="currentColor" />
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
