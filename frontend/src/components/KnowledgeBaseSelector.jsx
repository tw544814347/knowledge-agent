import { useState, useEffect } from 'react';
import { Database, ChevronDown, Check, AlertCircle } from 'lucide-react';

export default function KnowledgeBaseSelector({ user, onKnowledgeBaseChange }) {
  const [knowledgeBases, setKnowledgeBases] = useState([]);
  const [currentKB, setCurrentKB] = useState(null);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 获取知识库列表
  const loadKnowledgeBases = async () => {
    if (!user) return;
    
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/knowledge-bases', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      setKnowledgeBases(data.knowledge_bases || []);
      setCurrentKB(data.current);
      setError(null);
    } catch (err) {
      console.error('加载知识库列表失败:', err);
      setError('加载失败');
    }
  };

  // 切换知识库
  const switchKnowledgeBase = async (kbId) => {
    if (!user || kbId === currentKB) return;
    
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/knowledge-bases/switch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ kb_id: kbId })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      setCurrentKB(kbId);
      setIsOpen(false);
      setError(null);
      onKnowledgeBaseChange?.(kbId);
    } catch (err) {
      console.error('切换知识库失败:', err);
      setError('切换失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadKnowledgeBases();
  }, [user]);

  if (!user || knowledgeBases.length === 0) {
    return null;
  }

  const currentKBInfo = knowledgeBases.find(kb => kb.id === currentKB);

  return (
    <div className="relative">
      {/* 当前知识库显示 */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={loading}
        className="w-full flex items-center justify-between gap-2 p-3 rounded-lg bg-[var(--color-dark-700)] border border-[var(--color-border)] hover:bg-[var(--color-dark-600)] disabled:opacity-50 transition-colors"
      >
        <div className="flex items-center gap-2 min-w-0">
          <Database size={16} className="text-[var(--color-accent)] shrink-0" />
          <div className="flex-1 min-w-0 text-left">
            <div className="text-sm font-medium text-[var(--color-text-primary)] truncate">
              {currentKBInfo?.name || '未选择知识库'}
            </div>
            {currentKBInfo?.description && (
              <div className="text-xs text-[var(--color-text-muted)] truncate">
                {currentKBInfo.description}
              </div>
            )}
          </div>
        </div>
        <ChevronDown 
          size={16} 
          className={`text-[var(--color-text-secondary)] transition-transform ${isOpen ? 'rotate-180' : ''}`}
        />
      </button>

      {/* 知识库列表下拉 */}
      {isOpen && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-[var(--color-dark-700)] border border-[var(--color-border)] rounded-lg shadow-lg z-10 max-h-64 overflow-y-auto">
          {knowledgeBases.map(kb => (
            <button
              key={kb.id}
              onClick={() => switchKnowledgeBase(kb.id)}
              disabled={!kb.is_active || loading}
              className={`w-full flex items-center gap-3 p-3 text-left hover:bg-[var(--color-dark-600)] disabled:opacity-50 disabled:cursor-not-allowed transition-colors ${
                kb.id === currentKB ? 'bg-[var(--color-dark-600)]' : ''
              }`}
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-[var(--color-text-primary)] truncate">
                    {kb.name}
                  </span>
                  {!kb.is_active && (
                    <AlertCircle size={14} className="text-yellow-500 shrink-0" />
                  )}
                </div>
                {kb.description && (
                  <div className="text-xs text-[var(--color-text-muted)] truncate">
                    {kb.description}
                  </div>
                )}
              </div>
              {kb.id === currentKB && (
                <Check size={16} className="text-[var(--color-accent)] shrink-0" />
              )}
            </button>
          ))}
        </div>
      )}

      {/* 错误提示 */}
      {error && (
        <div className="mt-2 text-xs text-red-400">
          {error}
        </div>
      )}
    </div>
  );
}