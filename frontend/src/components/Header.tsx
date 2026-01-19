import React from 'react';
import { Zap, Settings, User, Sparkles } from 'lucide-react';
import ThemeToggle from './ThemeToggle';

const Header: React.FC = () => {
  return (
    <header className="sticky top-0 left-0 right-0 z-50 glass
                       border-b border-gray-200/50 dark:border-cyan-500/20 
                       px-6 py-2 transition-all duration-300">
      <div className="flex items-center justify-between max-w-7xl mx-auto">
        {/* Logo Section */}
        <div className="flex items-center space-x-3 group">
          <div className="relative">
            {/* Glow effect behind icon */}
            <div className="absolute inset-0 w-10 h-10 bg-gradient-to-r from-cyan-400 to-purple-500 
                           rounded-xl blur-lg opacity-50 dark:opacity-70 group-hover:opacity-80 
                           transition-opacity duration-300 animate-glow-pulse"></div>

            {/* Icon container */}
            <div className="relative w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-purple-600 
                           flex items-center justify-center shadow-lg 
                           group-hover:scale-105 transition-transform duration-300">
              <Zap className="w-5 h-5 text-white" />
            </div>
          </div>

          <div>
            <h1 className="text-2xl font-bold tracking-tight">
              <span className="bg-gradient-to-r from-cyan-600 via-blue-600 to-purple-600 
                             dark:from-cyan-400 dark:via-blue-400 dark:to-purple-400 
                             bg-clip-text text-transparent">
                NEXUS
              </span>
            </h1>
            <div className="flex items-center space-x-1.5">
              <Sparkles className="w-3 h-3 text-cyan-500 dark:text-cyan-400" />
              <p className="text-[10px] text-gray-500 dark:text-gray-400 uppercase tracking-[0.2em] font-medium">
                AI Tutor • IITI
              </p>
            </div>
          </div>
        </div>

        {/* Actions Section */}
        <div className="flex items-center space-x-2">
          <ThemeToggle />

          <button className="p-2.5 rounded-xl bg-gray-100/80 dark:bg-gray-800/50 
                            hover:bg-gray-200/80 dark:hover:bg-gray-700/50 
                            border border-gray-200/50 dark:border-gray-700/30 
                            hover:border-gray-300 dark:hover:border-cyan-500/30
                            transition-all duration-300 group
                            hover:shadow-md dark:hover:shadow-glow-sm">
            <Settings className="w-4 h-4 text-gray-500 dark:text-gray-400 
                                group-hover:text-gray-700 dark:group-hover:text-cyan-400 
                                group-hover:rotate-90 transition-all duration-300" />
          </button>

          <button className="p-2.5 rounded-xl bg-gray-100/80 dark:bg-gray-800/50 
                            hover:bg-gray-200/80 dark:hover:bg-gray-700/50 
                            border border-gray-200/50 dark:border-gray-700/30 
                            hover:border-gray-300 dark:hover:border-cyan-500/30
                            transition-all duration-300 group
                            hover:shadow-md dark:hover:shadow-glow-sm">
            <User className="w-4 h-4 text-gray-500 dark:text-gray-400 
                            group-hover:text-gray-700 dark:group-hover:text-cyan-400 
                            transition-colors duration-300" />
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
