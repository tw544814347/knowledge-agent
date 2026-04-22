import { useState, useEffect, useRef } from 'react';
import ChatPanel from './components/ChatPanel';
import Sidebar from './components/Sidebar';
import AuthModal from './components/AuthModal';
import AskModal from './components/AskModal';
import ChangePasswordModal from './components/ChangePasswordModal';
import BackendUnavailable from './components/BackendUnavailable';
import BackendChecking from './components/BackendChecking';
import { healthCheck, getStatus, getCurrentUser, logout, sendAskResponse, getConversation } from './api';

const HEALTH_PROBE_MS = 12_000;

export default function App() {
  /** checking: 首次探测；online: 后端可达；offline: 不可达（展示保养提示） */
  const [connectivity, setConnectivity] = useState('checking');
  const [serverStatus, setServerStatus] = useState(null);
  const [indexStatus, setIndexStatus] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(() =>
    typeof window === 'undefined' ? true : window.innerWidth >= 768
  );
  const isMobile = () => typeof window !== 'undefined' && window.innerWidth < 768;
  const handleSelectConversation = (conv) => {
    setSelectedConversation(conv);
    if (conv && isMobile()) setSidebarOpen(false);
  };

  const [selectedConversation, setSelectedConversation] = useState(null);
  /** 每次点击「新对话」递增，用于在 selectedConversation 已是 null 时仍强制重置 ChatPanel（清空草稿与流式请求） */
  const [draftSessionKey, setDraftSessionKey] = useState(0);
  const [user, setUser] = useState(() => getCurrentUser());

  const handleStartNewConversation = () => {
    setSelectedConversation(null);
    setDraftSessionKey((k) => k + 1);
    if (isMobile()) setSidebarOpen(false);
  };
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

  /** 选中会话后、或历史列表刷新后，拉取最新会话（含截断后的 messages），避免与后端存储不一致 */
  useEffect(() => {
    if (!user?.id || !selectedConversation?.id) return;
    const convId = selectedConversation.id;
    let cancelled = false;
    (async () => {
      try {
        const fresh = await getConversation(convId);
        if (!cancelled && fresh?.id === convId) {
          setSelectedConversation(fresh);
        }
      } catch {
        /* 忽略：列表里已有快照时可继续用 */
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [user?.id, selectedConversation?.id, conversationRefreshTrigger]);

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
        <>
          {/* 移动端半透明遮罩：点击收起侧边栏；桌面端隐藏 */}
          <div
            className="fixed inset-0 bg-black/50 z-30 md:hidden"
            onClick={() => setSidebarOpen(false)}
            aria-hidden="true"
          />
          <Sidebar
            serverStatus={serverStatus}
            indexStatus={indexStatus}
            onStartNewConversation={handleStartNewConversation}
            onClose={() => setSidebarOpen(false)}
            onStatusRefresh={async () => {
              const status = await getStatus();
              setIndexStatus(status);
            }}
            onSelectConversation={handleSelectConversation}
            selectedConversationId={selectedConversation?.id}
            user={user}
            onLogin={() => setShowAuthModal(true)}
            onLogout={handleLogout}
            onChangePassword={() => setShowChangePasswordModal(true)}
            refreshTrigger={conversationRefreshTrigger}
          />
        </>
      )}

      <main className="flex-1 flex flex-col min-w-0">
        <ChatPanel
          isConnected={!!serverStatus}
          onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
          sidebarOpen={sidebarOpen}
          selectedConversation={selectedConversation}
          draftSessionKey={draftSessionKey}
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
