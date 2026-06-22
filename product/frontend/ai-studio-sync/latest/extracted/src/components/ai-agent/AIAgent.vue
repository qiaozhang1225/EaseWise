<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue';
import { Send, Bot, User, Sparkles, Compass, HelpCircle, ArrowRight } from 'lucide-vue-next';
import { sendChatToAgent } from '../../lib/api';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

const { requestRegisteredUser } = useEaseWiseApp();

const messages = ref<ChatMessage[]>([
  {
    id: 'welcome',
    role: 'assistant',
    content: '尊驾好！吾乃「易如反掌玄学智能体」。深谙数字奇门相克生助气场，精通四柱八字调配中和之道。请问尊驾今日有何关于命盘、手机号神位，或五行运势的疑惑？'
  }
]);

const userInput = ref('');
const loading = ref(false);
const chatContainer = ref<HTMLElement | null>(null);

const suggestions = [
  "如何推演11位手机号生克吉凶？",
  "流年犯冲太岁如何用五行调衡？",
  "八字中日主甲木坐申，代表何意？",
  "我的财位该如何布局最合适？"
];

function scrollToBottom() {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
    }
  });
}

async function handleSendMessage(textToSend?: string) {
  const text = (textToSend || userInput.value).trim();
  if (!text || loading.value) return;

  // Let guests use, but request login on deep interaction if requested
  userInput.value = '';

  messages.value.push({
    id: `u_${Date.now()}`,
    role: 'user',
    content: text
  });
  scrollToBottom();

  loading.value = true;

  try {
    const apiHistory = messages.value
      .filter(m => m.id !== 'welcome')
      .slice(-6) // Send recent context
      .map(m => ({
        role: m.role === 'user' ? 'user' : 'model',
        content: m.content
      }));

    const response = await sendChatToAgent(text, apiHistory);

    messages.value.push({
      id: `a_${Date.now()}`,
      role: 'assistant',
      content: response.reply
    });
  } catch (error: any) {
    messages.value.push({
      id: `err_${Date.now()}`,
      role: 'assistant',
      content: '深表歉意，吾刚才掐指忽遇紫微星流。你可以稍等片刻，或添加客服获取详细算批！'
    });
  } finally {
    loading.value = false;
    scrollToBottom();
  }
}

onMounted(() => {
  scrollToBottom();
});
</script>

<template>
  <div class="pt-2 pb-20 max-w-md mx-auto px-margin-mobile flex flex-col h-[calc(100vh-60px)] text-left">
    <!-- Header visual -->
    <div class="bg-white rounded-2xl p-4 border border-brand-paper shadow-sm mb-4 flex items-center gap-3">
      <div class="w-12 h-12 rounded-full bg-brand-primary/10 flex items-center justify-center shrink-0">
        <Bot :size="24" class="text-brand-primary" />
      </div>
      <div>
        <h2 class="font-serif text-[17px] font-bold text-brand-ink-strong flex items-center gap-1.5">
          玄学命局 AI 智能体
          <span class="bg-brand-gold-fixed/15 text-brand-gold-fixed font-sans text-[9px] px-1.5 py-0.5 rounded font-bold uppercase tracking-wider scale-90">ONLINE</span>
        </h2>
        <p class="font-sans text-[11.5px] text-brand-secondary leading-normal mt-0.5">
          基于奇门遁甲、周易六爻、八字命理模型，为您提供极速推算。
        </p>
      </div>
    </div>

    <!-- Chat container area -->
    <div class="flex-1 bg-white rounded-2xl border border-brand-paper shadow-sm flex flex-col overflow-hidden mb-4">
      <div
        ref="chatContainer"
        class="flex-1 p-4 overflow-y-auto space-y-4 font-sans text-[13px] leading-relaxed select-text"
      >
        <div
          v-for="msg in messages"
          :key="msg.id"
          class="flex items-start gap-2 max-w-[90%]"
          :class="msg.role === 'user' ? 'ml-auto flex-row-reverse' : ''"
        >
          <!-- User vs Bot Avatar -->
          <div
            class="w-7 h-7 rounded-full flex items-center justify-center shrink-0 shadow-sm"
            :class="msg.role === 'user' ? 'bg-brand-primary text-white' : 'bg-brand-paper text-brand-ink-strong'"
          >
            <User v-if="msg.role === 'user'" :size="14" />
            <Bot v-else :size="14" class="text-brand-primary" />
          </div>

          <!-- Message bubble -->
          <div
            class="p-3 rounded-2xl relative"
            :class="msg.role === 'user'
              ? 'bg-brand-primary text-white rounded-tr-none'
              : 'bg-brand-paper/55 text-brand-ink border border-gray-100 rounded-tl-none'"
          >
            <div class="whitespace-pre-wrap select-text selection:bg-brand-primary/20">{{ msg.content }}</div>
          </div>
        </div>

        <!-- System Loading state -->
        <div v-if="loading" class="flex items-start gap-2 max-w-[80%]">
          <div class="w-7 h-7 rounded-full bg-brand-paper flex items-center justify-center shrink-0">
            <Bot :size="14" class="text-brand-primary animate-spin" />
          </div>
          <div class="bg-brand-paper/55 border border-gray-100 p-3 rounded-2xl rounded-tl-none flex items-center gap-2">
            <span class="w-1.5 h-1.5 rounded-full bg-brand-primary animate-bounce"></span>
            <span class="w-1.5 h-1.5 rounded-full bg-brand-primary animate-bounce delay-100"></span>
            <span class="w-1.5 h-1.5 rounded-full bg-brand-primary animate-bounce delay-200"></span>
            <span class="text-brand-secondary text-[11px] font-serif font-semibold ml-1">神机测算中...</span>
          </div>
        </div>
      </div>

      <!-- Quick recommendation blocks -->
      <div class="p-3 bg-brand-paper/20 border-t border-gray-50 text-left shrink-0">
        <span class="text-brand-secondary text-[10.5px] font-extrabold flex items-center gap-1 mb-2">
          <Sparkles :size="11" class="text-brand-gold-fixed" />
          <span>推荐问题（轻按快速发送）：</span>
        </span>
        <div class="flex flex-wrap gap-1.5 max-h-[110px] overflow-y-auto">
          <button
            v-for="s in suggestions"
            :key="s"
            @click="handleSendMessage(s)"
            :disabled="loading"
            class="bg-white border border-gray-150 rounded-xl px-2.5 py-1.5 text-brand-secondary font-medium text-[11px] cursor-pointer hover:border-brand-primary/50 transition-colors flex items-center gap-1 outline-none relative"
          >
            <span>{{ s }}</span>
            <ArrowRight :size="10" class="text-brand-secondary" />
          </button>
        </div>
      </div>
    </div>

    <!-- Input Box area -->
    <div class="bg-white rounded-2xl border border-brand-paper shadow-sm p-2 flex items-center gap-2 shrink-0">
      <input
        v-model="userInput"
        @keydown.enter="handleSendMessage()"
        type="text"
        placeholder="在这里输入您想咨询的玄学奥秘..."
        :disabled="loading"
        class="flex-1 bg-transparent px-3 py-2 border-none outline-none font-sans text-[13px] text-brand-ink-strong disabled:text-gray-400"
      />
      <button
        @click="handleSendMessage()"
        :disabled="!userInput.trim() || loading"
        class="w-9 h-9 rounded-xl bg-brand-primary text-white flex items-center justify-center hover:bg-brand-primary/90 active:scale-95 transition-all disabled:opacity-40 disabled:scale-100 cursor-pointer border-none shadow-sm"
      >
        <Send :size="15" />
      </button>
    </div>
  </div>
</template>

<style scoped>
.chat-container::-webkit-scrollbar {
  width: 4px;
}
.chat-container::-webkit-scrollbar-track {
  background: transparent;
}
.chat-container::-webkit-scrollbar-thumb {
  background-color: #e2e8f0;
  border-radius: 99px;
}
</style>
