import { useState } from 'react';
import { X } from 'lucide-react';

export default function AskModal({ question, options, onClose, onSelect }) {
  const [selectedOption, setSelectedOption] = useState(null);

  const handleSelect = (option, index) => {
    setSelectedOption(index);
    onSelect(option, index);
  };

  if (!question || !options || options.length === 0) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-[var(--color-dark-800)] border border-[var(--color-border)] rounded-xl max-w-md w-full mx-4 max-h-[80vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-[var(--color-border)]">
          <h2 className="text-lg font-semibold text-[var(--color-text-primary)]">
            系统询问
          </h2>
          <button
            onClick={onClose}
            className="p-1 rounded hover:bg-[var(--color-dark-600)] text-[var(--color-text-secondary)]"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 overflow-y-auto">
          {/* Question with markdown support */}
          <div className="mb-6">
            <div 
              className="text-[var(--color-text-primary)] markdown-body"
              dangerouslySetInnerHTML={{ 
                __html: question.replace(/\n/g, '<br/>') 
              }}
            />
          </div>

          {/* Options */}
          <div className="space-y-2">
            {options.map((option, index) => (
              <button
                key={index}
                onClick={() => handleSelect(option, index)}
                className={`w-full text-left p-3 rounded-lg border transition-all duration-200 ${
                  selectedOption === index
                    ? 'bg-[var(--color-accent)] border-[var(--color-accent)] text-white'
                    : 'bg-[var(--color-dark-700)] border-[var(--color-border)] text-[var(--color-text-primary)] hover:bg-[var(--color-dark-600)] hover:border-[var(--color-accent-dim)]'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span className={`w-6 h-6 rounded-full border-2 flex items-center justify-center text-xs font-medium ${
                    selectedOption === index
                      ? 'border-white bg-white text-[var(--color-accent)]'
                      : 'border-[var(--color-text-muted)] text-[var(--color-text-muted)]'
                  }`}>
                    {index + 1}
                  </span>
                  <span className="flex-1">{option}</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Footer - Optional */}
        <div className="p-4 border-t border-[var(--color-border)] bg-[var(--color-dark-700)]">
          <p className="text-xs text-[var(--color-text-muted)] text-center">
            点击选项进行选择
          </p>
        </div>
      </div>
    </div>
  );
}