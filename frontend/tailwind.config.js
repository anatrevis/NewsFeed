/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['DM Sans', 'system-ui', 'sans-serif'],
      },
      colors: {
        midnight: {
          50: '#f0f4ff',
          100: '#e0e8ff',
          200: '#c7d4fe',
          300: '#a4b8fc',
          400: '#7a91f9',
          500: '#5a6cf3',
          600: '#4149e7',
          700: '#353bcc',
          800: '#2e34a5',
          900: '#0f172a',
          950: '#080b14',
        },
        accent: {
          cyan: '#22d3ee',
          pink: '#f472b6',
          amber: '#fbbf24',
        },
      },
    },
  },
  plugins: [],
}

