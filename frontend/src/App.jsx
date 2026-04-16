import { useState, useEffect } from 'react';
import ChatPanel from './components/ChatPanel';
import Sidebar from './components/Sidebar';
import AuthModal from './components/AuthModal';
import AskModal from './components/AskModal';
import { healthCheck, getStatus, getCurrentUser, logout, sendAskResponse } from './api';

export default function App() {
  const [serverStatus, setServerStatus] = useState(null);
  const [indexStatus, setIndexStatus] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [user, setUser] = useState(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [askModal, setAskModal] = useState(null); // { question, options }

  useEffect(() => {
    // 检查本地存储的用户信息
    const currentUser = getCurrentUser();
    if (currentUser) {
      setUser(currentUser);
    }

    const checkServer = async () => {
      try {
        const [health, status] = await Promise.all([healthCheck(), getStatus()]);
        setServerStatus(health);
        setIndexStatus(status);
      } catch {
        setServerStatus(null);
        setIndexStatus(null);
      }
    };
    checkServer();
    const timer = setInterval(checkServer, 30000);
    return () => clearInterval(timer);
  }, []);

  const handleAuthSuccess = (userData) => {
    setUser(userData);
    setShowAuthModal(false);
  };

  const handleLogout = () => {
    logout();
    setUser(null);
    setSelectedConversation(null);
  };

  const handleAskResponse = async (selectedOption, optionIndex) => {
    if (askModal) {
      try {
        await sendAskResponse(askModal.question, selectedOption, optionIndex);
      } catch (error) {
        console.error('发送ask响应失败:', error);
      }
      setAskModal(null);
    }
  };

  return (
    <div className="flex h-screen bg-[var(--color-dark-900)]">
      {sidebarOpen && (
        <Sidebar
          serverStatus={serverStatus}
          indexStatus={indexStatus}
          onClose={() => setSidebarOpen(false)}
          onStatusRefresh={async () => {
            const status = await getStatus();
            setIndexStatus(status);
          }}
          onSelectConversation={setSelectedConversation}
          selectedConversationId={selectedConversation?.id}
          user={user}
          onLogin={() => setShowAuthModal(true)}
          onLogout={handleLogout}
        />
      )}

      <main className="flex-1 flex flex-col min-w-0">
        <ChatPanel
          isConnected={!!serverStatus}
          onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
          sidebarOpen={sidebarOpen}
          selectedConversation={selectedConversation}
          user={user}
          onLogin={() => setShowAuthModal(true)}
          onConversationSaved={(conversation) => {
            // 对话保存后可以刷新侧边栏，这里暂时不做处理
          }}
        />
      </main>

      {/* Auth Modal */}
      {showAuthModal && (
        <AuthModal
          onClose={() => setShowAuthModal(false)}
          onAuthSuccess={handleAuthSuccess}
        />
      )}

      {/* Ask Modal */}
      {askModal && (
        <AskModal
          question={askModal.question}
          options={askModal.options}
          onClose={() => setAskModal(null)}
          onSelect={handleAskResponse}
        />
      )}
    </div>
  );
}
