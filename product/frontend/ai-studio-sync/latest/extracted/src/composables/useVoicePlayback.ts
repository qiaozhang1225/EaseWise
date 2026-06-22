import { computed, ref } from 'vue';
import { EASEWISE_STORAGE_KEYS } from '../constants/storage';
import { ApiError, createVoiceNarration, getApiBaseUrl } from '../lib/api';
import type { ReviewAspect, ReviewRecord, VoiceNarrationRequest, VoiceRuntimeConfigResponse } from '../types/api';

type VoicePlaybackStatus = 'idle' | 'loading' | 'playing' | 'error';

type SpeakOptions = {
  auto?: boolean;
};

export type VoiceSpeakResult = {
  started: boolean;
  completed: boolean;
  stopped?: boolean;
  error?: string;
};

type VoicePlaybackOptions = {
  getAccessToken: () => string | null;
  getVoiceConfig: () => VoiceRuntimeConfigResponse | null | undefined;
  showToast?: (message: string) => void;
};

const autoSpokenKeys = new Set<string>();
const SILENT_AUDIO_DATA_URL = 'data:audio/wav;base64,UklGRiYAAABXQVZFZm10IBAAAAABAAEAQB8AAIA+AAACABAAZGF0YQIAAAAAAA==';

export function useVoicePlayback(options: VoicePlaybackOptions) {
  const status = ref<VoicePlaybackStatus>('idle');
  const currentKey = ref<string | null>(null);
  const error = ref<string | null>(null);
  const primed = ref(false);
  const storedEnabled = ref(readStoredBoolean(EASEWISE_STORAGE_KEYS.voiceEnabled));
  const storedAutoplayEnabled = ref(readStoredBoolean(EASEWISE_STORAGE_KEYS.voiceAutoplayEnabled));
  let currentAudio: HTMLAudioElement | null = null;
  let unlockedAudio: HTMLAudioElement | null = null;
  let speechRunId = 0;
  let activeResolve: ((result: VoiceSpeakResult) => void) | null = null;

  const voiceConfig = computed(() => options.getVoiceConfig() ?? null);
  const enabled = computed(() => {
    if (voiceConfig.value?.enabled === false) {
      return false;
    }
    return storedEnabled.value ?? true;
  });
  const autoplayEnabled = computed(() => {
    if (!enabled.value) {
      return false;
    }
    return storedAutoplayEnabled.value ?? voiceConfig.value?.autoplay_default_enabled ?? true;
  });
  const browserSpeechSupported = computed(() => typeof window !== 'undefined' && 'speechSynthesis' in window && 'SpeechSynthesisUtterance' in window);
  const manualStartNeeded = computed(() => status.value === 'error' && error.value === 'autoplay_blocked');

  function primeAudioSession(): void {
    primed.value = true;
    if (typeof window === 'undefined') {
      return;
    }
    if (browserSpeechSupported.value) {
      void window.speechSynthesis.getVoices();
    }
    if (status.value === 'loading' || status.value === 'playing') {
      return;
    }
    const audio = ensureUnlockedAudio();
    audio.muted = false;
    audio.volume = 1;
    audio.src = SILENT_AUDIO_DATA_URL;
    audio.load();
    void audio.play()
      .then(() => {
        audio.pause();
        audio.currentTime = 0;
      })
      .catch(() => {
        // Browsers can still reject this on some platforms; playback will fall back later.
      });
  }

  function setAutoplayEnabled(nextEnabled: boolean): void {
    storedAutoplayEnabled.value = nextEnabled;
    writeStoredBoolean(EASEWISE_STORAGE_KEYS.voiceAutoplayEnabled, nextEnabled);
    if (!nextEnabled && (status.value === 'playing' || status.value === 'loading')) {
      stop();
    }
  }

  function setEnabled(nextEnabled: boolean): void {
    storedEnabled.value = nextEnabled;
    writeStoredBoolean(EASEWISE_STORAGE_KEYS.voiceEnabled, nextEnabled);
    if (!nextEnabled) {
      stop();
    }
  }

  function toggleAutoplayEnabled(): void {
    setAutoplayEnabled(!autoplayEnabled.value);
  }

  async function speakPhoneSummary(review: ReviewRecord | null | undefined, speakOptions: SpeakOptions = {}): Promise<VoiceSpeakResult> {
    if (!review?.id) {
      return createVoiceResult(false);
    }
    const text = buildPhoneSummaryNarrationText(review);
    if (!text) {
      return createVoiceResult(false);
    }
    const key = `phone_summary:${review.id}:${review.updated_at || ''}`;
    const requestPayload: VoiceNarrationRequest = {
      scene: 'phone_summary',
      review_id: review.id,
      voice_key: voiceConfig.value?.default_voice_key ?? null,
    };
    return speakNarration({ key, text, requestPayload, auto: Boolean(speakOptions.auto) });
  }

  async function speakStability(review: ReviewRecord | null | undefined, speakOptions: SpeakOptions = {}): Promise<VoiceSpeakResult> {
    if (!review?.id) {
      return createVoiceResult(false);
    }
    const text = buildStabilityNarrationText(review);
    if (!text) {
      return createVoiceResult(false);
    }
    const key = `phone_stability:${review.id}:${review.updated_at || ''}`;
    const requestPayload: VoiceNarrationRequest = {
      scene: 'phone_stability',
      review_id: review.id,
      voice_key: voiceConfig.value?.default_voice_key ?? null,
    };
    return speakNarration({ key, text, requestPayload, auto: Boolean(speakOptions.auto) });
  }

  async function speakAspect(review: ReviewRecord | null | undefined, aspect: ReviewAspect | null | undefined, speakOptions: SpeakOptions = {}): Promise<VoiceSpeakResult> {
    if (!review?.id || !aspect?.aspect_key || !aspect.is_unlocked) {
      return createVoiceResult(false);
    }
    const text = buildAspectNarrationText(aspect);
    if (!text) {
      return createVoiceResult(false);
    }
    const key = `phone_aspect:${review.id}:${aspect.aspect_key}`;
    const requestPayload: VoiceNarrationRequest = {
      scene: 'phone_aspect',
      review_id: review.id,
      aspect_key: aspect.aspect_key,
      voice_key: voiceConfig.value?.default_voice_key ?? null,
    };
    return speakNarration({ key, text, requestPayload, auto: Boolean(speakOptions.auto) });
  }

  function stop(): void {
    speechRunId += 1;
    if (currentAudio) {
      currentAudio.onended = null;
      currentAudio.onerror = null;
      currentAudio.pause();
      currentAudio.removeAttribute('src');
      currentAudio.load();
      currentAudio = null;
    }
    if (typeof window !== 'undefined' && browserSpeechSupported.value) {
      window.speechSynthesis.cancel();
    }
    status.value = 'idle';
    currentKey.value = null;
    error.value = null;
    resolveActivePlayback(createVoiceResult(false, { stopped: true }));
  }

  async function speakNarration({
    key,
    text,
    requestPayload,
    auto,
  }: {
    key: string;
    text: string;
    requestPayload: VoiceNarrationRequest;
    auto: boolean;
  }): Promise<VoiceSpeakResult> {
    if (!enabled.value) {
      return createVoiceResult(false);
    }
    if (auto) {
      if (!autoplayEnabled.value || autoSpokenKeys.has(key)) {
        return createVoiceResult(false);
      }
      autoSpokenKeys.add(key);
    }

    stop();
    const runId = speechRunId + 1;
    speechRunId = runId;
    currentKey.value = key;
    error.value = null;
    status.value = 'loading';

    const mode = voiceConfig.value?.mode ?? 'hybrid';
    const shouldUseCloud = mode !== 'browser' && Boolean(options.getAccessToken());
    if (shouldUseCloud) {
      try {
        const narration = await createVoiceNarration(options.getAccessToken() || '', requestPayload);
        if (speechRunId !== runId || currentKey.value !== key) {
          return createVoiceResult(false, { stopped: true });
        }
        const audioResult = await playAudioUrl(resolveAudioUrl(narration.audio_url), key, runId, auto);
        if (audioResult.completed || (audioResult.started && !audioResult.error) || mode === 'cloud' || !browserSpeechSupported.value) {
          return audioResult;
        }
        if (speechRunId !== runId || currentKey.value !== key) {
          return createVoiceResult(false, { stopped: true });
        }
        error.value = null;
        status.value = 'loading';
      } catch (cloudError) {
        if (mode === 'cloud' || !browserSpeechSupported.value) {
          applyVoiceError(cloudError, auto);
          return createVoiceResult(false, { error: normalizeVoiceError(cloudError) });
        }
      }
    }

    if (!browserSpeechSupported.value) {
      const nextError = new Error('browser_speech_unavailable');
      applyVoiceError(nextError, auto);
      return createVoiceResult(false, { error: normalizeVoiceError(nextError) });
    }

    try {
      if (speechRunId !== runId || currentKey.value !== key) {
        return createVoiceResult(false, { stopped: true });
      }
      return await speakWithBrowser(text, key, runId);
    } catch (browserError) {
      applyVoiceError(browserError, auto);
      return createVoiceResult(false, { error: normalizeVoiceError(browserError) });
    }
  }

  function playAudioUrl(audioUrl: string, key: string, runId: number, auto: boolean): Promise<VoiceSpeakResult> {
    const audio = ensureUnlockedAudio();
    currentAudio = audio;
    audio.onended = null;
    audio.onerror = null;
    audio.muted = false;
    audio.volume = 1;
    audio.preload = 'auto';
    audio.src = audioUrl;
    audio.load();

    return new Promise<VoiceSpeakResult>((resolve) => {
      activeResolve = resolve;
      audio.onended = () => {
        if (currentKey.value !== key || speechRunId !== runId) {
          return;
        }
        if (currentKey.value === key && speechRunId === runId) {
          status.value = 'idle';
          currentKey.value = null;
        }
        resolveActivePlayback(createVoiceResult(true, { completed: true }));
      };
      audio.onerror = () => {
        if (currentKey.value !== key || speechRunId !== runId) {
          return;
        }
        const nextError = new Error('audio_play_failed');
        if (currentKey.value === key && speechRunId === runId) {
          applyVoiceError(nextError, auto);
        }
        resolveActivePlayback(createVoiceResult(true, { error: normalizeVoiceError(nextError) }));
      };
      audio.play()
        .then(() => {
          if (currentKey.value === key && speechRunId === runId) {
            status.value = 'playing';
          }
        })
        .catch((playError: unknown) => {
          if (currentKey.value !== key || speechRunId !== runId) {
            return;
          }
          if (currentKey.value === key && speechRunId === runId) {
            applyVoiceError(playError, auto);
          }
          resolveActivePlayback(createVoiceResult(false, { error: normalizeVoiceError(playError) }));
        });
    });
  }

  function ensureUnlockedAudio(): HTMLAudioElement {
    if (!unlockedAudio) {
      unlockedAudio = new Audio();
      unlockedAudio.preload = 'auto';
      unlockedAudio.setAttribute('playsinline', 'true');
      unlockedAudio.setAttribute('webkit-playsinline', 'true');
    }
    return unlockedAudio;
  }

  function speakWithBrowser(text: string, key: string, runId: number): Promise<VoiceSpeakResult> {
    if (!browserSpeechSupported.value) {
      throw new Error('browser_speech_unavailable');
    }
    const speechSynthesis = window.speechSynthesis;
    const chunks = splitSpeechText(text);
    if (!chunks.length) {
      throw new Error('voice_text_empty');
    }

    speechSynthesis.cancel();
    status.value = 'playing';

    return new Promise<VoiceSpeakResult>((resolve) => {
      activeResolve = resolve;
      let chunkIndex = 0;
      const speakNext = () => {
        if (speechRunId !== runId) {
          return;
        }
        const chunk = chunks[chunkIndex];
        if (!chunk) {
          if (currentKey.value === key) {
            status.value = 'idle';
            currentKey.value = null;
          }
          resolveActivePlayback(createVoiceResult(true, { completed: true }));
          return;
        }
        chunkIndex += 1;
        const utterance = new SpeechSynthesisUtterance(chunk);
        utterance.lang = 'zh-CN';
        utterance.rate = 0.95;
        utterance.pitch = 1;
        const voice = resolveChineseVoice();
        if (voice) {
          utterance.voice = voice;
        }
        utterance.onend = speakNext;
        utterance.onerror = () => {
          if (speechRunId === runId) {
            const nextError = new Error('browser_speech_failed');
            applyVoiceError(nextError, false);
            resolveActivePlayback(createVoiceResult(true, { error: normalizeVoiceError(nextError) }));
          }
        };
        speechSynthesis.speak(utterance);
      };
      speakNext();
    });
  }

  function applyVoiceError(rawError: unknown, auto: boolean): void {
    status.value = 'error';
    error.value = normalizeVoiceError(rawError);
    if (auto) {
      options.showToast?.('语音播报未能自动开始，可点击播放按钮手动收听。');
    }
  }

  function resolveActivePlayback(result: VoiceSpeakResult): void {
    if (!activeResolve) {
      return;
    }
    const resolve = activeResolve;
    activeResolve = null;
    resolve(result);
  }

  return {
    status,
    currentKey,
    error,
    enabled,
    autoplayEnabled,
    browserSpeechSupported,
    manualStartNeeded,
    primed,
    primeAudioSession,
    setAutoplayEnabled,
    setEnabled,
    toggleAutoplayEnabled,
    speakPhoneSummary,
    speakStability,
    speakAspect,
    stop,
    buildPhoneSummaryNarrationText,
    buildStabilityNarrationText,
    buildAspectNarrationText,
  };
}

function buildPhoneSummaryNarrationText(review: ReviewRecord): string {
  const summary = review.phone_summary;
  if (!summary) {
    return '';
  }
  return joinNarrationParts([
    '综合评述',
    summary.title,
    '风险提醒',
    summary.risk,
    '使用建议',
    summary.usage_guidance,
  ]);
}

function buildStabilityNarrationText(review: ReviewRecord): string {
  const stability = review.stability_detail;
  if (!stability) {
    return '';
  }
  return joinNarrationParts([
    '长期使用建议',
    stability.verdict,
    stability.content,
  ]);
}

function buildAspectNarrationText(aspect: ReviewAspect): string {
  if (!aspect.is_unlocked || !aspect.content) {
    return '';
  }
  const aspectTitle = aspect.short_title || aspect.title;
  return joinNarrationParts([
    `${aspectTitle}专项`,
    aspect.title,
    aspect.risk ? '风险提示' : '',
    aspect.risk,
    aspect.content,
  ]);
}

function createVoiceResult(started: boolean, detail: Partial<VoiceSpeakResult> = {}): VoiceSpeakResult {
  return {
    started,
    completed: false,
    ...detail,
  };
}

function joinNarrationParts(parts: Array<string | null | undefined>): string {
  const cleaned = parts
    .map((part) => cleanVoiceText(part))
    .filter(Boolean);
  return cleaned.length ? `${cleaned.join('。')}。` : '';
}

function cleanVoiceText(value: string | null | undefined): string {
  const text = String(value || '').trim();
  if (!text || ['title', 'risk', 'usage guidance'].includes(text.toLowerCase())) {
    return '';
  }
  return text.replace(/\s+/g, ' ').replace(/[｛｝{}*_`#>~]+/g, '').replace(/[。]+$/g, '').trim();
}

function splitSpeechText(text: string): string[] {
  const cleanText = cleanVoiceText(text);
  if (!cleanText) {
    return [];
  }
  const maxLength = 120;
  const chunks: string[] = [];
  let buffer = '';
  const sentences = cleanText.split(/(?<=[。！？!?；;])/);
  for (const sentence of sentences) {
    const candidate = `${buffer}${sentence}`.trim();
    if (candidate.length <= maxLength) {
      buffer = candidate;
      continue;
    }
    if (buffer) {
      chunks.push(buffer);
      buffer = '';
    }
    let remaining = sentence.trim();
    while (remaining.length > maxLength) {
      chunks.push(remaining.slice(0, maxLength));
      remaining = remaining.slice(maxLength);
    }
    buffer = remaining;
  }
  if (buffer) {
    chunks.push(buffer);
  }
  return chunks;
}

function resolveChineseVoice(): SpeechSynthesisVoice | null {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
    return null;
  }
  const voices = window.speechSynthesis.getVoices();
  return (
    voices.find((voice) => voice.lang.toLowerCase().startsWith('zh-cn')) ||
    voices.find((voice) => voice.lang.toLowerCase().startsWith('zh')) ||
    voices.find((voice) => /chinese|mandarin|中文|普通话/i.test(voice.name)) ||
    null
  );
}

function resolveAudioUrl(audioUrl: string): string {
  if (/^https?:\/\//i.test(audioUrl)) {
    return audioUrl;
  }
  const baseUrl = getApiBaseUrl();
  const normalizedPath = audioUrl.startsWith('/') ? audioUrl : `/${audioUrl}`;
  return `${baseUrl}${normalizedPath}`;
}

function normalizeVoiceError(rawError: unknown): string {
  if (rawError instanceof DOMException && rawError.name === 'NotAllowedError') {
    return 'autoplay_blocked';
  }
  if (rawError instanceof ApiError) {
    return rawError.detail;
  }
  if (rawError instanceof Error && rawError.message) {
    return rawError.message;
  }
  return 'voice_playback_failed';
}

function readStoredBoolean(key: string): boolean | null {
  if (typeof window === 'undefined') {
    return null;
  }
  const value = window.localStorage.getItem(key);
  if (value === null) {
    return null;
  }
  return value === 'true' || value === '1';
}

function writeStoredBoolean(key: string, value: boolean): void {
  if (typeof window === 'undefined') {
    return;
  }
  window.localStorage.setItem(key, value ? 'true' : 'false');
}
