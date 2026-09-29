import React from 'react';
import { Loader2 } from 'lucide-react';
import { useHumanizer } from './hooks/useHumanizer';
import { Header } from './components/Header';
import { EditorCard } from './components/EditorCard';
import { SettingsModal } from './components/SettingsModal';

const TONE_OPTIONS = [
  { id: 'natural', label: 'Natural' },
  { id: 'academic', label: 'Academic' },
  { id: 'business', label: 'Professional' },
  { id: 'casual', label: 'Casual' },
];

const SAMPLE_TEXT = `Dalam era modern ini, kecerdasan buatan memainkan peran penting dalam mentransformasi berbagai sektor kehidupan manusia. Oleh karena itu, penting untuk dicatat bahwa pemanfaatan teknologi ini harus diimbangi dengan etika yang bijaksana. Tidak dapat dipungkiri bahwa otomatisasi menghadirkan solusi yang sangat efisien. Namun demikian, perlu diingat bahwa sentuhan manusiawi tetap merupakan hal yang krusial.`;

export const App: React.FC = () => {
  const {
    sourceText,
    setSourceText,
    resultText,
    toneValue,
    setToneValue,
    modeValue,
    setModeValue,
    sourceAnalysis,
    resultAnalysis,
    providerUrl,
    setProviderUrl,
    apiKey,
    setApiKey,
    modelName,
    setModelName,
    isLoading,
    errorMessage,
    setErrorMessage,
    isModalOpen,
    setIsModalOpen,
    executeHumanize,
  } = useHumanizer();

  return (
    <div className="min-h-screen flex flex-col bg-[#fafaf9] text-stone-900">
      {/* Top navigation header */}
      <Header
        onOpenSettings={() => setIsModalOpen(true)}
      />

      <main className="flex-1 max-w-[1400px] w-full mx-auto px-6 sm:px-10 lg:px-12 py-8 flex flex-col gap-6">
        {/* Error notification */}
        {errorMessage && (
          <div className="flex items-center justify-between px-5 py-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-sm font-normal">
            <span>{errorMessage}</span>
            <button onClick={() => setErrorMessage(null)} className="hover:underline ml-4 text-xs font-semibold">
              Dismiss
            </button>
          </div>
        )}

        {/* Toolbar controls with generous pill sizing */}
        <div className="flex flex-wrap items-center justify-between gap-4 pb-1">
          <div className="flex flex-wrap items-center gap-3">
            {/* Tone selector */}
            <div className="inline-flex items-center gap-1.5 p-1.5 bg-stone-100 border border-stone-200/90 rounded-full shadow-2xs">
              {TONE_OPTIONS.map((option) => (
                <button
                  key={option.id}
                  onClick={() => setToneValue(option.id)}
                  className={`px-5 py-2 text-sm transition-all rounded-full ${
                    toneValue === option.id
                      ? 'bg-stone-900 text-white font-medium shadow-xs'
                      : 'text-stone-600 hover:text-stone-950 font-normal hover:bg-stone-200/50'
                  }`}
                >
                  {option.label}
                </button>
              ))}
            </div>

            {/* Mode selector */}
            <div className="inline-flex items-center gap-1 p-1 bg-stone-100 border border-stone-200/90 rounded-full shadow-2xs text-xs">
              <button
                onClick={() => setModeValue('fast')}
                className={`px-3.5 py-1.5 rounded-full transition-all flex items-center gap-1.5 ${
                  modeValue === 'fast'
                    ? 'bg-white text-stone-900 font-semibold shadow-xs'
                    : 'text-stone-600 hover:text-stone-900'
                }`}
                title="1-Pass Fast Humanization"
              >
                <span>⚡ Cepat</span>
              </button>
              <button
                onClick={() => setModeValue('deep')}
                className={`px-3.5 py-1.5 rounded-full transition-all flex items-center gap-1.5 ${
                  modeValue === 'deep'
                    ? 'bg-white text-stone-900 font-semibold shadow-xs'
                    : 'text-stone-600 hover:text-stone-900'
                }`}
                title="Multi-Pass Adversarial Loopback Refinement"
              >
                <span>✨ Luwes Mendalam</span>
              </button>
            </div>
          </div>

          <button
            onClick={executeHumanize}
            disabled={isLoading}
            className="flex items-center gap-2 px-7 py-2.5 rounded-full text-sm font-semibold bg-stone-900 hover:bg-stone-800 text-white shadow-sm active:scale-[0.98] transition-all disabled:opacity-40 cursor-pointer disabled:cursor-not-allowed"
          >
            {isLoading && <Loader2 className="w-4 h-4 animate-spin" strokeWidth={1.5} />}
            <span>
              {isLoading
                ? modeValue === 'deep'
                  ? 'Memoles Mendalam...'
                  : 'Luweskan Teks...'
                : 'Luweskan Teks'}
            </span>
          </button>
        </div>

        {/* Dual pane workspace with generous width */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 flex-1">
          <EditorCard
            cardTitle="Input"
            textContent={sourceText}
            onTextChange={setSourceText}
            placeholderText="Type or paste AI text here to analyze and rewrite..."
            metricsData={sourceAnalysis}
            onClearText={() => setSourceText('')}
            onLoadSample={() => setSourceText(SAMPLE_TEXT)}
          />

          <EditorCard
            cardTitle="Output"
            textContent={resultText}
            isReadOnly={true}
            placeholderText="Humanized text will appear here..."
            metricsData={resultAnalysis}
          />
        </div>
      </main>

      {/* Settings dialog */}
      <SettingsModal
        isModalOpen={isModalOpen}
        onCloseModal={() => setIsModalOpen(false)}
        initialUrl={providerUrl}
        initialKey={apiKey}
        initialModel={modelName}
        onSaveSettings={(savedUrl, savedKey, savedModel) => {
          setProviderUrl(savedUrl);
          setApiKey(savedKey);
          setModelName(savedModel);
        }}
      />
    </div>
  );
};
