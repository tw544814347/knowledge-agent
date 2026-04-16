import { useState, useEffect } from 'react';
import { MessageSquare, Pin, PinOff, Trash2, Clock } from 'lucide-react';
import { getConversations, updateConversation, deleteConversation } from '../api';

export default function ConversationHistory({ onSelectConversation, selectedConversationId }) {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadConversations = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await getConversations(20);
      setConversations(result.conversations || []);
    } catch (e) {
      setError(e.message);
      console.error('加载对话历史失败:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConversations();
  }, []);

  const handlePin = async (conversationId, currentPinned) => {
    try {
      await updateConversation(conversationId, { pinned: !currentPinned });
      await loadConversations(); // 重新加载列表
    } catch (e) {
      console.error('更新置顶状态失败:', e);
      setError(e.message);
    }
  };

  const handleDelete = async (conversationId) => {
    if (!confirm('确定要删除这个对话吗？')) return;
    
    try {
      await deleteConversation(conversationId);
      await loadConversations(); // 重新加载列表
      
      // 如果删除的是当前选中的对话，清除选中状态
      if (selectedConversationId === conversationId) {
        onSelectConversation(null);
      }
    } catch (e) {
      console.error('删除对话失败:', e);
      setError(e.message);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffHours = diffMs / (1000 * 60 * 60);
    
    if (diffHours < 1) {
      const diffMins = Math.floor(diffMs / (1000 * 60));
      return `${diffMins}分钟前`;
    } else if (diffHours < 24) {
      return `${Math.floor(diffHours)}小时前`;
    } else {
      return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-4">
        <div className="text-sm text-[var(--color-text-muted)]">加载中...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-3 text-xs text-red-400 bg-red-900/20 rounded">
        加载失败: {error}
      </div>
    );
  }

  if (conversations.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-[var(--color-text-muted)]">
        <MessageSquare size={32} className="mb-2 opacity-50" />
        <div className="text-sm">暂无历史对话</div>
      </div>
    );
  }

  // 分离置顶和普通对话
  const pinnedConversations = conversations.filter(c => c.pinned);
  const regularConversations = conversations.filter(c => !c.pinned);

  return (
    <div className="space-y-1">
      {/* 置顶对话 */}
      {pinnedConversations.length > 0 && (
        <div>
          <div className="text-xs text-[var(--color-text-muted)] px-2 py-1 uppercase tracking-wider">
            置顶对话
          </div>
          {pinnedConversations.map((conversation) => (
            <ConversationItem
              key={conversation.id}
              conversation={conversation}
              isSelected={selectedConversationId === conversation.id}
              onSelect={() => onSelectConversation(conversation)}
              onPin={handlePin}
              onDelete={handleDelete}
              formatDate={formatDate}
            />
          ))}
        </div>
      )}

      {/* 最近对话 */}
      {regularConversations.length > 0 && (
        <div>
          {pinnedConversations.length > 0 && (
            <div className="text-xs text-[var(--color-text-muted)] px-2 py-1 uppercase tracking-wider mt-3">
              最近对话
            </div>
          )}
          {regularConversations.map((conversation) => (
            <ConversationItem
              key={conversation.id}
              conversation={conversation}
              isSelected={selectedConversationId === conversation.id}
              onSelect={() => onSelectConversation(conversation)}
              onPin={handlePin}
              onDelete={handleDelete}
              formatDate={formatDate}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function ConversationItem({ conversation, isSelected, onSelect, onPin, onDelete, formatDate }) {
  const [showActions, setShowActions] = useState(false);

  return (
    <div
      className={`group relative p-2 rounded-lg cursor-pointer transition-all duration-200 ${
        isSelected 
          ? 'bg-[var(--color-primary)]/20 border border-[var(--color-primary)]/30' 
          : 'hover:bg-[var(--color-dark-700)]'
      }`}
      onClick={onSelect}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1 mb-1">
            {conversation.pinned && (
              <Pin size={12} className="text-yellow-500 flex-shrink-0" />
            )}
            <div className="text-sm font-medium text-[var(--color-text-primary)] truncate">
              {conversation.title}
            </div>
          </div>
          
          <div className="flex items-center gap-1 text-xs text-[var(--color-text-muted)]">
            <Clock size={10} />
            <span>{formatDate(conversation.created_at)}</span>
          </div>
        </div>

        {/* 操作按钮 */}
        {(showActions || isSelected) && (
          <div className="flex items-center gap-1 flex-shrink-0">
            <button
              onClick={(e) => {
                e.stopPropagation();
                onPin(conversation.id, conversation.pinned);
              }}
              className="p-1 rounded hover:bg-[var(--color-dark-600)] transition-colors"
              title={conversation.pinned ? "取消置顶" : "置顶"}
            >
              {conversation.pinned ? (
                <PinOff size={12} className="text-yellow-500" />
              ) : (
                <Pin size={12} className="text-[var(--color-text-muted)] hover:text-yellow-500" />
              )}
            </button>
            
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDelete(conversation.id);
              }}
              className="p-1 rounded hover:bg-red-600/20 transition-colors"
              title="删除对话"
            >
              <Trash2 size={12} className="text-[var(--color-text-muted)] hover:text-red-400" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}