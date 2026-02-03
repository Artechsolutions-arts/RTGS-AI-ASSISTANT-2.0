import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'gov-primary': '#0066CC',
        'gov-secondary': '#00897B',
        'gov-accent': '#FF6F00',
        'gov-bg': '#F5F5F5',
        'gov-text': '#333333',
        'gov-border': '#E0E0E0',
      },
      fontFamily: {
        sans: ['Arial', 'Helvetica', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
export default config
