function getAudioExtension(mimeType = '') {
  if (mimeType.includes('webm')) return 'webm';
  if (mimeType.includes('mp4')) return 'mp4';
  if (mimeType.includes('mpeg')) return 'mp3';
  if (mimeType.includes('wav')) return 'wav';
  if (mimeType.includes('ogg')) return 'ogg';
  return 'webm';
}

function getLanguageHint(language = '') {
  return language.split('-')[0] || 'en';
}

function createVoiceError(message, status = 500, code = 'voice_error', details = '') {
  const error = new Error(message);
  error.status = status;
  error.code = code;
  error.details = details;
  return error;
}

async function readErrorPayload(response) {
  const raw = await response.text();

  try {
    const parsed = JSON.parse(raw);
    return {
      raw,
      parsed,
      message: parsed?.error?.message || parsed?.message || raw,
      code: parsed?.error?.code || parsed?.code,
    };
  } catch {
    return {
      raw,
      parsed: null,
      message: raw,
      code: null,
    };
  }
}

async function transcribeAudio(audioDataUrl, language = 'en-IN') {
  if (!process.env.OPENROUTER_API_KEY) {
    throw new Error('OPENROUTER_API_KEY is required for voice transcription.');
  }

  const [metadata, base64Data] = audioDataUrl.split(',');
  if (!metadata || !base64Data) {
    throw new Error('Invalid audio payload.');
  }

  const mimeMatch = metadata.match(/^data:(.+);base64$/);
  if (!mimeMatch) {
    throw new Error('Unsupported audio format.');
  }

  const mimeType = mimeMatch[1];
  const extension = getAudioExtension(mimeType);

  const response = await fetch('https://openrouter.ai/api/v1/audio/transcriptions', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${process.env.OPENROUTER_API_KEY}`,
      'Content-Type': 'application/json',
      'HTTP-Referer': process.env.APP_URL || 'http://localhost:3171',
      'X-OpenRouter-Title': 'AI Legal Q&A',
    },
    body: JSON.stringify({
      model: process.env.OPENROUTER_STT_MODEL || 'openai/whisper-large-v3',
      input_audio: {
        data: base64Data,
        format: extension,
      },
      language: getLanguageHint(language),
    }),
  });

  if (!response.ok) {
    const { message, code, raw } = await readErrorPayload(response);

    if (
      response.status === 402 &&
      /at least \$0\.50 in balance for audio/i.test(message)
    ) {
      throw createVoiceError(
        'Voice transcription is unavailable because the configured OpenRouter account needs at least $0.50 balance for audio requests. Add credits to that account and try again.',
        402,
        code || 'insufficient_audio_balance',
        raw
      );
    }

    throw createVoiceError(
      `Transcription failed: ${message}`,
      response.status,
      code || 'transcription_failed',
      raw
    );
  }

  const data = await response.json();
  return data.text?.trim() || '';
}

async function synthesizeSpeech(text) {
  if (!process.env.OPENROUTER_API_KEY) {
    throw new Error('OPENROUTER_API_KEY is required for text-to-speech.');
  }

  const response = await fetch('https://openrouter.ai/api/v1/audio/speech', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${process.env.OPENROUTER_API_KEY}`,
      'Content-Type': 'application/json',
      'HTTP-Referer': process.env.APP_URL || 'http://localhost:3171',
      'X-OpenRouter-Title': 'AI Legal Q&A',
    },
    body: JSON.stringify({
      model: process.env.OPENROUTER_TTS_MODEL || 'openai/gpt-4o-mini-tts-2025-12-15',
      voice: process.env.TTS_VOICE || 'alloy',
      input: text,
      response_format: 'mp3',
    }),
  });

  if (!response.ok) {
    const { message, code, raw } = await readErrorPayload(response);

    if (
      response.status === 402 &&
      /at least \$0\.50 in balance for audio/i.test(message)
    ) {
      throw createVoiceError(
        'Text-to-speech is unavailable because the configured OpenRouter account needs at least $0.50 balance for audio requests. Add credits to that account and try again.',
        402,
        code || 'insufficient_audio_balance',
        raw
      );
    }

    throw createVoiceError(
      `Speech generation failed: ${message}`,
      response.status,
      code || 'speech_generation_failed',
      raw
    );
  }

  return Buffer.from(await response.arrayBuffer());
}

module.exports = {
  synthesizeSpeech,
  transcribeAudio,
};
