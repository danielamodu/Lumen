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
        canvas: "#06080c",
        surface: {
          1: "#0b0f17",
          2: "#111723",
          3: "#182030",
          4: "#222c40",
        },
        border: {
          subtle: "rgba(255, 255, 255, 0.07)",
          muted: "rgba(255, 255, 255, 0.12)",
          strong: "rgba(255, 255, 255, 0.22)",
        },
        brand: {
          400: "#818cf8",
          500: "#6366f1",
          600: "#4f46e5",
          700: "#4338ca",
        },
        signal: {
          win: "#10b981",
          loss: "#f43f5e",
          cross: "#f59e0b",
        },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "-apple-system", "BlinkMacSystemFont", "sans-serif"],
        display: ["var(--font-display)", "Georgia", "serif"],
        mono: ["var(--font-mono)", "JetBrains Mono", "monospace"],
      },
      boxShadow: {
        glass: "0 8px 32px 0 rgba(0, 0, 0, 0.37)",
        elevated: "0 20px 40px -15px rgba(0, 0, 0, 0.7)",
        glow: "0 0 30px -5px rgba(99, 102, 241, 0.3)",
      },
    },
  },
  plugins: [],
};
export default config;
