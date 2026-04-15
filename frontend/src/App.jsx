import { useState, useEffect } from 'react';
import ChatPanel from './components/ChatPanel';
import Sidebar from './components/Sidebar';
import { healthCheck, getStatus } from './api';

export default function App() {
  const [serverStatus, setServerStatus] = useState(null);
  const [indexStatus, setIndexStatus] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
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
        />
      )}

      <main className="flex-1 flex flex-col min-w-0">
        <ChatPanel
          isConnected={!!serverStatus}
          onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
          sidebarOpen={sidebarOpen}
        />
      </main>
    </div>
  );
}
