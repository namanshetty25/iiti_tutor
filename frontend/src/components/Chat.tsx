import React, { useState, useEffect, useRef } from 'react';
import { Sparkles } from 'lucide-react';
import Message from './Message';
import ChatInput from './ChatInput';
import TypingIndicator from './TypingIndicator';
import { ServiceResponse } from '../types/chat';

interface ChatMessage {
  id: string;
  message: string;
  isBot: boolean;
  timestamp: string;
  file?: Blob;
  fileName?: string;
}

interface ChatProps {
  selectedFeature: string | null;
}

const Chat: React.FC<ChatProps> = ({ selectedFeature }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      message: "Welcome to NEXUS! I'm your AI tutor for the IITI community. I can help you with course doubts, create study schedules, solve question papers, and much more. How can I assist you today?",
      isBot: true,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (selectedFeature) {
      const prompts: Record<string, string> = {
        doubt: "I'm ready to help with your course doubts...",
        schedule: "Let's create a personalized study schedule...",
        solve: "I can help you solve question papers...",
        generate: "I'll generate custom question papers...",
        upload: "Upload your study materials or textbook pages...",
        tutor: "I'm your personal AI tutor!"
      };
      handleSendMessage(prompts[selectedFeature] || '', true);
    }
  }, [selectedFeature]);

  const handleSendMessage = (message: string, isBot = false, file?: File) => {
    const newMessage: ChatMessage = {
      id: Date.now().toString(),
      message,
      isBot,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      file: file,
      fileName: file?.name
    };
    setMessages(prev => [...prev, newMessage]);

    if (!isBot) {
      setIsLoading(true);
    }
  };

  const handleReceiveResponse = (response: ServiceResponse) => {
    setIsLoading(false);

    if (response.text) {
      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        message: response.text,
        isBot: true,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        file: response.file || undefined,
        fileName: response.file ? 'response.pdf' : undefined
      };
      setMessages(prev => [...prev, botMessage]);
    }
  };

  return (
    <div className="flex flex-col flex-1 overflow-hidden">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-4 py-6 scroll-smooth">
        {/* Welcome decoration for empty chat */}
        {messages.length === 1 && (
          <div className="flex justify-center mb-8 animate-fade-in">
            <div className="flex items-center space-x-2 px-4 py-2 rounded-full 
                           bg-gradient-to-r from-cyan-500/10 to-purple-500/10 
                           dark:from-cyan-500/20 dark:to-purple-500/20
                           border border-cyan-200/50 dark:border-cyan-500/20">
              <Sparkles className="w-4 h-4 text-cyan-500 dark:text-cyan-400 animate-pulse" />
              <span className="text-sm text-gray-600 dark:text-gray-300">
                Start a conversation with NEXUS
              </span>
            </div>
          </div>
        )}

        {/* Messages */}
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.map((msg, index) => (
            <div
              key={msg.id}
              className="animate-fade-in"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <Message
                message={msg.message}
                isBot={msg.isBot}
                timestamp={msg.timestamp}
                file={msg.file}
                fileName={msg.fileName}
              />
            </div>
          ))}

          {isLoading && (
            <div className="animate-fade-in">
              <TypingIndicator />
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input area */}
      <div className="flex-shrink-0 border-t border-gray-200/50 dark:border-gray-700/50 
                     bg-white/50 dark:bg-black/50 backdrop-blur-lg
                     px-4 py-3 transition-colors duration-300">
        <div className="max-w-4xl mx-auto">
          <ChatInput
            onSendMessage={handleSendMessage}
            onReceiveResponse={handleReceiveResponse}
            isLoading={isLoading}
          />
        </div>
      </div>
    </div>
  );
};

export default Chat;
