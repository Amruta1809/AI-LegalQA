import { useEffect, useRef, useState } from 'react';
import StructuredAnswer from './StructuredAnswer';
import { speakText } from '../services/api';

function MessageBubble({ message, language = 'en-IN' }) {
  const [copied, setCopied] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const audioRef = useRef(null);
  const audioUrlRef = useRef(null);

  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
      }
      if (audioUrlRef.current) {
        URL.revokeObjectURL(audioUrlRef.current);
      }
    };
  }, []);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSpeak = async () => {
    if (speaking) {
      window.speechSynthesis.cancel();
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
      }
      setSpeaking(false);
      return;
    }

    try {
      setSpeaking(true);
      const audioBlob = await speakText(message.text);
      const nextAudioUrl = URL.createObjectURL(audioBlob);
      if (audioUrlRef.current) {
        URL.revokeObjectURL(audioUrlRef.current);
      }
      audioUrlRef.current = nextAudioUrl;

      const audio = new Audio(nextAudioUrl);
      audioRef.current = audio;
      audio.onended = () => setSpeaking(false);
      audio.onerror = () => setSpeaking(false);
      await audio.play();
    } catch (error) {
      // Fall back to browser TTS if OpenAI TTS is unavailable.
      const utterance = new SpeechSynthesisUtterance(message.text);
      utterance.lang = language;
      utterance.rate = 0.9;
      utterance.onend = () => setSpeaking(false);
      utterance.onerror = () => setSpeaking(false);
      window.speechSynthesis.speak(utterance);
    }
  };

  if (message.type === 'user') {
    return (
      <div className="flex justify-end">
        <div className="max-w-[75%]">
          {message.image && (
            <div className="mb-2 flex justify-end">
              <img src={message.image} alt="Attached" className="max-h-48 rounded-xl border border-gray-700" />
            </div>
          )}
          <div className="bg-blue-600 text-white px-4 py-3 rounded-2xl rounded-tr-sm text-sm leading-relaxed">
            {message.text}
            {message.ocrText && (
              <div className="mt-2 pt-2 border-t border-blue-500/30 text-xs text-blue-200">
                📄 Extracted text from image
              </div>
            )}
          </div>
          <p className="text-xs text-gray-600 text-right mt-1">
            {new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-start gap-3">
      <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-sm flex-shrink-0 mt-1">⚖️</div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-sm font-medium text-white">Legal AI Assistant</span>
          <span className="text-xs text-gray-600">{new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}</span>
        </div>

        <div className="bg-gray-800/50 rounded-2xl rounded-tl-sm px-5 py-4 border border-gray-700/50">
          <StructuredAnswer text={message.text} citations={message.citations} />
        </div>

        {/* Action buttons */}
        <div className="mt-2 flex items-center gap-4">
          <button onClick={handleCopy} className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-300 transition-colors">
            {copied ? '✓ Copied' : '📋 Copy'}
          </button>
          <button onClick={handleSpeak} className={`flex items-center gap-1.5 text-xs transition-colors ${speaking ? 'text-blue-400' : 'text-gray-500 hover:text-gray-300'}`}>
            {speaking ? '⏹ Stop' : '🔊 Read aloud'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default MessageBubble;
