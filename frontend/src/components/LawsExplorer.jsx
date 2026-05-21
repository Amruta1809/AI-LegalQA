
import { useState, useEffect } from 'react';
import { fetchLaws } from '../services/api';

const ACT_ICONS = {
  'Indian Penal Code': '⚔️',
  'Information Technology Act 2000': '💻',
  'Indian Contract Act 1872': '📝',
  'Consumer Protection Act 2019': '🛒',
  'Right to Information Act 2005': '📢',
  'Motor Vehicles Act 1988': '🚗',
  'Hindu Marriage Act 1955': '💍',
  'Protection of Women from Domestic Violence Act 2005': '🛡️',
  'POCSO Act 2012': '👶',
  'Constitution of India': '🏛️',
  'Code of Criminal Procedure 1973': '⚖️',
  'Indian Evidence Act 1872': '📋',
};

function LawsExplorer() {
  const [laws, setLaws] = useState({});
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState('');
  const [expandedAct, setExpandedAct] = useState(null);
  const [expandedLaw, setExpandedLaw] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      loadLaws();
    }, search ? 300 : 0);
    return () => clearTimeout(timer);
  }, [search]);

  const loadLaws = async () => {
    setLoading(true);
    try {
      const data = await fetchLaws(search);
      setLaws(data.laws);
      setTotal(data.total);
    } catch (err) {
      console.error('Failed to load laws:', err);
    }
    setLoading(false);
  };

  const actNames = Object.keys(laws);

  return (
    <div className="flex-1 flex flex-col bg-gray-900 min-h-0">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-800">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">📚 Laws Explorer</h2>
        <p className="text-xs text-gray-500 mt-1">{total} laws across {actNames.length} acts</p>
        {/* Search */}
        <div className="mt-3 relative">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search laws, sections, keywords..."
            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-sm text-white placeholder-gray-500 outline-none focus:border-blue-500 transition-colors"
          />
          <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500">🔍</span>
        </div>
      </div>

      {/* Laws list */}
      <div className="flex-1 overflow-y-auto px-4 py-4 chat-scroll">
        {loading ? (
          <div className="text-center text-gray-500 py-8">Loading laws...</div>
        ) : actNames.length === 0 ? (
          <div className="text-center text-gray-500 py-8">No laws found{search && ` for "${search}"`}</div>
        ) : (
          <div className="space-y-2">
            {actNames.map(act => (
              <div key={act} className="border border-gray-800 rounded-xl overflow-hidden">
                {/* Act header */}
                <button
                  onClick={() => setExpandedAct(expandedAct === act ? null : act)}
                  className="w-full flex items-center justify-between px-4 py-3 bg-gray-800/50 hover:bg-gray-800 transition-colors text-left"
                >
                  <div className="flex items-center gap-2">
                    <span>{ACT_ICONS[act] || '📄'}</span>
                    <span className="text-sm font-medium text-white">{act}</span>
                    <span className="text-xs text-gray-500 bg-gray-700 px-2 py-0.5 rounded-full">{laws[act].length}</span>
                  </div>
                  <svg xmlns="http://www.w3.org/2000/svg" className={`h-4 w-4 text-gray-500 transition-transform ${expandedAct === act ? 'rotate-180' : ''}`} viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </button>

                {/* Sections */}
                {expandedAct === act && (
                  <div className="divide-y divide-gray-800/50">
                    {laws[act].map(law => (
                      <div key={law.id} className="px-4 py-2">
                        <button
                          onClick={() => setExpandedLaw(expandedLaw === law.id ? null : law.id)}
                          className="w-full text-left flex items-center justify-between py-1"
                        >
                          <div>
                            <span className="text-xs text-blue-400 font-mono">§{law.section}</span>
                            <span className="text-sm text-gray-300 ml-2">{law.title}</span>
                          </div>
                          <svg xmlns="http://www.w3.org/2000/svg" className={`h-3 w-3 text-gray-600 transition-transform flex-shrink-0 ${expandedLaw === law.id ? 'rotate-180' : ''}`} viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                          </svg>
                        </button>
                        {expandedLaw === law.id && (
                          <div className="mt-2 mb-2 p-3 bg-gray-800/50 rounded-lg">
                            <p className="text-xs text-gray-400 leading-relaxed">{law.content}</p>
                            {law.keywords && law.keywords.length > 0 && (
                              <div className="mt-2 flex flex-wrap gap-1">
                                {law.keywords.map((kw, i) => (
                                  <span key={i} className="text-xs bg-gray-700 text-gray-400 px-2 py-0.5 rounded-full">{kw}</span>
                                ))}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default LawsExplorer;
