import React, { useState } from 'react';
import { Copy, Check, RotateCcw } from 'lucide-react';
import { AnalysisMetrics } from '../types';
import { ScoreMeter } from './ScoreMeter';

interface EditorCardProps {
  cardTitle: string;
  textContent: string;
  onTextChange?: (updatedText: string) => void;
  isReadOnly?: boolean;
  placeholderText: string;
  metricsData: AnalysisMetrics | null;
  onClearText?: () => void;
  onLoadSample?: () => void;
}

export const EditorCard: React.FC<EditorCardProps> = ({
  cardTitle,
  textContent,
  onTextChange,
  isReadOnly = false,
  placeholderText,
  metricsData,
  onClearText,
  onLoadSample,
}) => {
  const [isCopied, setIsCopied] = useState<boolean>(false);

  // Copy text to clipboard
  const handleCopy = async () => {
    if (!textContent) return;
    await navigator.clipboard.writeText(textContent);
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 1800);
  };

  const wordCount = textContent.trim() ? textContent.trim().split(/\s+/).length : 0;
  const charCount = textContent.length;

  return (
    <div className="flex flex-col bg-white border border-stone-200/90 rounded-2xl overflow-hidden shadow-xs focus-within:border-stone-400 focus-within:ring-3 focus-within:ring-stone-200/60 transition-all">
      {/* Editor toolbar with unified fixed height */}
      <div className="flex items-center justify-between px-5 h-14 border-b border-stone-200/80 bg-stone-50/70">
        <span className="text-xs font-bold uppercase tracking-wider text-stone-700">
          {cardTitle}
        </span>

        <div className="flex items-center gap-2 min-h-[36px]">
          {onLoadSample && !textContent && (
            <button
              onClick={onLoadSample}
              className="text-xs font-medium text-stone-700 hover:text-stone-950 px-3.5 py-1.5 rounded-full border border-stone-200 bg-white hover:bg-stone-50 shadow-xs transition-colors"
            >
              Insert sample
            </button>
          )}

          {onClearText && textContent && (
            <button
              onClick={onClearText}
              className="w-9 h-9 rounded-full flex items-center justify-center border border-stone-200 bg-white hover:bg-stone-50 text-stone-500 hover:text-stone-900 shadow-xs transition-colors"
              title="Clear text"
            >
              <RotateCcw className="w-4 h-4" strokeWidth={1.5} />
            </button>
          )}

          {/* Dedicated circular copy button */}
          {textContent && (
            <button
              onClick={handleCopy}
              className="w-9 h-9 rounded-full flex items-center justify-center border border-stone-200 bg-white hover:bg-stone-50 text-stone-600 hover:text-stone-950 shadow-xs active:scale-95 transition-all"
              title="Copy to clipboard"
            >
              {isCopied ? (
                <Check className="w-4 h-4 text-emerald-600" strokeWidth={2} />
              ) : (
                <Copy className="w-4 h-4 text-stone-600" strokeWidth={1.5} />
              )}
            </button>
          )}
        </div>
      </div>

      {/* Editor display area: strictly non-editable display for Output, textarea for Input */}
      <div className="flex-1 min-h-[460px] p-6 flex overflow-y-auto">
        {isReadOnly ? (
          <div className="w-full h-full text-stone-900 text-base leading-relaxed font-normal whitespace-pre-wrap select-text selection:bg-stone-200">
            {textContent || (
              <span className="text-stone-400 select-none font-normal">
                {placeholderText}
              </span>
            )}
          </div>
        ) : (
          <textarea
            value={textContent}
            onChange={(event) => onTextChange && onTextChange(event.target.value)}
            placeholder={placeholderText}
            className="w-full h-full bg-transparent resize-none outline-none text-stone-900 text-base leading-relaxed placeholder:text-stone-400 font-normal selection:bg-stone-200"
          />
        )}
      </div>

      {/* Simple metrics footer */}
      <ScoreMeter
        metricsData={metricsData}
        cardTitle={cardTitle}
        wordCount={wordCount}
        charCount={charCount}
      />
    </div>
  );
};
