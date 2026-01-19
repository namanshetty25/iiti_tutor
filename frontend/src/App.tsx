import 'katex/dist/katex.min.css';
import { useState } from 'react';
import { Menu, X } from 'lucide-react';
import { ThemeProvider } from './contexts/ThemeContext';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Chat from './components/Chat';
import AnimatedBackground from './components/AnimatedBackground';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [selectedFeature, setSelectedFeature] = useState<string | null>(null);

  const handleFeatureSelect = (feature: string) => {
    setSelectedFeature(feature);
    setSidebarOpen(false);
  };

  return (
    <ThemeProvider>
      <div className="h-screen w-screen bg-gradient-to-br from-slate-50 via-white to-blue-50 
                      dark:from-gray-950 dark:via-black dark:to-gray-950 
                      text-gray-900 dark:text-white flex flex-col overflow-hidden 
                      transition-colors duration-500 relative">
        {/* Animated background */}
        <AnimatedBackground />

        {/* Main content wrapper */}
        <div className="relative z-10 flex flex-col h-full">
          <Header />

          <div className="flex flex-1 overflow-hidden">
            {/* Mobile sidebar toggle */}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="md:hidden fixed top-4 left-4 z-50 p-2.5 rounded-xl glass
                        hover:scale-105 active:scale-95
                        transition-all duration-300 shadow-lg"
              aria-label="Toggle sidebar"
            >
              {sidebarOpen ? (
                <X className="w-5 h-5 text-gray-700 dark:text-cyan-400" />
              ) : (
                <Menu className="w-5 h-5 text-gray-700 dark:text-cyan-400" />
              )}
            </button>

            {/* Mobile overlay */}
            {sidebarOpen && (
              <div
                className="md:hidden fixed inset-0 bg-black/20 dark:bg-black/50 backdrop-blur-sm z-30 
                          transition-all duration-300 animate-fade-in"
                onClick={() => setSidebarOpen(false)}
              />
            )}

            <Sidebar isOpen={sidebarOpen} onFeatureSelect={handleFeatureSelect} />

            <div className="flex-1 flex flex-col overflow-hidden">
              <Chat selectedFeature={selectedFeature} />
            </div>
          </div>
        </div>
      </div>
    </ThemeProvider>
  );
}

export default App;
