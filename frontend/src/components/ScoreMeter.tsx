import React from 'react';
import { AnalysisMetrics } from '../types';

interface ScoreMeterProps {
  metricsData: AnalysisMetrics | null;
  cardTitle: string;
  wordCount: number;
  charCount: number;
}

export const ScoreMeter: React.FC<ScoreMeterProps> = ({
  metricsData,
  wordCount,
  charCount,
}) => {
  return (
    <div className="py-2.5 px-5 bg-stone-50/70 border-t border-stone-200/80 flex items-center justify-between gap-3 text-xs text-stone-500 font-mono">
      {/* Show document size without implying authorship certainty */}
      <div className="flex items-center gap-2 shrink-0">
        <span>{wordCount} {wordCount === 1 ? 'word' : 'words'}</span>
        <span className="text-stone-300">·</span>
        <span>{charCount} {charCount === 1 ? 'char' : 'chars'}</span>
      </div>

      {/* Show transparent lint status instead of an unsupported human score */}
      {metricsData && (
        <div className="flex items-center gap-2 font-sans text-xs text-right">
          <span className="text-stone-500">{metricsData.verdictText}</span>
          <span className="text-stone-300">·</span>
          <span className="font-mono text-stone-700">
            {metricsData.clicheCount} {metricsData.clicheCount === 1 ? 'style flag' : 'style flags'}
          </span>
        </div>
      )}
    </div>
  );
};
