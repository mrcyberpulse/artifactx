import type { Config } from "tailwindcss";

export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#0a0a0f",
        "background-secondary": "#11111a",
        card: "#171722",
        border: "#24243380",
        primary: {
          DEFAULT: "#a855f7",
          foreground: "#f5f5f5",
        },
        accent: {
          DEFAULT: "#22d3ee",
          foreground: "#0a0a0f",
        },
        foreground: "#f5f5f5",
        muted: "#a1a1aa",
        danger: "#f43f5e",
        warning: "#f59e0b",
        success: "#22c55e",
      },
      borderRadius: {
        lg: "0.75rem",
        md: "0.5rem",
        sm: "0.375rem",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
      keyframes: {
        "fade-in": { from: { opacity: "0" }, to: { opacity: "1" } },
        "slide-in": {
          from: { opacity: "0", transform: "translateY(4px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        "fade-in": "fade-in 150ms ease-out",
        "slide-in": "slide-in 150ms ease-out",
      },
    },
  },
  plugins: [],
} satisfies Config;
