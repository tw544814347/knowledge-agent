import { useState, useRef, useEffect } from 'react';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Copy, Check, FileText, User, Bot, Brain, ChevronRight } from 'lucide-react';
import ThinkingIndicator from './ThinkingIndicator';

const markdownComponents = {
  code({ className, children, ...props }) {
    const match = /language-(\w+)/.exec(className || '');
    const isBlock = String(children).includes('\n');
    if (match && isBlock) {
      return (
        <SyntaxHighlighter style={oneDark} language={match[1]} PreTag="div" customStyle={{ margin: 0, borderRadius: '6px', fontSize: '0.85em' }}>
          {String(children).replace(/\n$/, '')}
        </SyntaxHighlighter>
      );
    }
    return <code className={className} {...props}>{children}</code>;
  },
};

export default function MessageBubble({ message }) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === 'user';
  const thinkDetailsRef = useRef(null);
  const thinkScrollRef = useRef(null);
  const wasAutoOpened = useRef(false);
  const wasAutoClosed = useRef(false);

  useEffect(() => {
    if (!thinkDetailsRef.current) return;
    if (message.thinking && !wasAutoOpened.current) {
      thinkDetailsRef.current.open = true;
      wasAutoOpened.current = true;
    }
    if (message.thinkingDone && !wasAutoClosed.current) {
      thinkDetailsRef.current.open = false;
      wasAutoClosed.current = true;
    }
  }, [message.thinking, message.thinkingDone]);

  useEffect(() => {
    if (thinkScrollRef.current && !message.thinkingDone) {
      thinkScrollRef.current.scrollTop = thinkScrollRef.current.scrollHeight;
    }
  }, [message.thinking, message.thinkingDone]);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const renderAIContent = () => {
    const hasVisibleContent = message.thinking || message.content;

    if (message.loading && !hasVisibleContent) {
      return <ThinkingIndicator startTime={message.thinkingStartTime} />;
    }

    return (
      <>
        {message.thinking && (
          <details ref={thinkDetailsRef} className="thinking-box mb-2">
            <summary className="flex items-center gap-1.5 text-xs cursor-pointer select-none py-1 text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)] transition-colors">
              <ChevronRight size={12} className="thinking-chevron transition-transform duration-200" />
              <Brain size={12} />
              <span>{message.thinkingDone ? '思考过程' : '思考中...'}</span>
              {!message.thinkingDone && <span className="thinking-dot-pulse">●</span>}
            </summary>
            <div
              ref={thinkScrollRef}
              className="thinking-scroll mt-1 max-h-36 overflow-y-auto text-xs leading-relaxed text-[var(--color-text-muted)] whitespace-pre-wrap pl-3 border-l-2 border-[var(--color-dark-500)]"
            >
              {message.thinking}
            </div>
          </details>
        )}

        {message.content ? (
          <div className="markdown-body">
            <Markdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
              {message.content}
            </Markdown>
            {message.loading && <span className="streaming-cursor" />}
          </div>
        ) : message.loading && message.thinkingDone ? (
          <span className="text-xs text-[var(--color-text-muted)] animate-pulse">等待生成...</span>
        ) : null}
      </>
    );
  };

  return (
    <div className={`msg-enter max-w-3xl mx-auto mb-5 ${isUser ? 'flex justify-end' : ''}`}>
      <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''} max-w-[85%]`}>
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 mt-0.5 ${isUser ? 'bg-[var(--color-user-bubble)]' : 'bg-[var(--color-dark-600)]'}`}>
          {isUser ? <User size={16} className="text-white" /> : <Bot size={16} className="text-[var(--color-accent)]" />}
        </div>

        <div className="min-w-0 flex-1">
          <div className={`rounded-xl px-4 py-3 text-sm leading-relaxed ${
            isUser
              ? 'bg-[var(--color-user-bubble)] text-white'
              : 'bg-[var(--color-dark-700)] text-[var(--color-text-primary)]'
          } ${message.error ? 'border border-red-500/40' : ''}`}>
            {isUser ? (
              <p className="whitespace-pre-wrap">{message.content}</p>
            ) : (
              renderAIContent()
            )}
          </div>

          {!isUser && message.sources?.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1.5">
              {message.sources.map((s, i) => (
                <span
                  key={i}
                  className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs bg-[var(--color-dark-600)] text-[var(--color-text-muted)] border border-[var(--color-border)]"
                  title={`${s.filename} [${s.category}] 相关度: ${s.score?.toFixed(2)}`}
                >
                  <FileText size={10} />
                  {s.filename}
                  {s.score > 0 && <span className="text-[var(--color-accent)] ml-0.5">{(s.score * 100).toFixed(0)}%</span>}
                </span>
              ))}
            </div>
          )}

          {!isUser && !message.loading && message.content && (
            <div className="mt-1.5 flex items-center gap-2">
              <button
                onClick={handleCopy}
                className="flex items-center gap-1 text-xs text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)] transition-colors"
              >
                {copied ? <><Check size={12} /> 已复制</> : <><Copy size={12} /> 复制</>}
              </button>
              <span className="text-xs text-[var(--color-text-muted)]">
                {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
