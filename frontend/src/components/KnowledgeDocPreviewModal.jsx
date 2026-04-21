import { useEffect, useState, useCallback } from 'react';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { X, FileText, Loader2 } from 'lucide-react';
import { getKnowledgeDocument } from '../api';

const markdownComponents = {
  code({ className, children, ...props }) {
    const match = /language-(\w+)/.exec(className || '');
    const isBlock = String(children).includes('\n');
    if (match && isBlock) {
      return (
        <SyntaxHighlighter
          style={oneDark}
          language={match[1]}
          PreTag="div"
          customStyle={{ margin: 0, borderRadius: '6px', fontSize: '0.85em' }}
        >
          {String(children).replace(/\n$/, '')}
        </SyntaxHighlighter>
      );
    }
    return (
      <code className={className} {...props}>
        {children}
      </code>
    );
  },
};

/**
 * 全屏遮罩 + 居中「纸张」区域：模拟可滚动阅读的 PDF/文档视图
 */
export default function KnowledgeDocPreviewModal({ open, onClose, sourceRel, filename, title }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [payload, setPayload] = useState(null);

  const load = useCallback(async () => {
    if (!sourceRel && !filename) return;
    setLoading(true);
    setError(null);
    setPayload(null);
    try {
      const data = await getKnowledgeDocument(sourceRel || null, filename || null);
      setPayload(data);
    } catch (e) {
      setError(e.message || '加载失败');
    } finally {
      setLoading(false);
    }
  }, [sourceRel, filename]);

  useEffect(() => {
    if (!open) {
      setPayload(null);
      setError(null);
      return;
    }
    load();
  }, [open, load]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6 bg-black/65 backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-labelledby="kb-preview-title"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="flex flex-col w-full max-w-4xl max-h-[min(92vh,900px)] rounded-xl border border-[var(--color-border)] bg-[var(--color-dark-800)] shadow-2xl overflow-hidden">
        <header className="flex items-center justify-between gap-3 px-4 py-3 border-b border-[var(--color-border)] shrink-0">
          <div className="flex items-center gap-2 min-w-0">
            <FileText size={18} className="text-[var(--color-accent)] shrink-0" />
            <h2 id="kb-preview-title" className="text-sm font-medium text-[var(--color-text-primary)] truncate">
              {title || payload?.filename || '知识库文档'}
            </h2>
            {payload?.rel_path && (
              <span className="text-xs text-[var(--color-text-muted)] truncate hidden sm:inline max-w-[40%]">
                {payload.rel_path}
              </span>
            )}
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-[var(--color-dark-600)] text-[var(--color-text-muted)]"
            aria-label="关闭"
          >
            <X size={20} />
          </button>
        </header>

        <div className="flex-1 min-h-0 overflow-y-auto bg-[#e8e8ea]">
          {loading && (
            <div className="flex items-center justify-center gap-2 py-24 text-gray-600">
              <Loader2 className="animate-spin" size={22} />
              <span className="text-sm">加载文档…</span>
            </div>
          )}
          {error && !loading && (
            <div className="max-w-lg mx-auto my-16 px-6 text-sm text-red-800 bg-red-50 rounded-lg border border-red-200 py-4">
              {error}
            </div>
          )}
          {payload && !loading && (
            <div className="max-w-3xl mx-auto my-6 sm:my-10 px-4 sm:px-10 py-8 sm:py-12 bg-white text-gray-900 shadow-lg rounded-sm border border-gray-200/80 min-h-[60vh]">
              <div className="markdown-body markdown-paper-prose text-[15px] leading-relaxed">
                {payload.format === 'markdown' ? (
                  <Markdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
                    {payload.content}
                  </Markdown>
                ) : (
                  <pre className="whitespace-pre-wrap font-sans text-sm">{payload.content}</pre>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
