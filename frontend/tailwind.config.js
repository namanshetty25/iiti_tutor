/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Primary palette
        primary: {
          50: '#ecfeff',
          100: '#cffafe',
          200: '#a5f3fc',
          300: '#67e8f9',
          400: '#22d3ee',
          500: '#06b6d4',
          600: '#0891b2',
          700: '#0e7490',
          800: '#155e75',
          900: '#164e63',
        },
        // Secondary palette (purple)
        secondary: {
          50: '#faf5ff',
          100: '#f3e8ff',
          200: '#e9d5ff',
          300: '#d8b4fe',
          400: '#c084fc',
          500: '#a855f7',
          600: '#9333ea',
          700: '#7e22ce',
          800: '#6b21a8',
          900: '#581c87',
        },
        // Surface colors
        surface: {
          light: '#ffffff',
          'light-elevated': '#f8fafc',
          dark: '#000000',
          'dark-elevated': '#111827',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'float-delayed': 'float-delayed 8s ease-in-out infinite',
        'shimmer': 'shimmer 2s infinite',
        'glow-pulse': 'glow-pulse 2s ease-in-out infinite',
        'spin-slow': 'spin-slow 20s linear infinite',
        'wave': 'wave 1.3s ease-in-out infinite',
        'fade-in': 'fade-in 0.3s ease-out forwards',
        'slide-in-left': 'slide-in-left 0.3s ease-out forwards',
        'gradient-x': 'gradient-x 3s ease infinite',
      },
      backdropBlur: {
        xs: '2px',
      },
      boxShadow: {
        'glow-sm': '0 0 15px -3px rgba(34, 211, 238, 0.3)',
        'glow': '0 0 25px -5px rgba(34, 211, 238, 0.4)',
        'glow-lg': '0 0 50px -10px rgba(34, 211, 238, 0.5)',
        'glow-purple': '0 0 25px -5px rgba(168, 85, 247, 0.4)',
        'glow-mixed': '0 4px 30px -5px rgba(34, 211, 238, 0.2), 0 4px 30px -5px rgba(168, 85, 247, 0.2)',
        'inner-glow': 'inset 0 0 20px rgba(34, 211, 238, 0.1)',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'gradient-mesh': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      },
      transitionTimingFunction: {
        'bounce-soft': 'cubic-bezier(0.34, 1.56, 0.64, 1)',
      },
    },
  },
  plugins: [],
};
