import React from 'react';
import { Moon, Sun } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

const ThemeToggle: React.FC = () => {
  const { isDarkMode, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="relative p-2.5 rounded-xl bg-gray-100/80 dark:bg-gray-800/50 
                 hover:bg-gray-200/80 dark:hover:bg-gray-700/50 
                 border border-gray-200/50 dark:border-gray-700/30 
                 hover:border-amber-300 dark:hover:border-blue-500/50
                 transition-all duration-500 group overflow-hidden
                 hover:shadow-md dark:hover:shadow-glow-sm"
      aria-label="Toggle theme"
    >
      {/* Background glow on hover */}
      <div className={`absolute inset-0 transition-opacity duration-500 ${isDarkMode
          ? 'bg-gradient-to-br from-blue-500/20 to-purple-500/20 opacity-0 group-hover:opacity-100'
          : 'bg-gradient-to-br from-amber-300/30 to-orange-300/30 opacity-0 group-hover:opacity-100'
        }`} />

      <div className="relative w-4 h-4">
        {/* Sun icon */}
        <Sun
          className={`w-4 h-4 text-amber-500 absolute inset-0 transition-all duration-500 ${isDarkMode
              ? 'opacity-0 rotate-180 scale-0'
              : 'opacity-100 rotate-0 scale-100'
            }`}
        />

        {/* Moon icon */}
        <Moon
          className={`w-4 h-4 text-blue-400 absolute inset-0 transition-all duration-500 ${isDarkMode
              ? 'opacity-100 rotate-0 scale-100'
              : 'opacity-0 -rotate-180 scale-0'
            }`}
        />
      </div>
    </button>
  );
};

export default ThemeToggle;
