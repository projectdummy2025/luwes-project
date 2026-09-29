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
    <div className="py-2.5 px-5 bg-stone-50/70 border-t border-stone-200/80 flex items-center justify-between text-xs text-stone-500 font-mono">
      {/* Simple word and character counter */}
      <div className="flex items-center gap-2">
        <span>{wordCount} {wordCount === 1 ? 'word' : 'words'}</span>
        <span className="text-stone-300">·</span>
        <span>{charCount} {charCount === 1 ? 'char' : 'chars'}</span>
      </div>

      {/* Simple score percentage without progress bar */}
      {metricsData && metricsData.humanScore > 0 && (
        <div className="flex items-center gap-1.5 font-sans text-xs">
          <span className="text-stone-400">Score:</span>
          <span className="font-semibold font-mono text-stone-800">
            {metricsData.humanScore}%
          </span>
        </div>
      )}
    </div>
  );
};
