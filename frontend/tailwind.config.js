/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        darkBackground: '#0b0f19',
        darkCard: '#131b2e',
        darkBorder: 'rgba(255, 255, 255, 0.08)',
      },
    },
  },
  plugins: [],
}
