import { useState, useRef, useEffect } from 'react';
import Tesseract from 'tesseract.js';
import MessageBubble from './MessageBubble';
import { askQuestion, transcribeAudio } from '../services/api';

const LANGUAGES = [
  { code: 'en-IN', label: 'English', flag: '🇬🇧', ocr: 'eng' },
  { code: 'hi-IN', label: 'हिन्दी', flag: '🇮🇳', ocr: 'hin' },
  { code: 'mr-IN', label: 'मराठी', flag: '🇮🇳', ocr: 'mar' },
  { code: 'ta-IN', label: 'தமிழ்', flag: '🇮🇳', ocr: 'tam' },
  { code: 'te-IN', label: 'తెలుగు', flag: '🇮🇳', ocr: 'tel' },
  { code: 'bn-IN', label: 'বাংলা', flag: '🇮🇳', ocr: 'ben' },
  { code: 'gu-IN', label: 'ગુજરાતી', flag: '🇮🇳', ocr: 'guj' },
  { code: 'kn-IN', label: 'ಕನ್ನಡ', flag: '🇮🇳', ocr: 'kan' },
  { code: 'ml-IN', label: 'മലയാളം', flag: '🇮🇳', ocr: 'mal' },
  { code: 'pa-IN', label: 'ਪੰਜਾਬੀ', flag: '🇮🇳', ocr: 'pan' },
];

function ChatBox({ chat, onUpdateMessages, onNewChat, sidebarOpen, onToggleSidebar }) {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [language, setLanguage] = useState('en-IN');
  const [showLangMenu, setShowLangMenu] = useState(false);
  const [attachedImage, setAttachedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [ocrProgress, setOcrProgress] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const fileInputRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const mediaStreamRef = useRef(null);
  const audioChunksRef = useRef([]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chat?.messages]);

  useEffect(() => {
    inputRef.current?.focus();
  }, [chat?.id]);

  useEffect(() => {
    return () => {
      mediaStreamRef.current?.getTracks().forEach((track) => track.stop());
    };
  }, []);

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    mediaStreamRef.current?.getTracks().forEach((track) => track.stop());
    mediaStreamRef.current = null;
    setIsRecording(false);
  };

  const toggleRecording = async () => {
    if (isRecording) {
      stopRecording();
      return;
    }

    if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
      alert('Voice recording is not supported in this browser.');
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;
      audioChunksRef.current = [];

      const recorder = new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      recorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: recorder.mimeType || 'audio/webm' });
        if (!audioBlob.size) {
          return;
        }

        setIsTranscribing(true);
        try {
          const result = await transcribeAudio(audioBlob, language);
          const transcript = result.text?.trim();
          if (transcript) {
            setInput((prev) => (prev ? `${prev} ${transcript}` : transcript));
          }
        } catch (error) {
          console.error('Voice transcription failed:', error);
          const errorMessage =
            error?.response?.data?.error ||
            error?.message ||
            'Voice transcription failed. Please try again.';
          alert(errorMessage);
        } finally {
          setIsTranscribing(false);
        }
      };

      recorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Unable to start recording:', error);
      alert('Microphone access is required for voice input.');
    }
  };

  const getLangName = (code) => LANGUAGES.find(l => l.code === code)?.label || 'English';
  const getOcrLang = (code) => LANGUAGES.find(l => l.code === code)?.ocr || 'eng';

  // Image handling
  const handleImageSelect = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.type.startsWith('image/')) return;
    setAttachedImage(file);
    const reader = new FileReader();
    reader.onload = (ev) => setImagePreview(ev.target.result);
    reader.readAsDataURL(file);
  };

  const removeImage = () => {
    setAttachedImage(null);
    setImagePreview(null);
    setOcrProgress(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const extractTextFromImage = async (imageFile) => {
    const ocrLang = getOcrLang(language);
    setOcrProgress('Extracting text from image...');
    try {
      const result = await Tesseract.recognize(imageFile, ocrLang, {
        logger: (m) => {
          if (m.status === 'recognizing text') {
            setOcrProgress(`Reading image... ${Math.round(m.progress * 100)}%`);
          }
        },
      });
      setOcrProgress(null);
      return result.data.text.trim();
    } catch (err) {
      setOcrProgress(null);
      console.error('OCR error:', err);
      return '';
    }
  };

  const handleSend = async () => {
    if ((!input.trim() && !attachedImage) || loading) return;
    if (!chat) { onNewChat(); return; }

    let question = input.trim();
    let ocrText = '';
    const msgImage = imagePreview;

    // Run OCR if image attached
    if (attachedImage) {
      ocrText = await extractTextFromImage(attachedImage);
      if (ocrText) {
        question = question
          ? `${question}\n\n[Text extracted from attached image]:\n${ocrText}`
          : `Please analyze this legal text extracted from an image:\n\n${ocrText}`;
      }
    }

    const userMessage = { type: 'user', text: input.trim() || 'Attached an image for analysis', image: msgImage, ocrText };
    const newMessages = [...(chat.messages || []), userMessage];
    const title = chat.messages.length === 0 ? (input.trim() || 'Image analysis').substring(0, 40) : chat.title;
    onUpdateMessages(chat.id, newMessages, title);
    setInput('');
    removeImage();
    setLoading(true);

    try {
      const langName = getLangName(language);
      const langHint = language !== 'en-IN' ? ` (Please respond in ${langName})` : '';
      const response = await askQuestion(question + langHint);
      const botMessage = { type: 'bot', text: response.answer, citations: response.citations };
      onUpdateMessages(chat.id, [...newMessages, botMessage], title);
    } catch (error) {
      const errorMessage = { type: 'bot', text: 'Sorry, something went wrong. Please try again.' };
      onUpdateMessages(chat.id, [...newMessages, errorMessage], title);
    }
    setLoading(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  // Welcome screen
  if (!chat) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-gray-900 px-4">
        {!sidebarOpen && (
          <button onClick={onToggleSidebar} className="absolute top-4 left-4 text-gray-500 hover:text-gray-300" aria-label="Open sidebar">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" /></svg>
          </button>
        )}
        <div className="text-center max-w-lg">
          <div className="text-5xl mb-4">⚖️</div>
          <h1 className="text-2xl font-bold text-white mb-2">AI Legal Q&A</h1>
          <p className="text-gray-400 mb-2">Ask questions about Indian laws and get answers with citations.</p>
          <p className="text-gray-500 text-sm mb-8">🗣️ Voice · 📷 Image OCR · 🌐 Regional Languages</p>
          <button onClick={onNewChat} className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-medium transition-colors">Start a New Chat</button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-gray-900 relative min-h-0">
      {/* Header */}
      <div className="flex items-center gap-3 px-4 py-3 border-b border-gray-800 bg-gray-900">
        {!sidebarOpen && (
          <button onClick={onToggleSidebar} className="text-gray-500 hover:text-gray-300" aria-label="Open sidebar">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" /></svg>
          </button>
        )}
        <span className="text-lg">⚖️</span>
        <h2 className="text-sm font-medium text-gray-300 truncate flex-1">{chat.title}</h2>
        {/* Language selector */}
        <div className="relative">
          <button onClick={() => setShowLangMenu(!showLangMenu)} className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-800 hover:bg-gray-700 rounded-lg text-xs text-gray-300 border border-gray-700">
            <span>🌐</span>
            <span>{LANGUAGES.find(l => l.code === language)?.label || 'English'}</span>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3" viewBox="0 0 20 20" fill="currentColor"><path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" /></svg>
          </button>
          {showLangMenu && (
            <div className="absolute right-0 top-full mt-1 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-50 py-1 w-40">
              {LANGUAGES.map(lang => (
                <button key={lang.code} onClick={() => { setLanguage(lang.code); setShowLangMenu(false); }}
                  className={`w-full text-left px-3 py-2 text-xs hover:bg-gray-700 flex items-center gap-2 ${language === lang.code ? 'text-blue-400' : 'text-gray-300'}`}>
                  <span>{lang.flag}</span><span>{lang.label}</span>{language === lang.code && <span className="ml-auto">✓</span>}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 bg-gray-900 chat-scroll">
        <div className="max-w-3xl mx-auto space-y-6">
          {chat.messages.map((msg, index) => (
            <MessageBubble key={index} message={msg} language={language} />
          ))}
          {loading && (
            <div className="flex items-start gap-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-sm flex-shrink-0">⚖️</div>
              <div className="bg-gray-800 rounded-2xl rounded-tl-sm px-4 py-3">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                  <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                  <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input area */}
      <div className="border-t border-gray-800 bg-gray-900 px-4 py-4">
        <div className="max-w-3xl mx-auto">
          {/* Image preview */}
          {imagePreview && (
            <div className="mb-3 relative inline-block">
              <img src={imagePreview} alt="Attached" className="h-24 rounded-lg border border-gray-700" />
              <button onClick={removeImage} className="absolute -top-2 -right-2 w-5 h-5 bg-red-500 rounded-full text-white text-xs flex items-center justify-center hover:bg-red-600">✕</button>
              {ocrProgress && (
                <div className="absolute inset-0 bg-black/70 rounded-lg flex items-center justify-center">
                  <p className="text-xs text-white px-2 text-center">{ocrProgress}</p>
                </div>
              )}
            </div>
          )}

          <div className="flex items-end gap-2 bg-gray-800 rounded-xl border border-gray-700 focus-within:border-blue-500 transition-colors px-4 py-3">
            {/* Attach image */}
            <input type="file" ref={fileInputRef} accept="image/*" onChange={handleImageSelect} className="hidden" />
            <button
              onClick={() => fileInputRef.current?.click()}
              className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors flex-shrink-0"
              title="Attach image (OCR)"
              aria-label="Attach image"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
              </svg>
            </button>
            {/* Voice input */}
            <button
              onClick={toggleRecording}
              disabled={isTranscribing}
              className={`p-2 rounded-lg transition-colors flex-shrink-0 ${
                isRecording
                  ? 'bg-red-500 text-white animate-pulse'
                  : isTranscribing
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-700'
              }`}
              title={isRecording ? 'Stop recording' : isTranscribing ? 'Transcribing...' : 'Voice input'}
              aria-label={isRecording ? 'Stop recording' : 'Start voice input'}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
              </svg>
            </button>
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
              className="flex-1 bg-transparent text-white placeholder-gray-500 resize-none outline-none text-sm"
              placeholder={isRecording ? 'Recording...' : isTranscribing ? 'Transcribing voice...' : 'Type your legal question here...'}
              style={{ maxHeight: '120px' }}
            />
            <button
              onClick={handleSend}
              disabled={(!input.trim() && !attachedImage) || loading}
              className="p-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:text-gray-500 rounded-lg transition-colors flex-shrink-0"
              aria-label="Send message"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
              </svg>
            </button>
          </div>
          <p className="text-xs text-gray-600 text-center mt-2">📷 Attach legal documents · 🎙 Voice record & transcribe · 🌐 Regional languages</p>
          {/* Suggested questions */}
          {chat.messages.length === 0 && (
            <div className="flex items-center gap-2 mt-3 overflow-x-auto pb-1">
              <span className="text-xs text-gray-600 flex-shrink-0">Try:</span>
              {['What is cyber bullying?', 'What is FIR?', 'My salary is not paid, what can I do?', 'What is Section 498A?'].map(q => (
                <button key={q} onClick={() => setInput(q)}
                  className="flex-shrink-0 px-3 py-1.5 bg-gray-800 border border-gray-700 rounded-full text-xs text-gray-400 hover:text-white hover:border-gray-500 transition-colors">{q}</button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ChatBox;
