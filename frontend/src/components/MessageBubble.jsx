import { useState, useRef, useEffect } from 'react';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Copy, Check, FileText, User, Brain, ChevronRight, ThumbsUp, Globe, ExternalLink } from 'lucide-react';

const TAGENT_AVATAR_SRC = '/branding/tagent-avatar.png';
import ThinkingIndicator from './ThinkingIndicator';
import KnowledgeDocPreviewModal from './KnowledgeDocPreviewModal';

/** 网络来源：优先 web_url，旧数据可能仅在 section 存 URL */
function pickWebHref(source) {
  const wu = (source.web_url || '').trim();
  if (wu) {
    try {
      const u = new URL(wu);
      if (u.protocol === 'http:' || u.protocol === 'https:') return u.href;
    } catch {
      /* ignore */
    }
  }
  const sec = (source.section || '').trim();
  if (/^https?:\/\//i.test(sec)) {
    try {
      const u = new URL(sec);
      if (u.protocol === 'http:' || u.protocol === 'https:') return u.href;
    } catch {
      /* ignore */
    }
  }
  return null;
}

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

export default function MessageBubble({ message, onLike }) {
  const [copied, setCopied] = useState(false);
  const [likeBusy, setLikeBusy] = useState(false);
  const [docPreview, setDocPreview] = useState(null);
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

  const canLike =
    onLike &&
    message.role === 'assistant' &&
    message.conversationId != null &&
    message.messageIndex != null &&
    !message.loading &&
    message.content &&
    !message.error;

  const handleLike = async () => {
    if (!canLike || likeBusy) return;
    setLikeBusy(true);
    try {
      await onLike(message, !message.liked);
    } finally {
      setLikeBusy(false);
    }
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
        <div
          className={`w-8 h-8 shrink-0 mt-0.5 overflow-hidden flex items-center justify-center ${
            isUser ? 'rounded-lg bg-[var(--color-user-bubble)]' : 'rounded-full bg-black ring-1 ring-[var(--color-border)]'
          }`}
        >
          {isUser ? (
            <User size={16} className="text-white" />
          ) : (
            <img
              src={TAGENT_AVATAR_SRC}
              alt="Tagent"
              className="h-full w-full object-cover"
              width={32}
              height={32}
              decoding="async"
            />
          )}
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
              {message.sources.map((s, i) => {
                const isWeb = s.category === '网络';
                const webHref = isWeb ? pickWebHref(s) : null;
                const canPreviewKb = !isWeb && !!(s.source_rel || s.filename);
                const chipTitle = isWeb
                  ? (webHref ? `${s.filename}\n${webHref}` : s.section ? `${s.filename}\n${s.section}` : s.filename)
                  : `${s.filename}${s.section ? ` · ${s.section}` : ''}${s.score > 0 ? ` · 相关度 ${(s.score * 100).toFixed(0)}%` : ''}${canPreviewKb ? '' : '（无法打开：缺少文件路径）'}`;

                if (isWeb && webHref) {
                  return (
                    <button
                      key={i}
                      type="button"
                      onClick={() => window.open(webHref, '_blank', 'noopener,noreferrer')}
                      title={chipTitle}
                      className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs bg-[var(--color-dark-600)] text-[var(--color-accent)] border border-[var(--color-accent)]/40 hover:bg-[var(--color-accent)]/15 transition-colors cursor-pointer"
                    >
                      <Globe size={10} />
                      <span className="truncate max-w-[200px]">{s.filename}</span>
                      <ExternalLink size={10} className="opacity-80 shrink-0" />
                    </button>
                  );
                }

                if (isWeb && !webHref) {
                  return (
                    <span
                      key={i}
                      title={chipTitle}
                      className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs bg-[var(--color-dark-600)] text-[var(--color-text-muted)] border border-[var(--color-border)] opacity-80"
                    >
                      <Globe size={10} />
                      <span className="truncate max-w-[200px]">{s.filename}</span>
                    </span>
                  );
                }

                return (
                  <button
                    key={i}
                    type="button"
                    disabled={!canPreviewKb}
                    onClick={() =>
                      canPreviewKb &&
                      setDocPreview({
                        sourceRel: s.source_rel || null,
                        filename: s.source_rel ? null : s.filename,
                        title: s.filename,
                      })
                    }
                    title={canPreviewKb ? `${chipTitle}\n点击在弹窗中阅读全文` : chipTitle}
                    className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs border border-[var(--color-border)] transition-colors ${
                      canPreviewKb
                        ? 'bg-[var(--color-dark-600)] text-[var(--color-text-secondary)] hover:bg-[var(--color-dark-500)] hover:text-[var(--color-text-primary)] cursor-pointer'
                        : 'bg-[var(--color-dark-600)] text-[var(--color-text-muted)] opacity-50 cursor-not-allowed'
                    }`}
                  >
                    <FileText size={10} />
                    <span className="truncate max-w-[220px]">{s.filename}</span>
                    {s.score > 0 && (
                      <span className="text-[var(--color-accent)] ml-0.5 shrink-0">{(s.score * 100).toFixed(0)}%</span>
                    )}
                  </button>
                );
              })}
            </div>
          )}

          {!isUser && !message.loading && message.content && (
            <div className="mt-1.5 flex items-center gap-2 flex-wrap">
              <button
                onClick={handleCopy}
                className="flex items-center gap-1 text-xs text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)] transition-colors"
              >
                {copied ? <><Check size={12} /> 已复制</> : <><Copy size={12} /> 复制</>}
              </button>
              {canLike && (
                <button
                  type="button"
                  onClick={handleLike}
                  disabled={likeBusy}
                  title={message.liked ? '取消点赞' : '满意，加入语料库'}
                  className={`flex items-center gap-1 text-xs transition-colors disabled:opacity-40 ${
                    message.liked
                      ? 'text-[var(--color-accent)]'
                      : 'text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)]'
                  }`}
                >
                  <ThumbsUp size={12} className={message.liked ? 'fill-current' : ''} />
                  {message.liked ? '已点赞' : '点赞'}
                </button>
              )}
              <span className="text-xs text-[var(--color-text-muted)]">
                {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
              {message.generationTime && (
                <span className="text-xs text-[var(--color-text-muted)]">
                  耗时 {message.generationTime.toFixed(1)}s
                </span>
              )}
            </div>
          )}
        </div>
      </div>

      <KnowledgeDocPreviewModal
        open={docPreview != null}
        onClose={() => setDocPreview(null)}
        sourceRel={docPreview?.sourceRel}
        filename={docPreview?.filename}
        title={docPreview?.title}
      />
    </div>
  );
}
