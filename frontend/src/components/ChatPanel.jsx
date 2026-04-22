import { useState, useRef, useEffect, useCallback } from 'react';
import { Send, PanelLeftOpen, Square, Globe } from 'lucide-react';
import MessageBubble from './MessageBubble';
import { askQuestionStream, setMessageLike } from '../api';

const INTERFACE_LOGO_SRC = `${import.meta.env.BASE_URL}branding/tagent-interface-logo.png`;

const EMPTY_STATE_SUGGESTIONS = [
  { tag: '📖 入门', q: '我可以问你哪些问题？' },
  { tag: '🧠 专业', q: 'Multi-Agent 和 Workflow 有什么区别？' },
  { tag: '🌐 联网', q: '结合知识库和最新资讯，帮我做一份竞品对比' },
];

export default function ChatPanel({ 
  isConnected, 
  onToggleSidebar, 
  sidebarOpen, 
  selectedConversation,
  draftSessionKey = 0,
  user,
  onLogin,
  onConversationSaved 
}) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [webSearchOn, setWebSearchOn] = useState(false);
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

  // 切换会话、或点击「新对话」递增 draftSessionKey 时：中止流式请求并同步消息区
  useEffect(() => {
    if (abortRef.current) {
      abortRef.current.abort();
      abortRef.current = null;
    }
    if (rafRef.current) {
      cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
    }
    pendingQuestionRef.current = '';
    pendingMsgIdsRef.current = { userId: null, aiId: null };
    setLoading(false);

    if (selectedConversation) {
      // 处理不同的数据结构：置顶对话使用messages数组，普通对话使用message对象
      let conversationMessages = [];
      
      if (selectedConversation.messages && Array.isArray(selectedConversation.messages)) {
        // 置顶对话：有多条消息的情况
        selectedConversation.messages.forEach((msg, index) => {
          const userMsg = {
            id: `u_${Date.now()}_${index}`,
            role: 'user',
            content: msg.question,
            timestamp: new Date(msg.created_at || selectedConversation.created_at),
          };
          
          const aiMsg = {
            id: `a_${Date.now()}_${index}`,
            role: 'assistant',
            content: msg.answer,
            sources: msg.sources || [],
            timestamp: new Date(msg.created_at || selectedConversation.created_at),
            loading: false,
            streaming: false,
            thinking: '',
            thinkingDone: true,
            conversationId: selectedConversation.id,
            messageIndex: index,
            liked: !!msg.liked,
          };
          
          conversationMessages.push(userMsg, aiMsg);
        });
      } else if (selectedConversation.message) {
        // 普通对话：单条消息的情况
        const userMsg = {
          id: `u_${Date.now()}`,
          role: 'user',
          content: selectedConversation.message.question,
          timestamp: new Date(selectedConversation.created_at),
        };
        
        const aiMsg = {
          id: `a_${Date.now()}`,
          role: 'assistant',
          content: selectedConversation.message.answer,
          sources: selectedConversation.message.sources || [],
          timestamp: new Date(selectedConversation.created_at),
          loading: false,
          streaming: false,
          thinking: '',
          thinkingDone: true,
          conversationId: selectedConversation.id,
          messageIndex: 0,
          liked: !!selectedConversation.message?.liked,
        };
        
        conversationMessages = [userMsg, aiMsg];
      }
      
      setMessages(conversationMessages);
      setInput('');
    } else {
      // 未选中历史会话：空白草稿（含引导区）；draftSessionKey 变化时也会进入此分支以清空进行中的草稿
      setMessages([]);
      setInput('');
    }
  }, [selectedConversation, draftSessionKey]);

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
    if (!question || loading || !isConnected || !user) return;

    const userId = `u_${Date.now()}`;
    const aiMsgId = `a_${Date.now()}`;
    const startTime = Date.now(); // 记录开始时间
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
      generationStartTime: startTime, // 记录生成开始时间
      liked: false,
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
      // 如果有选中的对话，传递conversation_id以在该对话中添加消息
      const conversationId = selectedConversation?.id || null;
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
          const endTime = Date.now();
          setMessages(prev => prev.map(m => m.id === aiMsgId ? {
            ...m, 
            loading: false, 
            thinkingDone: true,
            generationTime: m.generationStartTime ? (endTime - m.generationStartTime) / 1000 : null, // 计算耗时（秒）
          } : m));
          
          // 通知父组件对话已完成（后端会自动保存到历史记录）
          setTimeout(() => {
            try {
              const finalMessage = [...messages].find(m => m.id === aiMsgId);
              if (finalMessage && finalMessage.content && !finalMessage.error) {
                // 触发对话历史刷新（由于后端自动保存，前端只需要刷新显示）
                onConversationSaved?.({ 
                  id: 'auto_saved', 
                  title: question.slice(0, 30),
                  refresh: true 
                });
              }
            } catch (error) {
              console.error('通知对话完成失败:', error);
            }
          }, 500);
        } else if (chunk.type === 'conversation_saved') {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === aiMsgId
                ? {
                    ...m,
                    conversationId: chunk.conversation_id,
                    messageIndex: chunk.message_index,
                    liked: m.liked ?? false,
                  }
                : m
            )
          );
        } else if (chunk.type === 'error') {
          if (rafRef.current) { cancelAnimationFrame(rafRef.current); rafRef.current = null; }
          setMessages(prev => prev.map(m => m.id === aiMsgId ? {
            ...m, content: `请求失败：${chunk.message}`, loading: false, error: true,
          } : m));
        }
      }, conversationId, webSearchOn);
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

  const handleLikeToggle = async (message, nextLiked) => {
    if (!user || message.conversationId == null || message.messageIndex == null) return;
    try {
      await setMessageLike(message.conversationId, message.messageIndex, nextLiked);
      setMessages((prev) =>
        prev.map((m) => (m.id === message.id ? { ...m, liked: nextLiked } : m))
      );
      onConversationSaved?.({ refresh: true });
    } catch (err) {
      console.error('点赞失败:', err);
    }
  };

  return (
    <div className="flex flex-col h-full bg-[var(--color-chat-bg)]">
      {/* Header */}
      <header className="flex items-center gap-3 px-4 py-3 border-b border-[var(--color-border)] bg-[var(--color-dark-800)]">
        {!sidebarOpen && (
          <button onClick={onToggleSidebar} className="p-1.5 rounded-lg hover:bg-[var(--color-dark-600)] text-[var(--color-text-secondary)]">
            <PanelLeftOpen size={18} />
          </button>
        )}
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-sm text-[var(--color-text-secondary)]">Tagent - 你身边的专属知识智能专家</span>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto bg-[var(--color-chat-bg)] px-4 py-6">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <img
              src={INTERFACE_LOGO_SRC}
              alt="Tagent"
              className="max-w-[min(80%,260px)] w-auto h-auto object-contain mb-4 select-none"
              decoding="async"
            />
            <h2 className="text-lg font-medium text-[var(--color-text-primary)] mb-2">Tagent</h2>
            <p className="text-sm text-[var(--color-text-muted)] max-w-sm leading-relaxed">
              你的专属知识智能专家。支持私有知识库检索、专业问题推理，必要时联网搜索最新资讯。
            </p>
            {!user && (
              <button
                onClick={onLogin}
                className="mt-4 px-6 py-2 rounded-lg bg-[var(--color-accent)] hover:bg-[var(--color-accent-dim)] text-white transition-colors"
              >
                登录 / 注册
              </button>
            )}
            <div className="mt-6 flex flex-col gap-2 w-full max-w-sm">
              {EMPTY_STATE_SUGGESTIONS.map(({ tag, q }) => (
                <button
                  key={q}
                  onClick={() => { setInput(q); textareaRef.current?.focus(); }}
                  className="flex items-center gap-2 px-3 py-2 text-xs rounded-lg border border-[var(--color-border)] text-[var(--color-text-secondary)] hover:bg-[var(--color-dark-700)] hover:text-[var(--color-text-primary)] transition-colors text-left"
                >
                  <span className="shrink-0 text-[var(--color-text-muted)]">{tag}</span>
                  <span className="truncate">{q}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <MessageBubble
            key={msg.id}
            message={msg}
            onLike={user ? handleLikeToggle : undefined}
          />
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* 已选历史会话或已与后端绑定的线程：展示当前问答对（pair）数量 */}
      {user &&
        messages.length > 0 &&
        (selectedConversation ||
          messages.some((m) => m.role === 'assistant' && m.conversationId)) && (
          <div className="shrink-0 border-t border-[var(--color-border)] bg-[var(--color-dark-800)] px-4 py-2">
            <div className="max-w-3xl mx-auto text-center text-xs text-[var(--color-text-muted)]">
              当前对话共{' '}
              <span className="text-[var(--color-text-secondary)] font-medium tabular-nums">
                {messages.filter((m) => m.role === 'user').length}
              </span>{' '}
              个问答对（pair）
              <span className="opacity-70"> · 单会话最多保存 50 对</span>
            </div>
          </div>
        )}

      {/* Input */}
      <div className="border-t border-[var(--color-border)] bg-[var(--color-dark-800)] p-4">
        <div className="max-w-3xl mx-auto flex items-end gap-2 bg-[var(--color-dark-700)] rounded-xl px-3 py-3 border border-[var(--color-border)] focus-within:border-[var(--color-accent-dim)] transition-colors">
          <button
            type="button"
            onClick={() => setWebSearchOn((v) => !v)}
            disabled={!user || !isConnected || loading}
            title={
              webSearchOn
                ? '已开启：知识库无命中时将自动联网检索并合并回答'
                : '关闭：仅使用知识库'
            }
            className={`mb-0.5 flex shrink-0 flex-col items-center justify-center gap-0.5 rounded-lg px-2 py-1.5 text-[10px] leading-tight transition-colors disabled:cursor-not-allowed disabled:opacity-30 ${
              webSearchOn
                ? 'bg-[var(--color-accent)]/25 text-[var(--color-accent)] ring-1 ring-[var(--color-accent)]/50'
                : 'text-[var(--color-text-muted)] hover:bg-[var(--color-dark-600)] hover:text-[var(--color-text-secondary)]'
            }`}
          >
            <Globe size={18} strokeWidth={webSearchOn ? 2.25 : 1.75} />
            <span className="whitespace-nowrap">联网搜索</span>
          </button>
          <textarea
            ref={textareaRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              !user ? '请先登录后开始对话...' :
              !isConnected ? '后端服务未连接...' :
              '输入你的问题...'
            }
            disabled={!user || !isConnected || loading}
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
              disabled={!input.trim() || !isConnected || !user}
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
