import React from 'react';
import { Bot } from 'lucide-react';

const TypingIndicator: React.FC = () => {
  return (
    <div className="flex items-start space-x-3 mb-4 animate-fade-in">
      {/* Avatar */}
      <div className="relative flex-shrink-0 w-9 h-9 rounded-xl 
                     bg-gradient-to-br from-cyan-500 to-purple-600
                     flex items-center justify-center shadow-lg">
        {/* Glow effect */}
        <div className="absolute inset-0 rounded-xl bg-cyan-500 blur-md opacity-40" />

        {/* Pulse ring */}
        <div className="absolute inset-0 rounded-xl border-2 border-cyan-400/50 
                       animate-ping opacity-30" />

        <Bot className="w-4 h-4 text-white relative z-10" />
      </div>

      {/* Typing bubble */}
      <div className="px-5 py-3.5 rounded-2xl rounded-tl-md 
                     bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm
                     border border-gray-200/50 dark:border-gray-700/50
                     shadow-sm">
        <div className="flex items-center space-x-1.5">
          <div
            className="w-2 h-2 bg-cyan-500 dark:bg-cyan-400 rounded-full animate-wave"
            style={{ animationDelay: '0ms' }}
          />
          <div
            className="w-2 h-2 bg-cyan-500 dark:bg-cyan-400 rounded-full animate-wave"
            style={{ animationDelay: '150ms' }}
          />
          <div
            className="w-2 h-2 bg-cyan-500 dark:bg-cyan-400 rounded-full animate-wave"
            style={{ animationDelay: '300ms' }}
          />
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;