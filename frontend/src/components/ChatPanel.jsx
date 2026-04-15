import { useState, useRef, useEffect, useCallback } from 'react';
import { Send, PanelLeftOpen, Square } from 'lucide-react';
import MessageBubble from './MessageBubble';
import { askQuestionStream } from '../api';

export default function ChatPanel({ isConnected, onToggleSidebar, sidebarOpen }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);
  const abortRef = useRef(null);
  const pendingQuestionRef = useRef('');
  const pendingMsgIdsRef = useRef({ userId: null, aiId: null });
  const rafRef = useRef(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 150) + 'px';
    }
  }, [input]);

  const handleStop = useCallback(() => {
    if (abortRef.current) {
      abortRef.current.abort();
      abortRef.current = null;
    }
    if (rafRef.current) {
      cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
    }

    const { userId, aiId } = pendingMsgIdsRef.current;
    setMessages(prev => prev.filter(m => m.id !== userId && m.id !== aiId));
    setInput(pendingQuestionRef.current);
    setLoading(false);
    pendingQuestionRef.current = '';
    pendingMsgIdsRef.current = { userId: null, aiId: null };

    setTimeout(() => textareaRef.current?.focus(), 50);
  }, []);

  const handleSend = async () => {
    const question = input.trim();
    if (!question || loading || !isConnected) return;

    const userId = `u_${Date.now()}`;
    const aiMsgId = `a_${Date.now()}`;
    const controller = new AbortController();

    abortRef.current = controller;
    pendingQuestionRef.current = question;
    pendingMsgIdsRef.current = { userId, aiId: aiMsgId };

    setMessages(prev => [...prev, {
      id: userId, role: 'user', content: question, timestamp: new Date(),
    }]);
    setInput('');
    setLoading(true);

    setMessages(prev => [...prev, {
      id: aiMsgId, role: 'assistant', content: '', sources: [],
      timestamp: new Date(), loading: true, streaming: false,
      thinking: '', thinkingDone: false, thinkingStartTime: Date.now(),
    }]);

    const rawContent = { current: '' };

    const flushRender = () => {
      const raw = rawContent.current;
      let thinking = '', answer = '', thinkingDone = false;

      const ts = raw.indexOf('<think>');
      const te = raw.indexOf('</think>');

      if (ts !== -1) {
        if (te !== -1) {
          thinking = raw.substring(ts + 7, te).trim();
          answer = raw.substring(te + 8).trim();
          thinkingDone = true;
        } else {
          thinking = raw.substring(ts + 7).trim();
        }
      } else {
        answer = raw.trim();
        thinkingDone = true;
      }

      setMessages(prev => prev.map(m => m.id === aiMsgId ? {
        ...m, thinking, thinkingDone, content: answer, streaming: true,
      } : m));
    };

    try {
      await askQuestionStream(question, 8, controller.signal, (chunk) => {
        if (chunk.type === 'sources') {
          setMessages(prev => prev.map(m => m.id === aiMsgId ? {
            ...m, sources: chunk.sources,
          } : m));
        } else if (chunk.type === 'token') {
          rawContent.current += chunk.content;
          if (!rafRef.current) {
            rafRef.current = requestAnimationFrame(() => {
              rafRef.current = null;
              flushRender();
            });
          }
        } else if (chunk.type === 'done') {
          if (rafRef.current) { cancelAnimationFrame(rafRef.current); rafRef.current = null; }
          flushRender();
          setMessages(prev => prev.map(m => m.id === aiMsgId ? {
            ...m, loading: false, thinkingDone: true,
          } : m));
        } else if (chunk.type === 'error') {
          if (rafRef.current) { cancelAnimationFrame(rafRef.current); rafRef.current = null; }
          setMessages(prev => prev.map(m => m.id === aiMsgId ? {
            ...m, content: `请求失败：${chunk.message}`, loading: false, error: true,
          } : m));
        }
      });
    } catch (err) {
      if (err.name === 'AbortError') return;
      setMessages(prev => prev.map(m => m.id === aiMsgId ? {
        ...m, content: `请求失败：${err.message}`, loading: false, error: true,
      } : m));
    } finally {
      if (rafRef.current) { cancelAnimationFrame(rafRef.current); rafRef.current = null; }
      if (!controller.signal.aborted) {
        setLoading(false);
        abortRef.current = null;
        pendingQuestionRef.current = '';
        pendingMsgIdsRef.current = { userId: null, aiId: null };
      }
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <header className="flex items-center gap-3 px-4 py-3 border-b border-[var(--color-border)] bg-[var(--color-dark-800)]">
        {!sidebarOpen && (
          <button onClick={onToggleSidebar} className="p-1.5 rounded-lg hover:bg-[var(--color-dark-600)] text-[var(--color-text-secondary)]">
            <PanelLeftOpen size={18} />
          </button>
        )}
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-sm text-[var(--color-text-secondary)]">知识库问答</span>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 rounded-2xl bg-[var(--color-dark-700)] flex items-center justify-center mb-4">
              <span className="text-3xl">🧠</span>
            </div>
            <h2 className="text-lg font-medium text-[var(--color-text-primary)] mb-1">知识库 Agent</h2>
            <p className="text-sm text-[var(--color-text-muted)] max-w-sm">
              基于 DeepSeek R1 + RAG 的智能问答系统，输入你的问题开始对话。
            </p>
            <div className="mt-6 flex flex-wrap gap-2 justify-center max-w-md">
              {['Multi-Agent 和 Workflow 有什么区别？', 'RAG 系统有哪些挑战？', 'Cursor 有什么使用技巧？'].map(q => (
                <button
                  key={q}
                  onClick={() => { setInput(q); textareaRef.current?.focus(); }}
                  className="px-3 py-1.5 text-xs rounded-full border border-[var(--color-border)] text-[var(--color-text-secondary)] hover:bg-[var(--color-dark-700)] hover:text-[var(--color-text-primary)] transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map(msg => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-[var(--color-border)] bg-[var(--color-dark-800)] p-4">
        <div className="max-w-3xl mx-auto flex items-end gap-3 bg-[var(--color-dark-700)] rounded-xl px-4 py-3 border border-[var(--color-border)] focus-within:border-[var(--color-accent-dim)] transition-colors">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={isConnected ? '输入你的问题...' : '后端服务未连接...'}
            disabled={!isConnected || loading}
            rows={1}
            className="flex-1 bg-transparent resize-none text-sm text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] outline-none disabled:opacity-40 max-h-[150px]"
          />
          {loading ? (
            <button
              onClick={handleStop}
              className="p-2 rounded-lg bg-red-600/80 hover:bg-red-500 text-white transition-colors shrink-0"
              title="停止生成"
            >
              <Square size={18} fill="currentColor" />
            </button>
          ) : (
            <button
              onClick={handleSend}
              disabled={!input.trim() || !isConnected}
              className="p-2 rounded-lg bg-[var(--color-accent-dim)] hover:bg-[var(--color-accent)] text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors shrink-0"
            >
              <Send size={18} />
            </button>
          )}
        </div>
        <div className="max-w-3xl mx-auto mt-2 flex justify-between text-xs text-[var(--color-text-muted)]">
          <span>{loading ? '生成中... 点击红色按钮可停止' : 'Enter 发送 · Shift+Enter 换行'}</span>
          <span>DeepSeek R1 14B · Local</span>
        </div>
      </div>
    </div>
  );
}
