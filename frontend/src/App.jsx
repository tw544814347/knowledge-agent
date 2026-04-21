import { useState, useEffect, useRef } from 'react';
import ChatPanel from './components/ChatPanel';
import Sidebar from './components/Sidebar';
import AuthModal from './components/AuthModal';
import AskModal from './components/AskModal';
import ChangePasswordModal from './components/ChangePasswordModal';
import BackendUnavailable from './components/BackendUnavailable';
import BackendChecking from './components/BackendChecking';
import { healthCheck, getStatus, getCurrentUser, logout, sendAskResponse } from './api';

const HEALTH_PROBE_MS = 12_000;

export default function App() {
  /** checking: 首次探测；online: 后端可达；offline: 不可达（展示保养提示） */
  const [connectivity, setConnectivity] = useState('checking');
  const [serverStatus, setServerStatus] = useState(null);
  const [indexStatus, setIndexStatus] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [user, setUser] = useState(() => getCurrentUser());
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [conversationRefreshTrigger, setConversationRefreshTrigger] = useState(0);
  const [showChangePasswordModal, setShowChangePasswordModal] = useState(false);
  const [askModal, setAskModal] = useState(null); // { question, options }

  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  useEffect(() => {
    const probeBackend = async () => {
      const ac = new AbortController();
      const t = setTimeout(() => ac.abort(), HEALTH_PROBE_MS);
      try {
        const health = await healthCheck(ac.signal);
        clearTimeout(t);
        if (!mountedRef.current) return;
        let status = null;
        try {
          status = await getStatus();
        } catch {
          status = null;
        }
        setServerStatus(health);
        setIndexStatus(status);
        setConnectivity('online');
      } catch {
        clearTimeout(t);
        if (!mountedRef.current) return;
        setServerStatus(null);
        setIndexStatus(null);
        setConnectivity('offline');
      }
    };

    probeBackend();
    const timer = setInterval(probeBackend, 30_000);
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

  if (connectivity === 'checking') {
    return <BackendChecking />;
  }

  if (connectivity === 'offline') {
    return <BackendUnavailable />;
  }

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
          onChangePassword={() => setShowChangePasswordModal(true)}
          refreshTrigger={conversationRefreshTrigger}
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
          onConversationSaved={() => {
            setConversationRefreshTrigger((prev) => prev + 1);
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

      {/* Change Password Modal */}
      {showChangePasswordModal && user && (
        <ChangePasswordModal
          user={user}
          onClose={() => setShowChangePasswordModal(false)}
          onSuccess={() => {
            // 密码修改成功后的回调（如果需要特别处理）
            console.log('密码修改成功');
          }}
        />
      )}
    </div>
  );
}
