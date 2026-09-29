import React, { useState } from 'react';
import { X } from 'lucide-react';

interface SettingsModalProps {
  isModalOpen: boolean;
  onCloseModal: () => void;
  initialUrl: string;
  initialKey: string;
  initialModel: string;
  onSaveSettings: (updatedUrl: string, updatedKey: string, updatedModel: string) => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isModalOpen,
  onCloseModal,
  initialUrl,
  initialKey,
  initialModel,
  onSaveSettings,
}) => {
  const [urlInput, setUrlInput] = useState<string>(initialUrl);
  const [keyInput, setKeyInput] = useState<string>(initialKey);
  const [modelInput, setModelInput] = useState<string>(initialModel);

  // Early return if modal is closed
  if (!isModalOpen) return null;

  const handleSave = () => {
    onSaveSettings(urlInput.trim(), keyInput.trim(), modelInput.trim());
    onCloseModal();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-stone-900/25 backdrop-blur-[2px]">
      <div className="w-full max-w-sm bg-white border border-stone-200 rounded-xl shadow-xl overflow-hidden">
        {/* Modal header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-stone-100 bg-stone-50/50">
          <h3 className="font-medium text-xs text-stone-800 tracking-tight">Provider Settings</h3>
          <button
            onClick={onCloseModal}
            className="p-1 text-stone-400 hover:text-stone-700 transition-colors"
          >
            <X className="w-3.5 h-3.5" strokeWidth={1.5} />
          </button>
        </div>

        {/* Modal body */}
        <div className="p-4 flex flex-col gap-3.5">
          <p className="text-[11px] text-stone-500 leading-normal font-light">
            Configure your OpenAI-compatible provider credentials and model selection.
          </p>

          <div className="flex flex-col gap-1">
            <label className="text-[11px] font-medium text-stone-600">Provider URL</label>
            <input
              type="text"
              value={urlInput}
              onChange={(event) => setUrlInput(event.target.value)}
              placeholder="https://api.openai.com/v1"
              className="px-2.5 py-1.5 bg-stone-50/50 border border-stone-200 rounded-md text-xs text-stone-800 outline-none focus:border-stone-400 font-mono placeholder:text-stone-300"
            />
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-[11px] font-medium text-stone-600">API Key</label>
            <input
              type="password"
              value={keyInput}
              onChange={(event) => setKeyInput(event.target.value)}
              placeholder="sk-..."
              className="px-2.5 py-1.5 bg-stone-50/50 border border-stone-200 rounded-md text-xs text-stone-800 outline-none focus:border-stone-400 font-mono placeholder:text-stone-300"
            />
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-[11px] font-medium text-stone-600">Model Name</label>
            <input
              type="text"
              value={modelInput}
              onChange={(event) => setModelInput(event.target.value)}
              placeholder="claude-opus-5"
              className="px-2.5 py-1.5 bg-stone-50/50 border border-stone-200 rounded-md text-xs text-stone-800 outline-none focus:border-stone-400 font-mono placeholder:text-stone-300"
            />
            <span className="text-[10px] text-stone-400">
              Stored locally in browser storage.
            </span>
          </div>
        </div>

        {/* Modal footer */}
        <div className="flex items-center justify-end gap-2 px-4 py-2.5 border-t border-stone-100 bg-stone-50/30">
          <button
            onClick={onCloseModal}
            className="px-2.5 py-1 text-xs text-stone-500 hover:text-stone-800 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="px-3.5 py-1 text-xs font-medium bg-stone-900 hover:bg-stone-800 text-white rounded-md shadow-sm transition-colors"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
};
