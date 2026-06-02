# EaseWise Voice Playback Integration

## Scope

The first voice playback foundation covers:

- H5 result pages in the current Vue frontend.
- Mini Program playback through the same backend narration API.
- Future agent replies through the same provider/cache layer after adding an agent scene.

## Backend Contract

`POST /api/v1/voice/narrations`

The frontend must send a source reference instead of raw text.

```ts
type VoiceNarrationRequest =
  | { scene: 'phone_summary'; review_id: string; voice_key?: string | null }
  | { scene: 'phone_aspect'; review_id: string; aspect_key: string; voice_key?: string | null };

type VoiceNarrationResponse = {
  narration_id: string;
  scene: 'phone_summary' | 'phone_aspect';
  text_hash: string;
  audio_url: string;
  provider: string;
  voice_key: string;
  format: 'mp3';
  char_count: number;
  cached: boolean;
};
```

The backend validates ownership, review readiness, and aspect unlock state before composing text.

## H5 Playback

The H5 app uses `useVoicePlayback`:

- Try cloud TTS first when `voice.mode` is `hybrid` or `cloud`.
- Fall back to `speechSynthesis` when cloud TTS is unavailable and mode is `hybrid`.
- Store autoplay preference in `easewise_voice_autoplay_enabled`.

## Mini Program Playback

Mini Program code should use cloud TTS only:

```ts
async function playNarration(accessToken: string, request: VoiceNarrationRequest) {
  const response = await requestVoiceNarration(accessToken, request);
  const audio = wx.createInnerAudioContext();
  audio.src = absoluteApiUrl(response.audio_url);
  audio.autoplay = true;
  audio.play();
  return audio;
}
```

Mini Program UI should keep the same behavior as H5:

- Prime playback from the user's review/unlock tap.
- Auto-play once for a new phone summary or newly unlocked aspect.
- Always provide a visible stop/play control.
- Store the user's autoplay preference in Mini Program storage.

## Runtime Config

Voice config is exposed under `runtimeConfig.modules.voice`:

- `enabled`
- `mode`
- `autoplay_default_enabled`
- `provider`
- `default_voice_key`
- `cache_enabled`
- `max_chars_per_request`
