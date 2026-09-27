/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0fdfa',
          100: '#ccfbf1',
          200: '#99f6e4',
          300: '#5eead4',
          400: '#2dd4bf',
          500: '#14b8a6', // Teal medical primary
          600: '#0d9488',
          700: '#0f766e',
          800: '#115e59',
          900: '#134e4a',
        },
        dental: {
          healthy: '#10b981',
          caries: '#ef4444',
          filled: '#3b82f6',
          crown: '#f59e0b',
          rct: '#8b5cf6',
          missing: '#6b7280',
          extraction: '#dc2626',
          fracture: '#ea580c',
          sensitivity: '#eab308',
          mobility: '#ec4899',
        }
      },
    },
  },
  plugins: [],
}
