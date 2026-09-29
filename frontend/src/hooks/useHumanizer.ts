import { useState, useEffect } from 'react';
import { AnalysisMetrics } from '../types';
import { apiService } from '../services/apiService';

// Custom hook to manage humanizer state and actions
export function useHumanizer() {
  // Text input and output states
  const [sourceText, setSourceText] = useState<string>('');
  const [resultText, setResultText] = useState<string>('');

  // Selected tone style
  const [toneValue, setToneValue] = useState<string>('natural');

  // Metrics analysis states
  const [sourceAnalysis, setSourceAnalysis] = useState<AnalysisMetrics | null>(null);
  const [resultAnalysis, setResultAnalysis] = useState<AnalysisMetrics | null>(null);

  // Settings states stored in local storage
  const [providerUrl, setProviderUrl] = useState<string>(() => localStorage.getItem('providerUrl') || '');
  const [apiKey, setApiKey] = useState<string>(() => localStorage.getItem('apiKey') || '');

  // UI status states
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

  // Sync settings to local storage
  useEffect(() => {
    localStorage.setItem('providerUrl', providerUrl);
  }, [providerUrl]);

  useEffect(() => {
    localStorage.setItem('apiKey', apiKey);
  }, [apiKey]);

  // Load server config on initial mount
  useEffect(() => {
    apiService.fetchConfig()
      .then((serverConfig) => {
        if (!providerUrl && serverConfig.providerUrl) {
          setProviderUrl(serverConfig.providerUrl);
        }
      })
      .catch((error) => {
        console.warn('Config fetch error:', error);
      });
  }, []);

  // Analyze text whenever source text changes
  useEffect(() => {
    // Guard clause for empty input
    if (!sourceText.trim()) {
      setSourceAnalysis(null);
      return;
    }

    const timerId = setTimeout(() => {
      apiService.analyzeContent(sourceText)
        .then(setSourceAnalysis)
        .catch(console.error);
    }, 350);

    return () => clearTimeout(timerId);
  }, [sourceText]);

  // Execute humanization with claude-opus-5
  const executeHumanize = async () => {
    // Guard clause for empty input
    if (!sourceText.trim()) {
      setErrorMessage('Please enter source text to humanize');
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);

    try {
      const responseData = await apiService.humanizeContent({
        sourceText,
        toneValue,
        providerUrl: providerUrl.trim() || undefined,
        apiKey: apiKey.trim() || undefined,
      });

      setResultText(responseData.resultText);
      setResultAnalysis(responseData.resultAnalysis);
    } catch (error) {
      const errorText = error instanceof Error ? error.message : 'Execution failed';
      setErrorMessage(errorText);
    } finally {
      setIsLoading(false);
    }
  };

  return {
    sourceText,
    setSourceText,
    resultText,
    toneValue,
    setToneValue,
    sourceAnalysis,
    resultAnalysis,
    providerUrl,
    setProviderUrl,
    apiKey,
    setApiKey,
    isLoading,
    errorMessage,
    setErrorMessage,
    isModalOpen,
    setIsModalOpen,
    executeHumanize,
  };
}
