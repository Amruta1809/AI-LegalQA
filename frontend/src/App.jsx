import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ChatBox from './components/ChatBox';
import LawsExplorer from './components/LawsExplorer';
import About from './components/About';

function App() {
  const [chatSessions, setChatSessions] = useState(() => {
    const saved = localStorage.getItem('chatSessions');
    return saved ? JSON.parse(saved) : [];
  });
  const [activeChatId, setActiveChatId] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeView, setActiveView] = useState('chat');

  useEffect(() => {
    localStorage.setItem('chatSessions', JSON.stringify(chatSessions));
  }, [chatSessions]);

  const activeChat = chatSessions.find(c => c.id === activeChatId);

  const handleNewChat = () => {
    const newChat = {
      id: Date.now().toString(),
      title: 'New Chat',
      messages: [],
      createdAt: new Date().toISOString(),
    };
    setChatSessions(prev => [newChat, ...prev]);
    setActiveChatId(newChat.id);
    setActiveView('chat');
  };

  const handleUpdateMessages = (chatId, messages, title) => {
    setChatSessions(prev =>
      prev.map(c =>
        c.id === chatId ? { ...c, messages, title: title || c.title } : c
      )
    );
  };

  const handleDeleteChat = (chatId) => {
    setChatSessions(prev => prev.filter(c => c.id !== chatId));
    if (activeChatId === chatId) setActiveChatId(null);
  };

  const handleSelectChat = (chatId) => {
    setActiveChatId(chatId);
    setActiveView('chat');
  };

  const renderMainContent = () => {
    switch (activeView) {
      case 'laws':
        return <LawsExplorer />;
      case 'about':
        return <About />;
      default:
        return (
          <ChatBox
            chat={activeChat}
            onUpdateMessages={handleUpdateMessages}
            onNewChat={handleNewChat}
            sidebarOpen={sidebarOpen}
            onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
          />
        );
    }
  };

  return (
    <div className="flex h-screen bg-gray-900 text-white overflow-hidden">
      <Sidebar
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        chatSessions={chatSessions}
        activeChatId={activeChatId}
        onSelectChat={handleSelectChat}
        onNewChat={handleNewChat}
        onDeleteChat={handleDeleteChat}
        activeView={activeView}
        onChangeView={setActiveView}
      />
      <main className="flex-1 flex flex-col min-h-0">
        {renderMainContent()}
      </main>
    </div>
  );
}

export default App;
