import React, { useState, useRef } from 'react';
import { Send, Paperclip, X, FileText, Image } from 'lucide-react';
import { sendMessage } from '../services/chatService';
import { ServiceResponse } from '../types/chat';

interface ChatInputProps {
  onSendMessage: (message: string, isBot?: boolean, file?: File) => void;
  onReceiveResponse: (response: ServiceResponse) => void;
  isLoading: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, onReceiveResponse, isLoading }) => {
  const [message, setMessage] = useState('');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [showAttachMenu, setShowAttachMenu] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || isLoading) return;

    const messageText = message.trim();
    const fileToSend = uploadedFile;

    // Clear input immediately for better UX
    setMessage('');
    setUploadedFile(null);

    // Show user message in chat with file if present
    onSendMessage(messageText, false, fileToSend || undefined);

    try {
      // Send to backend
      const response = await sendMessage(messageText, fileToSend || undefined);
      console.log('Backend response:', response);

      // Handle the response
      onReceiveResponse(response);
    } catch (error) {
      console.error('Message send failed:', error);
      // Handle error - could show error message to user
      onReceiveResponse({
        text: 'Sorry, there was an error sending your message. Please try again.',
        file: null
      });
    }
  };

  const handleAttachClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadedFile(file);
    setShowAttachMenu(false);
  };

  return (
    <div className="relative">
      {/* File preview */}
      {uploadedFile && (
        <div className="mb-3 animate-fade-in">
          <div className="inline-flex items-center space-x-3 px-4 py-2.5 rounded-xl 
                         bg-gray-100/80 dark:bg-gray-800/80 backdrop-blur-sm
                         border border-gray-200/50 dark:border-gray-700/50">
            {uploadedFile.type.startsWith('image') ? (
              <div className="relative">
                <img
                  src={URL.createObjectURL(uploadedFile)}
                  alt="preview"
                  className="h-12 w-12 object-cover rounded-lg shadow-sm"
                />
                <Image className="absolute -bottom-1 -right-1 w-4 h-4 p-0.5 
                                 bg-purple-500 text-white rounded-full" />
              </div>
            ) : (
              <div className="h-12 w-12 rounded-lg bg-gradient-to-br from-cyan-500/20 to-purple-500/20 
                             dark:from-cyan-500/30 dark:to-purple-500/30
                             flex items-center justify-center">
                <FileText className="w-5 h-5 text-cyan-600 dark:text-cyan-400" />
              </div>
            )}

            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-800 dark:text-white truncate max-w-[180px]">
                {uploadedFile.name}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {(uploadedFile.size / 1024).toFixed(1)} KB
              </p>
            </div>

            <button
              type="button"
              onClick={() => setUploadedFile(null)}
              className="p-1.5 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/30 
                        text-gray-400 hover:text-red-500 dark:hover:text-red-400
                        transition-colors duration-200"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Input form */}
      <form onSubmit={handleSubmit} className="flex items-end space-x-3">
        <div className="flex-1 relative">
          {/* Input container */}
          <div className="relative rounded-2xl overflow-hidden
                         bg-gray-100/80 dark:bg-gray-800/60 backdrop-blur-sm
                         border border-gray-200/50 dark:border-gray-700/50
                         focus-within:border-cyan-400/50 dark:focus-within:border-cyan-500/50
                         focus-within:shadow-lg focus-within:shadow-cyan-500/10
                         transition-all duration-300">
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Ask NEXUS anything about your studies..."
              className="w-full px-4 py-3 pr-12 bg-transparent
                        text-gray-800 dark:text-white 
                        placeholder-gray-400 dark:placeholder-gray-500
                        focus:outline-none resize-none 
                        min-h-[48px] max-h-32 overflow-y-auto"
              rows={1}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
            />

            {/* Attach button */}
            <div className="absolute right-2 bottom-2">
              <div className="relative">
                <button
                  type="button"
                  onClick={() => setShowAttachMenu((prev) => !prev)}
                  className="p-2 rounded-lg 
                            hover:bg-gray-200/80 dark:hover:bg-gray-700/80 
                            text-gray-400 hover:text-cyan-500 dark:hover:text-cyan-400
                            transition-all duration-200"
                >
                  <Paperclip className="w-4 h-4" />
                </button>

                {/* Attach menu dropdown */}
                {showAttachMenu && (
                  <div className="absolute bottom-12 right-0 z-50 w-52 
                                 bg-white/95 dark:bg-gray-800/95 backdrop-blur-lg
                                 border border-gray-200/50 dark:border-gray-700/50 
                                 rounded-xl shadow-xl p-2 animate-fade-in">
                    <button
                      onClick={() => {
                        handleAttachClick();
                        setShowAttachMenu(false);
                      }}
                      className="w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg
                                text-sm text-gray-700 dark:text-gray-200
                                hover:bg-gray-100 dark:hover:bg-gray-700/50
                                transition-colors duration-200"
                    >
                      <FileText className="w-4 h-4 text-cyan-500" />
                      <span>Upload File</span>
                    </button>
                  </div>
                )}
              </div>

              <input
                type="file"
                accept="application/pdf,image/*"
                ref={fileInputRef}
                onChange={handleFileChange}
                className="hidden"
              />
            </div>
          </div>
        </div>

        {/* Send button */}
        <button
          type="submit"
          disabled={!message.trim() || isLoading}
          className="relative p-3.5 rounded-xl 
                    bg-gradient-to-br from-cyan-500 to-purple-600 
                    text-white shadow-lg
                    disabled:opacity-40 disabled:cursor-not-allowed 
                    hover:shadow-xl hover:shadow-purple-500/25
                    hover:scale-105 active:scale-95
                    transition-all duration-300 group"
        >
          {/* Glow effect */}
          <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-cyan-400 to-purple-500 
                         blur-lg opacity-0 group-hover:opacity-50 transition-opacity duration-300" />

          <Send className="w-5 h-5 relative z-10 group-hover:translate-x-0.5 
                          group-hover:-translate-y-0.5 transition-transform duration-200" />
        </button>
      </form>
    </div>
  );
};

export default ChatInput;
