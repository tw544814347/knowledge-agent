import { useState } from 'react';
import { Database, RefreshCw, HardDriveDownload, X, Cpu, Layers, Plus, LogIn, LogOut } from 'lucide-react';
import { syncDocuments, rebuildIndex, newChat } from '../api';
import ConversationHistory from './ConversationHistory';

export default function Sidebar({ 
  serverStatus, 
  indexStatus, 
  onClose, 
  onStatusRefresh,
  onSelectConversation,
  selectedConversationId,
  user,
  onLogin,
  onLogout
}) {
  const [syncing, setSyncing] = useState(false);
  const [rebuilding, setRebuilding] = useState(false);
  const [message, setMessage] = useState('');
  const [creatingNewChat, setCreatingNewChat] = useState(false);

  const handleSync = async () => {
    setSyncing(true);
    setMessage('');
    try {
      const result = await syncDocuments();
      setMessage(`同步完成：+${result.added} 新增, ~${result.updated} 更新, -${result.deleted} 删除`);
      onStatusRefresh?.();
    } catch (e) {
      setMessage(`同步失败：${e.message}`);
    } finally {
      setSyncing(false);
    }
  };

  const handleRebuild = async () => {
    if (!confirm('确定要重建索引吗？这会清空现有向量库并重新索引所有文档。')) return;
    setRebuilding(true);
    setMessage('');
    try {
      const result = await rebuildIndex();
      setMessage(`重建完成：${result.total_chunks} 个 chunk`);
      onStatusRefresh?.();
    } catch (e) {
      setMessage(`重建失败：${e.message}`);
    } finally {
      setRebuilding(false);
    }
  };

  const handleNewChat = async () => {
    setCreatingNewChat(true);
    setMessage('');
    try {
      await newChat();
      onSelectConversation(null); // 清空当前选中的对话
      setMessage('新对话已创建');
    } catch (e) {
      setMessage(`创建新对话失败：${e.message}`);
    } finally {
      setCreatingNewChat(false);
    }
  };

  return (
    <aside className="w-64 bg-[var(--color-dark-800)] border-r border-[var(--color-border)] flex flex-col shrink-0">
      <div className="p-4 border-b border-[var(--color-border)] flex items-center justify-between">
        <h1 className="text-base font-semibold text-[var(--color-text-primary)]">知识库 Agent</h1>
        <button onClick={onClose} className="p-1 rounded hover:bg-[var(--color-dark-600)] text-[var(--color-text-secondary)]">
          <X size={16} />
        </button>
      </div>

      {/* 用户状态 */}
      <div className="p-4 border-b border-[var(--color-border)]">
        {user ? (
          <div className="flex items-center justify-between">
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-[var(--color-text-primary)] truncate">
                {user.nickname || user.email}
              </div>
              <div className="text-xs text-[var(--color-text-muted)] truncate">
                {user.email}
              </div>
            </div>
            <button
              onClick={onLogout}
              className="ml-2 p-1 rounded hover:bg-[var(--color-dark-600)] text-[var(--color-text-secondary)]"
              title="退出登录"
            >
              <LogOut size={16} />
            </button>
          </div>
        ) : (
          <button
            onClick={onLogin}
            className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-lg bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white transition-colors"
          >
            <LogIn size={16} />
            登录/注册
          </button>
        )}
      </div>

      <div className="flex-1 p-4 space-y-5 overflow-y-auto">
        {/* 服务状态 */}
        <section>
          <h2 className="text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-2">服务状态</h2>
          <div className="space-y-2 text-sm">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${serverStatus ? 'bg-green-500' : 'bg-red-500'}`} />
              <span className="text-[var(--color-text-secondary)]">
                {serverStatus ? '已连接' : '未连接'}
              </span>
            </div>
            {serverStatus && (
              <div className="flex items-center gap-2 text-[var(--color-text-secondary)]">
                <Cpu size={14} />
                <span>{serverStatus.model}</span>
              </div>
            )}
          </div>
        </section>

        {/* 索引信息 */}
        <section>
          <h2 className="text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-2">知识库</h2>
          {indexStatus ? (
            <div className="space-y-2 text-sm text-[var(--color-text-secondary)]">
              <div className="flex items-center gap-2">
                <Database size={14} />
                <span>{indexStatus.total_chunks} 个文档片段</span>
              </div>
              <div className="flex items-center gap-2">
                <Layers size={14} />
                <span className="truncate text-xs" title={indexStatus.source_dir}>
                  {indexStatus.source_dir?.split('/').slice(-2).join('/')}
                </span>
              </div>
              {indexStatus.last_sync && (
                <div className="text-xs text-[var(--color-text-muted)]">
                  上次同步：{new Date(indexStatus.last_sync).toLocaleString()}
                </div>
              )}
            </div>
          ) : (
            <p className="text-sm text-[var(--color-text-muted)]">加载中...</p>
          )}
        </section>

        {/* 历史对话 */}
        {user && (
          <section>
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wider">历史对话</h2>
              <button
                onClick={handleNewChat}
                disabled={creatingNewChat}
                className="flex items-center gap-1 px-2 py-1 rounded text-xs bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] disabled:opacity-50 text-white transition-colors"
                title="新对话"
              >
                <Plus size={12} />
                {creatingNewChat ? '创建中...' : '新对话'}
              </button>
            </div>
            <div className="max-h-64 overflow-y-auto">
              <ConversationHistory 
                onSelectConversation={onSelectConversation}
                selectedConversationId={selectedConversationId}
              />
            </div>
          </section>
        )}

        {/* 操作 */}
        <section>
          <h2 className="text-xs font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-2">操作</h2>
          <div className="space-y-2">
            <button
              onClick={handleSync}
              disabled={syncing || !serverStatus}
              className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm bg-[var(--color-dark-600)] hover:bg-[var(--color-dark-500)] disabled:opacity-40 disabled:cursor-not-allowed text-[var(--color-text-secondary)] transition-colors"
            >
              <RefreshCw size={14} className={syncing ? 'animate-spin' : ''} />
              {syncing ? '同步中...' : '增量同步'}
            </button>
            <button
              onClick={handleRebuild}
              disabled={rebuilding || !serverStatus}
              className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm bg-[var(--color-dark-600)] hover:bg-[var(--color-dark-500)] disabled:opacity-40 disabled:cursor-not-allowed text-[var(--color-text-secondary)] transition-colors"
            >
              <HardDriveDownload size={14} className={rebuilding ? 'animate-spin' : ''} />
              {rebuilding ? '重建中...' : '重建索引'}
            </button>
          </div>
        </section>

        {message && (
          <div className="text-xs p-2 rounded bg-[var(--color-dark-700)] text-[var(--color-text-secondary)] break-words">
            {message}
          </div>
        )}
      </div>

      <div className="p-3 border-t border-[var(--color-border)] text-center text-xs text-[var(--color-text-muted)]">
        DeepSeek R1 · ChromaDB · RAG
      </div>
    </aside>
  );
}
