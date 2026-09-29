import { AnalysisMetrics, HumanizePayload, HumanizeResponse, ServerConfiguration } from '../types';

// Pure service functions for API calls
export const apiService = {
  // Fetch server configuration
  async fetchConfig(): Promise<ServerConfiguration> {
    const responseObject = await fetch('/api/config');
    if (!responseObject.ok) {
      throw new Error(`Failed to fetch configuration: ${responseObject.statusText}`);
    }
    return responseObject.json();
  },

  // Request text analysis
  async analyzeContent(sourceText: string): Promise<AnalysisMetrics> {
    const responseObject = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sourceText }),
    });

    if (!responseObject.ok) {
      const errorData = await responseObject.json();
      throw new Error(errorData.detail || 'Analysis request failed');
    }

    const responseData = await responseObject.json();
    return responseData.analysisData;
  },

  // Request text humanization with claude-opus-5
  async humanizeContent(payloadData: HumanizePayload): Promise<HumanizeResponse> {
    const responseObject = await fetch('/api/humanize', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payloadData),
    });

    if (!responseObject.ok) {
      const errorData = await responseObject.json();
      throw new Error(errorData.detail || 'Humanization request failed');
    }

    return responseObject.json();
  },
};
