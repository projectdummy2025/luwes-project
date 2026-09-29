import React from 'react';

interface LogoProps {
  className?: string;
  size?: number;
}

export const Logo: React.FC<LogoProps> = ({ className = '', size = 32 }) => {
  return (
    <div
      style={{ width: size, height: size }}
      className={`relative flex items-center justify-center rounded-xl bg-stone-900 text-stone-100 shadow-xs select-none transition-transform hover:scale-105 ${className}`}
      title="Luwesin Studio"
    >
      <svg
        viewBox="0 0 32 32"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="w-[70%] h-[70%]"
      >
        {/* Fluid cursive loop forming dynamic 'L' and cadence wave */}
        <path
          d="M10 7C10 14.5 9.5 19.5 12 22.5C14 25 18 25.5 21 23C23.5 21 24 17.5 21.5 15C19 12.5 15.5 14 13.5 17.5C11.5 21 10 24 7.5 25.5"
          stroke="currentColor"
          strokeWidth="2.4"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        {/* Warm amber human essence accent */}
        <circle cx="21.5" cy="8.5" r="1.75" fill="#f59e0b" />
      </svg>
    </div>
  );
};
