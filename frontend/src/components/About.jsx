function About() {
  return (
    <div className="flex-1 overflow-y-auto bg-gray-900 chat-scroll">
      <div className="max-w-2xl mx-auto px-6 py-8">
        {/* Hero */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-3xl mx-auto mb-4">⚖️</div>
          <h1 className="text-2xl font-bold text-white">AI Legal Q&A</h1>
          <p className="text-gray-400 mt-1">Know Your Rights, Simply</p>
          <p className="text-xs text-gray-600 mt-2">Version 1.0.0</p>
        </div>

        {/* What it does */}
        <div className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-5 mb-4">
          <h2 className="text-sm font-semibold text-white flex items-center gap-2 mb-3">🎯 What is this?</h2>
          <p className="text-sm text-gray-400 leading-relaxed">
            An AI-powered legal assistant that helps Indian citizens understand their legal rights. Ask questions in plain language and get answers grounded in actual Indian law sections with proper citations.
          </p>
        </div>

        {/* Features */}
        <div className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-5 mb-4">
          <h2 className="text-sm font-semibold text-white flex items-center gap-2 mb-3">✨ Features</h2>
          <div className="grid grid-cols-2 gap-3">
            {[
              { icon: '🔍', title: 'Semantic Search', desc: 'Finds relevant laws using AI embeddings' },
              { icon: '📖', title: 'Citations', desc: 'Every answer cites the exact act & section' },
              { icon: '🗣️', title: 'Voice Input', desc: 'Speak your question in any Indian language' },
              { icon: '🌐', title: '10 Languages', desc: 'Hindi, Marathi, Tamil, Telugu & more' },
              { icon: '📷', title: 'Image OCR', desc: 'Scan legal documents and get analysis' },
              { icon: '🔊', title: 'Read Aloud', desc: 'Listen to answers in your language' },
              { icon: '📚', title: 'Laws Explorer', desc: 'Browse 300+ laws across 30+ acts' },
              { icon: '💬', title: 'Chat History', desc: 'All conversations saved locally' },
            ].map((f, i) => (
              <div key={i} className="flex items-start gap-2 p-2">
                <span className="text-lg">{f.icon}</span>
                <div>
                  <p className="text-xs font-medium text-gray-300">{f.title}</p>
                  <p className="text-xs text-gray-500">{f.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Tech Stack */}
        <div className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-5 mb-4">
          <h2 className="text-sm font-semibold text-white flex items-center gap-2 mb-3">🛠️ Tech Stack</h2>
          <div className="flex flex-wrap gap-2">
            {['React', 'Vite', 'Tailwind CSS', 'Node.js', 'Express', 'Supabase', 'pgvector', 'Hugging Face', 'OpenRouter', 'GPT-4o-mini', 'Tesseract.js', 'Web Speech API'].map(tech => (
              <span key={tech} className="px-3 py-1 bg-gray-700/50 border border-gray-600/50 rounded-full text-xs text-gray-300">{tech}</span>
            ))}
          </div>
        </div>

        {/* How it works */}
        <div className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-5 mb-4">
          <h2 className="text-sm font-semibold text-white flex items-center gap-2 mb-3">⚙️ How it works</h2>
          <div className="space-y-3">
            {[
              { step: '1', text: 'Your question is converted into a vector embedding using Hugging Face AI' },
              { step: '2', text: 'The embedding is matched against 300+ Indian law sections using cosine similarity' },
              { step: '3', text: 'Top matching laws are retrieved from the Supabase database' },
              { step: '4', text: 'GPT-4o-mini generates a clear answer grounded in the retrieved law text' },
              { step: '5', text: 'Citations with exact act and section numbers are displayed' },
            ].map(s => (
              <div key={s.step} className="flex items-start gap-3">
                <span className="w-6 h-6 rounded-full bg-blue-600/20 text-blue-400 text-xs flex items-center justify-center flex-shrink-0">{s.step}</span>
                <p className="text-xs text-gray-400 leading-relaxed">{s.text}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Disclaimer */}
        <div className="bg-red-500/5 border border-red-500/20 rounded-xl p-5 mb-4">
          <h2 className="text-sm font-semibold text-red-400 flex items-center gap-2 mb-2">⚠️ Disclaimer</h2>
          <p className="text-xs text-gray-400 leading-relaxed">
            This tool provides general legal information for educational purposes only. It is not a substitute for professional legal advice. Always consult a qualified lawyer for advice specific to your situation.
          </p>
        </div>

        {/* Footer */}
        <p className="text-center text-xs text-gray-600 mt-6">Built with ❤️ for Indian citizens</p>
      </div>
    </div>
  );
}

export default About;
