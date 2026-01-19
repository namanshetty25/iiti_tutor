import React from 'react';
import { Bot, User, Download } from 'lucide-react';
import FileButton from './FileButton';
import katex from 'katex';

interface MessageProps {
  message: string;
  isBot: boolean;
  timestamp: string;
  file?: Blob;
  fileName?: string;
}

// Utility to render text with KaTeX, supporting $...$ (inline) and $$...$$ (display)
function renderWithKatex(text: string): React.ReactNode {
  // Split by display math first
  const displayParts = text.split(/(\$\$[^$]+\$\$)/g);
  return displayParts.map((part, i) => {
    if (/^\$\$[^$]+\$\$$/.test(part)) {
      // Remove the $$ delimiters
      const math = part.slice(2, -2);
      try {
        return (
          <div key={i} dangerouslySetInnerHTML={{ __html: katex.renderToString(math, { displayMode: true, throwOnError: false }) }} />
        );
      } catch {
        return <div key={i}>{part}</div>;
      }
    } else {
      // Now split by inline math
      const inlineParts = part.split(/(\$[^$]+\$)/g);
      return inlineParts.map((inline, j) => {
        if (/^\$[^$]+\$/.test(inline)) {
          const math = inline.slice(1, -1);
          try {
            return (
              <span key={j} dangerouslySetInnerHTML={{ __html: katex.renderToString(math, { displayMode: false, throwOnError: false }) }} />
            );
          } catch {
            return <span key={j}>{inline}</span>;
          }
        } else {
          return <span key={j}>{inline}</span>;
        }
      });
    }
  });
}

const Message: React.FC<MessageProps> = ({
  message,
  isBot,
  timestamp,
  file,
  fileName
}) => {
  const handleFileDownload = () => {
    if (file && fileName) {
      const url = URL.createObjectURL(file);
      const a = document.createElement('a');
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  return (
    <div className={`flex items-start space-x-3 mb-4 ${isBot ? '' : 'flex-row-reverse space-x-reverse'}`}>
      {/* Avatar */}
      <div className={`
        relative flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center
        shadow-lg transition-transform duration-300 hover:scale-105
        ${isBot
          ? 'bg-gradient-to-br from-cyan-500 to-purple-600'
          : 'bg-gradient-to-br from-emerald-500 to-teal-600'
        }
      `}>
        {/* Glow effect */}
        <div className={`absolute inset-0 rounded-xl blur-md opacity-40 
                        ${isBot ? 'bg-cyan-500' : 'bg-emerald-500'}`} />

        {isBot ? (
          <Bot className="w-4 h-4 text-white relative z-10" />
        ) : (
          <User className="w-4 h-4 text-white relative z-10" />
        )}
      </div>

      {/* Message content */}
      <div className={`flex-1 max-w-xl ${isBot ? '' : 'flex flex-col items-end'}`}>
        {/* File attachment display */}
        {file && fileName && (
          <div className={`mb-2 ${isBot ? '' : 'flex justify-end'}`}>
            <FileButton
              fileName={fileName}
              fileBlob={file}
              onDownload={handleFileDownload}
            />
          </div>
        )}

        {/* Message bubble */}
        <div className={`
          relative px-4 py-3 rounded-2xl transition-all duration-300
          ${isBot
            ? `bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm
               border border-gray-200/50 dark:border-gray-700/50
               text-gray-800 dark:text-gray-100 rounded-tl-md
               shadow-sm hover:shadow-md dark:shadow-none dark:hover:shadow-glow-sm`
            : `bg-gradient-to-br from-cyan-500 to-purple-600
               text-white rounded-tr-md shadow-lg
               hover:shadow-xl hover:shadow-purple-500/20`
          }
        `}>
          {/* Subtle gradient overlay for bot messages */}
          {isBot && (
            <div className="absolute inset-0 rounded-2xl rounded-tl-md 
                           bg-gradient-to-br from-cyan-500/5 to-purple-500/5 
                           dark:from-cyan-500/10 dark:to-purple-500/10 
                           pointer-events-none" />
          )}

          <div className="relative text-sm leading-relaxed whitespace-pre-wrap break-words">
            {renderWithKatex(message)}
          </div>
        </div>

        {/* Timestamp */}
        <div className={`text-[10px] text-gray-400 dark:text-gray-500 mt-1.5 px-1 
                        ${isBot ? 'text-left' : 'text-right'}`}>
          {timestamp}
        </div>
      </div>
    </div>
  );
};

export default Message;
