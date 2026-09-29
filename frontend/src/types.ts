// Interface for analysis metrics
export interface AnalysisMetrics {
  wordCount: number;
  sentenceCount: number;
  burstinessScore: number;
  clicheCount: number;
  humanScore: number;
  verdictText: string;
  flaggedSentences?: string[];
}

// Interface for server configuration
export interface ServerConfiguration {
  modelName: string;
  hasServerKey: boolean;
  hasServerUrl: boolean;
  providerUrl: string;
}

// Interface for humanization request payload
export interface HumanizePayload {
  sourceText: string;
  toneValue: string;
  modeValue?: 'fast' | 'deep';
  modelName?: string;
  providerUrl?: string;
  apiKey?: string;
}

// Interface for humanization response payload
export interface HumanizeResponse {
  resultText: string;
  resultAnalysis: AnalysisMetrics;
}
