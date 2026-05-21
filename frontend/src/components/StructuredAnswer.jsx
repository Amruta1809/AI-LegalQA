import { useState } from 'react';

function Section({ icon, title, color, children, defaultOpen = true }) {
  const [open, setOpen] = useState(defaultOpen);
  const colorMap = {
    blue: 'border-blue-500/30 bg-blue-500/5',
    yellow: 'border-yellow-500/30 bg-yellow-500/5',
    red: 'border-red-500/30 bg-red-500/5',
    green: 'border-green-500/30 bg-green-500/5',
    purple: 'border-purple-500/30 bg-purple-500/5',
  };
  const titleColor = {
    blue: 'text-blue-400',
    yellow: 'text-yellow-400',
    red: 'text-red-400',
    green: 'text-green-400',
    purple: 'text-purple-400',
  };

  return (
    <div className={`border rounded-xl ${colorMap[color]} overflow-hidden`}>
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-4 py-3 text-left"
      >
        <div className="flex items-center gap-2">
          <span>{icon}</span>
          <span className={`text-sm font-semibold ${titleColor[color]}`}>{title}</span>
        </div>
        <svg xmlns="http://www.w3.org/2000/svg" className={`h-4 w-4 text-gray-500 transition-transform ${open ? 'rotate-180' : ''}`} viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
        </svg>
      </button>
      {open && <div className="px-4 pb-3 text-sm text-gray-300 leading-relaxed">{children}</div>}
    </div>
  );
}

function parseAnswer(text, citations) {
  // Try to extract structured parts from the answer
  const lines = text.split('\n').filter(l => l.trim());
  let answer = '';
  let explanation = '';
  let punishment = '';
  let advice = '';

  // Simple heuristic parsing
  let currentSection = 'answer';
  for (const line of lines) {
    const lower = line.toLowerCase();
    if (lower.includes('explanation:') || lower.includes('what it means:')) {
      currentSection = 'explanation';
      explanation += line.replace(/^.*?:/i, '').trim() + '\n';
    } else if (lower.includes('punishment:') || lower.includes('penalty:') || lower.includes('imprisonment')) {
      if (!answer && currentSection === 'answer') {
        answer += line + '\n';
      } else {
        currentSection = 'punishment';
        punishment += line + '\n';
      }
    } else if (lower.includes('you can') || lower.includes('you should') || lower.includes('steps:') || lower.includes('what to do:')) {
      currentSection = 'advice';
      advice += line + '\n';
    } else {
      if (currentSection === 'answer') answer += line + '\n';
      else if (currentSection === 'explanation') explanation += line + '\n';
      else if (currentSection === 'punishment') punishment += line + '\n';
      else if (currentSection === 'advice') advice += line + '\n';
    }
  }

  // If no structured sections found, put everything in answer
  if (!explanation && !punishment && !advice) {
    answer = text;
  }

  return { answer: answer.trim(), explanation: explanation.trim(), punishment: punishment.trim(), advice: advice.trim() };
}

function StructuredAnswer({ text, citations }) {
  const { answer, explanation, punishment, advice } = parseAnswer(text, citations);
  const hasCitations = citations && citations.length > 0;

  return (
    <div className="space-y-3">
      {/* Main Answer */}
      <div className="flex items-start gap-2 mb-2">
        <span className="text-green-400 mt-0.5">✅</span>
        <div>
          <p className="text-sm font-semibold text-white mb-1">Answer</p>
          <p className="text-sm text-gray-300 leading-relaxed whitespace-pre-wrap">{answer}</p>
        </div>
      </div>

      {/* Applicable Law */}
      {hasCitations && (
        <Section icon="⚖️" title="Applicable Law" color="blue">
          {citations.map((c, i) => (
            <div key={i} className="flex items-center gap-2 py-1">
              <span className="text-xs text-gray-500">Act:</span>
              <span className="text-sm text-white">{c.act}</span>
              <span className="text-xs text-gray-500 ml-2">Section:</span>
              <span className="text-sm text-white">{c.section}</span>
            </div>
          ))}
        </Section>
      )}

      {/* Explanation */}
      {explanation && (
        <Section icon="📖" title="Explanation" color="yellow">
          <p className="whitespace-pre-wrap">{explanation}</p>
        </Section>
      )}

      {/* Punishment */}
      {punishment && (
        <Section icon="🚨" title="Punishment" color="red">
          <p className="whitespace-pre-wrap">{punishment}</p>
        </Section>
      )}

      {/* What You Can Do */}
      {advice && (
        <Section icon="💡" title="What You Can Do" color="green">
          <p className="whitespace-pre-wrap">{advice}</p>
        </Section>
      )}

      {/* Disclaimer */}
      <Section icon="ℹ️" title="Disclaimer" color="purple" defaultOpen={false}>
        <p className="text-gray-400 text-xs">This information is for general awareness only and not legal advice. Please consult a qualified lawyer for advice on your specific case.</p>
      </Section>
    </div>
  );
}

export default StructuredAnswer;
