const NAV_ITEMS = [
  { id: 'chat', label: 'Chat', icon: '💬' },
  { id: 'history', label: 'History', icon: '📜' },
  { id: 'laws', label: 'Laws Explorer', icon: '📚' },
  { id: 'about', label: 'About', icon: 'ℹ️' },
];

function Sidebar({ isOpen, onToggle, chatSessions, activeChatId, onSelectChat, onNewChat, onDeleteChat, activeView, onChangeView }) {
  if (!isOpen) return null;

  return (
    <aside className="w-64 bg-gray-950 border-r border-gray-800 flex flex-col h-full min-h-0">
      {/* Brand */}
      <div className="p-4 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-lg">⚖️</div>
          <div>
            <h1 className="text-sm font-semibold text-white">Legal AI Assistant</h1>
            <p className="text-xs text-gray-500">Know Your Rights, Simply</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="p-3 space-y-1">
        {NAV_ITEMS.map(item => (
          <button
            key={item.id}
            onClick={() => onChangeView(item.id === 'history' ? 'chat' : item.id)}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
              (activeView === item.id || (item.id === 'history' && activeView === 'chat'))
                ? 'bg-blue-600/20 text-blue-400'
                : 'text-gray-400 hover:bg-gray-800/50 hover:text-gray-300'
            }`}
          >
            <span>{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>

      {/* Chat History (shown when on chat/history view) */}
      {activeView === 'chat' && (
        <div className="flex-1 overflow-y-auto px-3 pb-3 sidebar-scroll border-t border-gray-800 mt-2 pt-3">
          <div className="flex items-center justify-between px-2 mb-2">
            <p className="text-xs text-gray-500 uppercase tracking-wider">Recent Chats</p>
            <button onClick={onNewChat} className="text-xs text-blue-400 hover:text-blue-300">+ New</button>
          </div>
          {chatSessions.length === 0 ? (
            <p className="text-xs text-gray-600 px-2">No conversations yet</p>
          ) : (
            <div className="space-y-1">
              {chatSessions.map(chat => (
                <div
                  key={chat.id}
                  className={`group flex items-center justify-between px-3 py-2 rounded-lg cursor-pointer transition-colors ${
                    activeChatId === chat.id ? 'bg-gray-800 text-white' : 'text-gray-400 hover:bg-gray-800/50 hover:text-gray-300'
                  }`}
                  onClick={() => onSelectChat(chat.id)}
                >
                  <p className="text-xs truncate flex-1">{chat.title}</p>
                  <button
                    onClick={(e) => { e.stopPropagation(); onDeleteChat(chat.id); }}
                    className="opacity-0 group-hover:opacity-100 text-gray-600 hover:text-red-400 transition-all ml-2"
                    aria-label="Delete chat"
                  >✕</button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Spacer for non-chat views */}
      {activeView !== 'chat' && <div className="flex-1" />}

      {/* Privacy note */}
      <div className="p-4 border-t border-gray-800">
        <div className="flex items-center gap-2">
          <span className="text-lg">🔒</span>
          <div>
            <p className="text-xs text-gray-400 font-medium">Your legal information is safe.</p>
            <p className="text-xs text-gray-600">We respect your privacy.</p>
          </div>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;
