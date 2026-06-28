<script setup lang="ts">
import { computed, nextTick, ref, onMounted, onUnmounted, watch } from 'vue';
import {
  AlertCircle, ArrowDown, Bot, CheckCircle2, ChevronRight, CornerDownLeft,
  HelpCircle, History, Loader2, MessageSquare, Play, Send, Sparkles, Square, Trash2, User, X
} from 'lucide-vue-next';
import { useEaseWiseApp } from '../../composables/useEaseWiseApp';
import { useVoicePlayback } from '../../composables/useVoicePlayback';
import type { AgentMessage, ChatSessionDetail } from '../../types/api';

const {
  state, isGuestUser, sendAgentChatMessage, createAgentChatSession,
  listAgentChatSessions, loadAgentChatSession, clearAgentChatSessions,
  requestRegisteredUser, showToast, openCustomerServiceModal, humanizeError
} = useEaseWiseApp();

const inputMessage = ref('');
const sending = ref(false);
const activeSessionId = ref<string | null>(null);
const showSessionList = ref(false);
const showSuggestionList = ref(true);

const chatContainerRef = ref<HTMLDivElement | null>(null);
const currentStreamingText = ref('');
const messagesList = ref<AgentMessage[]>([]);

const toastMsg = ref<string | null>(null);
function triggerToast(msg: string) {
  toastMsg.value = msg;
  setTimeout(() => { toastMsg.value = null; }, 2000);
}

const voice = useVoicePlayback({
  getAccessToken: () => state.accessToken,
  getVoiceConfig: () => (state.runtimeConfig?.modules as any)?.voice || (state.runtimeConfig?.modules as any)?.ai_agent?.voice,
  showToast: (msg) => triggerToast(msg),
});

const sessions = computed(() => state.chatSessions || []);
const activeSession = computed(() => sessions.value.find(s => s.id === activeSessionId.value) || null);
const userPoints = computed(() => state.points?.balance ?? 0);
const isRegistered = computed(() => !!state.accessToken);

const presetSuggestions = [
  { text: '如何利用奇门卦理选择最佳合伙人？', title: '奇门合伙' },
  { text: '我的手机号中出现“天蓬门迫”意味着什么？', title: '手机天蓬' },
  { text: '日干身弱且财旺的命局，今年如何合理修持？', title: '身弱财旺' },
  { text: '在梅花易数中，体卦受用卦克制该如何偏转运势？', title: '梅花偏转' },
];

onMounted(async () => {
  if (isRegistered.value) {
    try {
      const list = await listAgentChatSessions();
      if (list.length > 0) {
        activeSessionId.value = list[0].id;
        await handleLoadSession(list[0].id);
      } else {
        await handleCreateSession();
      }
    } catch (e) {
      console.error('Failed listing chat sessions', e);
    }
  } else {
    // Guest initial placeholder message
    messagesList.value = [
      {
        id: 'welcome',
        role: 'assistant',
        content: '您好！我是 EaseWise「易如反掌」玄学AI助理。您可以向我咨询关于奇门遁甲、四柱八字或梅花起卦中的盘局暗示，或者提出生活与事业抉择中的困惑，我会以经典古法卦理解构并给出策略。',
        created_at: new Date().toISOString()
      }
    ];
  }
});

onUnmounted(() => {
  voice.stop();
});

function scrollToBottom() {
  nextTick(() => {
    if (chatContainerRef.value) {
      chatContainerRef.value.scrollTop = chatContainerRef.value.scrollHeight;
    }
  });
}

async function handleCreateSession() {
  const authed = await requestRegisteredUser('发起新会话');
  if (!authed) return;

  try {
    const session = await createAgentChatSession('新决策咨询会话');
    activeSessionId.value = session.id;
    messagesList.value = session.messages || [];
    showSessionList.value = false;
    showSuggestionList.value = messagesList.value.length === 0;
    scrollToBottom();
  } catch (err: any) {
    triggerToast('创建新会话失败');
  }
}

async function handleLoadSession(sessionId: string) {
  try {
    const detail = await loadAgentChatSession(sessionId);
    activeSessionId.value = detail.id;
    messagesList.value = detail.messages || [];
    showSessionList.value = false;
    showSuggestionList.value = messagesList.value.length === 0;
    scrollToBottom();
  } catch (err: any) {
    triggerToast('加载会话失败');
  }
}

async function handleClearSessions() {
  if (!isRegistered.value) return;
  try {
    await clearAgentChatSessions();
    activeSessionId.value = null;
    messagesList.value = [];
    showSuggestionList.value = true;
    triggerToast('会话历史已清空');
    await handleCreateSession();
  } catch (e) {
    triggerToast('清空会话失败');
  }
}

async function handleSendMessage(textToSend?: string) {
  const text = (textToSend || inputMessage.value).trim();
  if (!text) return;

  const authed = await requestRegisteredUser('AI 咨询对话');
  if (!authed) return;

  if (userPoints.value < 1) {
    openCustomerServiceModal('points_insufficient', `AI 助理对话扣费：需要 1 积分，当前 ${userPoints.value}`);
    triggerToast('对话积分不足，已为您调出客服兑换中心！');
    return;
  }

  if (!activeSessionId.value) {
    await handleCreateSession();
    if (!activeSessionId.value) return;
  }

  inputMessage.value = '';
  showSuggestionList.value = false;

  // Optimistic client addition
  messagesList.value.push({
    id: `temp-user-${Date.now()}`,
    role: 'user',
    content: text,
    created_at: new Date().toISOString()
  });
  scrollToBottom();

  sending.value = true;
  currentStreamingText.value = '';
  voice.stop();

  try {
    await sendAgentChatMessage(activeSessionId.value, text, {
      onChunk: (chunkText) => {
        currentStreamingText.value += chunkText;
        scrollToBottom();
      },
      onComplete: (completedSession) => {
        messagesList.value = completedSession.messages || [];
        currentStreamingText.value = '';
        sending.value = false;
        scrollToBottom();

        // Auto voice play back if configured
        if (voice.autoplayEnabled.value && messagesList.value.length > 0) {
          const lastMsg = messagesList.value[messagesList.value.length - 1];
          if (lastMsg.role === 'assistant') {
            void voice.speakMessage(completedSession.id, lastMsg);
          }
        }
      },
      onError: (err) => {
        triggerToast(humanizeError(err) || '解答通道暂有波动，请稍后再试');
        sending.value = false;
      }
    });
  } catch (err: any) {
    triggerToast(humanizeError(err) || '网络异常，发送失败');
    sending.value = false;
  }
}

function speakSingleMessage(msg: AgentMessage) {
  if (!activeSessionId.value) return;
  const key = `message:${activeSessionId.value}:${msg.id}`;
  if (voice.currentKey.value === key) {
    voice.stop();
  } else {
    void voice.speakMessage(activeSessionId.value, msg);
  }
}
</script>

<template>
  <div class="pt-4 pb-32 max-w-md mx-auto px-margin-mobile flex flex-col h-[calc(100vh-64px)] overflow-hidden relative text-left">

    <transition name="fade">
      <div v-if="toastMsg" class="fixed top-4 left-1/2 -translate-x-1/2 z-[110] bg-brand-ink-strong text-white px-4 py-2.5 rounded-full font-sans text-[12.5px] shadow-lg font-medium flex items-center gap-2 max-w-[85%] whitespace-nowrap">
        <Sparkles :size="14" class="text-brand-accent shrink-0" />
        <span>{{ toastMsg }}</span>
      </div>
    </transition>

    <!-- Top session control header bar -->
    <div class="flex justify-between items-center mb-3 select-none">
      <div class="flex items-center gap-2">
        <button
          v-if="isRegistered"
          @click="showSessionList = !showSessionList"
          class="text-brand-ink-strong hover:text-brand-primary font-sans text-[12px] font-extrabold flex items-center gap-1 cursor-pointer border-none bg-transparent outline-none p-1.5 rounded-xl bg-white border border-gray-100 shadow-sm"
        >
          <History :size="14" />
          <span>{{ showSessionList ? '返回对话大厅' : '历史会话' }}</span>
        </button>
      </div>

      <div class="flex items-center gap-2">
        <button
          @click="voice.setEnabled(!voice.enabled.value)"
          class="px-2.5 py-1.5 rounded-xl text-[10.5px] font-extrabold cursor-pointer border transition-colors outline-none flex items-center gap-1"
          :class="voice.enabled.value
            ? 'bg-brand-primary/10 border-brand-primary/20 text-brand-primary'
            : 'bg-zinc-50 border-gray-150 text-zinc-400 hover:bg-zinc-100'"
        >
          <span>语音朗读: {{ voice.enabled.value ? '开' : '关' }}</span>
        </button>
        <button
          @click="voice.setAutoplayEnabled(!voice.autoplayEnabled.value)"
          class="px-2.5 py-1.5 rounded-xl text-[10.5px] font-extrabold cursor-pointer border transition-colors outline-none flex items-center gap-1"
          :class="voice.autoplayEnabled.value
            ? 'bg-emerald-50 border-emerald-200 text-emerald-700'
            : 'bg-zinc-50 border-gray-150 text-zinc-400 hover:bg-zinc-100'"
        >
          <span>自动播报: {{ voice.autoplayEnabled.value ? '开' : '关' }}</span>
        </button>
      </div>
    </div>

    <!-- MAIN CHAT CONTAINER PANEL -->
    <div class="flex-1 overflow-y-auto no-scrollbar rounded-2xl border border-brand-paper shadow-inner bg-white/70 p-4 mb-3 flex flex-col gap-4 relative">

      <!-- SESSIONS DRAWER -->
      <transition name="slide-down">
        <div v-if="showSessionList" class="absolute inset-0 z-30 bg-white p-4 overflow-y-auto flex flex-col gap-3">
          <div class="flex justify-between items-center border-b border-gray-100 pb-2.5">
            <h3 class="font-serif text-[14px] font-black text-brand-ink-strong">会话历史列表</h3>
            <button @click="handleClearSessions" class="text-red-500 hover:text-red-600 text-xs font-bold flex items-center gap-1 cursor-pointer border-none bg-transparent outline-none">
              <Trash2 :size="12" />
              <span>清空所有历史</span>
            </button>
          </div>

          <div v-if="sessions.length === 0" class="py-12 text-center text-zinc-400 font-sans text-xs">
            暂无历史会话，点击下方按钮新建会话。
          </div>
          <div v-else class="space-y-2 flex-1">
            <button
              v-for="s in sessions"
              :key="s.id"
              @click="handleLoadSession(s.id)"
              class="w-full bg-brand-paper/40 hover:bg-brand-paper/80 border border-gray-100 rounded-xl p-3 text-left flex justify-between items-center transition-all cursor-pointer outline-none"
              :class="s.id === activeSessionId ? 'border-brand-primary bg-brand-primary/[0.02]' : ''"
            >
              <div class="min-w-0 flex-1">
                <span class="font-sans text-[12.5px] font-extrabold text-brand-ink-strong block truncate">{{ s.title }}</span>
                <span class="text-[10px] text-brand-secondary/80 mt-1 block">更新于：{{ new Date(s.updated_at).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' }) }}</span>
              </div>
              <ChevronRight :size="14" class="text-zinc-300" />
            </button>
          </div>

          <button @click="handleCreateSession" class="w-full h-11 bg-brand-primary text-white font-sans text-xs font-bold rounded-xl flex items-center justify-center gap-1 border-none shadow-sm cursor-pointer outline-none mt-auto">
            <span>发起新会话</span>
          </button>
        </div>
      </transition>

      <div ref="chatContainerRef" class="flex-1 overflow-y-auto no-scrollbar flex flex-col gap-4">
        <div
          v-for="msg in messagesList"
          :key="msg.id"
          class="flex items-start gap-2.5"
          :class="msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'"
        >
          <!-- Avatar icon -->
          <div class="w-8 h-8 rounded-xl flex items-center justify-center shrink-0 border select-none"
               :class="msg.role === 'user'
                 ? 'bg-brand-primary/10 border-brand-primary/20 text-brand-primary'
                 : 'bg-zinc-50 border-gray-200 text-zinc-600'">
            <User v-if="msg.role === 'user'" :size="15" />
            <Bot v-else :size="15" />
          </div>

          <div class="flex flex-col max-w-[80%] gap-1">
            <div
              class="rounded-2xl p-3.5 text-[12.5px] leading-relaxed relative whitespace-pre-wrap select-text font-medium"
              :class="msg.role === 'user'
                ? 'bg-brand-primary text-white rounded-tr-none'
                : 'bg-[#F2F4F7] text-brand-ink-strong rounded-tl-none border border-gray-100'"
            >
              <p>{{ msg.content }}</p>

              <!-- Speak controls for assistant messages -->
              <div
                v-if="msg.role === 'assistant' && msg.id !== 'welcome'"
                class="mt-2.5 pt-2 border-t border-gray-200/50 flex justify-end select-none"
              >
                <button
                  @click="speakSingleMessage(msg)"
                  class="px-2.5 py-1 bg-white border border-gray-200 rounded-lg text-brand-primary text-[10px] font-bold cursor-pointer transition-all active:scale-95 flex items-center gap-1 shadow-xs outline-none"
                >
                  <span v-if="voice.currentKey.value === `message:${activeSessionId}:${msg.id}`">暂停</span>
                  <span v-else>播报</span>
                  <Square v-if="voice.currentKey.value === `message:${activeSessionId}:${msg.id}`" :size="9" />
                  <Play v-else :size="9" />
                </button>
              </div>
            </div>
            <span class="text-[9px] text-zinc-400 mt-0.5" :class="msg.role === 'user' ? 'text-right' : 'text-left'">
              {{ new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }}
            </span>
          </div>
        </div>

        <!-- STREAMING CHUNK PLACEHOLDER -->
        <div v-if="currentStreamingText" class="flex items-start gap-2.5 flex-row">
          <div class="w-8 h-8 rounded-xl flex items-center justify-center shrink-0 border bg-zinc-50 border-gray-200 text-zinc-600 select-none">
            <Bot :size="15" />
          </div>
          <div class="flex flex-col max-w-[80%] gap-1">
            <div class="rounded-2xl p-3.5 text-[12.5px] leading-relaxed bg-[#F2F4F7] text-brand-ink-strong rounded-tl-none border border-gray-100 whitespace-pre-wrap select-text font-medium">
              <span>{{ currentStreamingText }}</span>
              <span class="inline-block w-1.5 h-3 bg-brand-primary animate-pulse ml-0.5"></span>
            </div>
          </div>
        </div>
      </div>

      <!-- Suggestion pills -->
      <div v-if="showSuggestionList" class="border-t border-gray-100 pt-3 flex flex-col gap-2 z-10">
        <span class="text-[10px] text-brand-secondary font-extrabold uppercase tracking-wider block">常见咨询入口</span>
        <div class="grid grid-cols-2 gap-2">
          <button
            v-for="sug in presetSuggestions"
            :key="sug.text"
            @click="handleSendMessage(sug.text)"
            class="bg-brand-paper/60 hover:bg-brand-paper border border-gray-100 rounded-xl p-2.5 text-left transition-colors cursor-pointer outline-none flex flex-col gap-1"
          >
            <span class="font-serif text-[11.5px] font-black text-brand-primary-strong leading-none">{{ sug.title }}</span>
            <span class="font-sans text-[9.5px] text-brand-secondary/80 truncate leading-tight pr-1 mt-1">{{ sug.text }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Input text box -->
    <div class="relative flex items-center select-none bg-white border border-gray-150 rounded-2xl focus-within:border-brand-primary transition-all p-1.5 shadow-sm">
      <input
        v-model="inputMessage"
        type="text"
        placeholder="输入您在学业、事业或情感中的决策困惑..."
        class="w-full bg-transparent border-none text-[12px] text-brand-ink-strong py-2 px-3 outline-none placeholder-gray-400 font-sans"
        @keyup.enter="handleSendMessage()"
        :disabled="sending"
      />
      <button
        @click="handleSendMessage()"
        :disabled="sending || !inputMessage.trim()"
        class="w-10 h-10 rounded-xl bg-brand-primary text-white flex items-center justify-center cursor-pointer hover:bg-brand-primary/95 transition-all outline-none border-none shrink-0 disabled:opacity-40"
      >
        <Loader2 v-if="sending" class="animate-spin" :size="15" />
        <Send v-else :size="15" />
      </button>
    </div>

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

.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.no-scrollbar::-webkit-scrollbar {
  display: none;
}
</style>
