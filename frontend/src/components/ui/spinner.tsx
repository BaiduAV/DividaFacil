import React from 'react';

export const Spinner: React.FC<{ label?: string }> = ({ label = 'Loading...' }) => (
  <div className="flex flex-col items-center justify-center gap-2 text-gray-500 animate-pulse" role="status" aria-live="polite">
    <svg className="h-6 w-6 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" className="opacity-25" />
      <path d="M4 12a8 8 0 018-8" className="opacity-75" />
    </svg>
    <span className="text-xs uppercase tracking-wide">{label}</span>
  </div>
);

export default Spinner;
