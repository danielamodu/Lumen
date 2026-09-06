import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        "stone-black": "#0C0A09",
        "warm-charcoal": "#1C1917",
        "acid-lime": "#D4F268",
        "stone-white": "#E7E5E4",
      },
      fontFamily: {
        sans: ["var(--font-sans)", "'Instrument Sans'", "-apple-system", "BlinkMacSystemFont", "sans-serif"],
        display: ["var(--font-display)", "'Newsreader'", "Georgia", "serif"],
        mono: ["var(--font-mono)", "'JetBrains Mono'", "monospace"],
      },
    },
  },
  plugins: [],
};
export default config;
