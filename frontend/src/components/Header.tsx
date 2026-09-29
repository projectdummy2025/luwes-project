import React from 'react';
import { SlidersHorizontal } from 'lucide-react';
import { Logo } from './Logo';

interface HeaderProps {
  onOpenSettings: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onOpenSettings }) => {
  return (
    <header className="border-b border-stone-200 bg-white/90 backdrop-blur-md sticky top-0 z-30">
      <div className="max-w-[1400px] mx-auto px-6 sm:px-10 lg:px-12 h-16 flex items-center justify-between">
        {/* Brand logo luwesin */}
        <div className="flex items-center gap-3">
          <Logo size={32} />
          <span className="font-['Roboto',sans-serif] font-semibold text-xl tracking-tight text-stone-900 lowercase">
            luwesin
          </span>
          <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-stone-100 text-stone-600 border border-stone-200">
            studio
          </span>
        </div>

        {/* Action controls */}
        <div className="flex items-center gap-2.5">
          <button
            onClick={onOpenSettings}
            className="flex items-center gap-2 px-4 py-2 rounded-full border border-stone-200 bg-white hover:bg-stone-50 text-sm font-medium text-stone-700 transition-colors shadow-xs"
          >
            <SlidersHorizontal className="w-4 h-4 text-stone-500" strokeWidth={1.5} />
            <span>Settings</span>
          </button>
        </div>
      </div>
    </header>
  );
};
