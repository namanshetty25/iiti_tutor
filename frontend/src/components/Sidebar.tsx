import React from 'react';
import {
  Calendar,
  FileText,
  Upload,
  Brain,
  Target,
  Lightbulb,
  Zap,
  ChevronRight
} from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  onFeatureSelect: (feature: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onFeatureSelect }) => {
  const features = [
    { id: 'doubt', icon: Lightbulb, label: 'Ask Doubt', description: 'Course queries', color: 'from-yellow-400 to-orange-500' },
    { id: 'schedule', icon: Calendar, label: 'Study Schedule', description: 'Plan your time', color: 'from-green-400 to-emerald-500' },
    { id: 'solve', icon: Target, label: 'Solve Papers', description: 'Get solutions', color: 'from-blue-400 to-indigo-500' },
    { id: 'generate', icon: FileText, label: 'Generate Papers', description: 'Practice tests', color: 'from-purple-400 to-violet-500' },
    { id: 'upload', icon: Upload, label: 'Upload Book', description: 'Add materials', color: 'from-pink-400 to-rose-500' },
    { id: 'tutor', icon: Brain, label: 'AI Tutor', description: 'Personal help', color: 'from-cyan-400 to-blue-500' },
  ];

  return (
    <div className={`
      fixed left-0 top-0 h-full glass
      border-r border-gray-200/50 dark:border-cyan-500/20 
      transform transition-all duration-300 ease-out z-40
      ${isOpen ? 'translate-x-0' : '-translate-x-full'}
      w-72 md:w-64 md:relative md:translate-x-0
    `}>
      <div className="flex flex-col h-full p-5 pt-20 md:pt-5">
        {/* Features Section */}
        <div className="flex-1">
          <div className="mb-5">
            <h2 className="text-sm font-semibold text-gray-800 dark:text-white uppercase tracking-wider">
              Features
            </h2>
            <div className="mt-2 h-0.5 w-10 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-full"></div>
          </div>

          <div className="space-y-2">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <button
                  key={feature.id}
                  onClick={() => onFeatureSelect(feature.id)}
                  className="w-full flex items-center p-3 rounded-xl 
                            bg-gray-50/50 dark:bg-gray-800/30 
                            hover:bg-gray-100/80 dark:hover:bg-gray-700/50 
                            border border-gray-200/50 dark:border-gray-700/30 
                            hover:border-gray-300 dark:hover:border-cyan-500/30
                            transition-all duration-300 group
                            hover:shadow-md dark:hover:shadow-glow-sm
                            hover:translate-x-1"
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  {/* Icon */}
                  <div className={`p-2 rounded-lg bg-gradient-to-br ${feature.color} 
                                  shadow-lg group-hover:scale-110 group-hover:shadow-xl
                                  transition-all duration-300`}>
                    <Icon className="w-4 h-4 text-white" />
                  </div>

                  {/* Text */}
                  <div className="ml-3 flex-1 text-left">
                    <div className="text-sm font-medium text-gray-800 dark:text-white 
                                  group-hover:text-cyan-600 dark:group-hover:text-cyan-400 
                                  transition-colors duration-300">
                      {feature.label}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      {feature.description}
                    </div>
                  </div>

                  {/* Arrow */}
                  <ChevronRight className="w-4 h-4 text-gray-400 dark:text-gray-500 
                                          opacity-0 group-hover:opacity-100 
                                          -translate-x-2 group-hover:translate-x-0
                                          transition-all duration-300" />
                </button>
              );
            })}
          </div>
        </div>

        {/* AI Status Card */}
        <div className="mt-6 p-4 rounded-xl 
                       bg-gradient-to-br from-cyan-500/10 via-purple-500/10 to-pink-500/10
                       dark:from-cyan-500/20 dark:via-purple-500/20 dark:to-pink-500/20
                       border border-cyan-200/50 dark:border-cyan-500/20
                       backdrop-blur-sm">
          <div className="flex items-center space-x-2 mb-2">
            <div className="relative">
              <Zap className="w-4 h-4 text-cyan-500 dark:text-cyan-400" />
              <div className="absolute inset-0 w-4 h-4 bg-cyan-400 rounded-full blur-md 
                             opacity-50 animate-glow-pulse"></div>
            </div>
            <span className="text-sm font-semibold text-cyan-600 dark:text-cyan-400 tracking-wide">
              AI Status
            </span>
          </div>

          <p className="text-xs text-gray-600 dark:text-gray-300 leading-relaxed">
            Neural networks online and ready to assist with your studies.
          </p>

          <div className="flex items-center mt-3 pt-3 border-t border-gray-200/50 dark:border-gray-700/30">
            <div className="relative flex items-center justify-center w-2 h-2">
              <div className="absolute w-2 h-2 bg-green-500 rounded-full animate-ping opacity-75"></div>
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            </div>
            <span className="ml-2 text-xs font-medium text-green-600 dark:text-green-400">
              Connected & Ready
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
