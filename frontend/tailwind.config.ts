import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Inter"', "system-ui", "sans-serif"],
        display: ['"Space Grotesk"', "system-ui", "sans-serif"],
        mono: ['"Geist Mono"', "ui-monospace", "monospace"],
      },
      colors: {
        mesh: {
          bg: "#000000",
          surface: "#0a0a0a",
          elevated: "#111111",
          border: "rgba(255,255,255,0.08)",
          text: "#ededed",
          muted: "#888888",
          accent: "#a8b4ff",
        },
        decision: {
          saved:     "#34d399",
          blocked:   "#f87171",
          duplicate: "#fbbf24",
          skipped:   "#9ca3af",
          error:     "#c084fc",
          messy:     "#fb923c",
        },
      },
      boxShadow: {
        card: "0 0 0 1px rgba(255,255,255,0.06)",
        glow: "0 0 40px rgba(168,180,255,0.12)",
      },
    },
  },
  plugins: [],
} satisfies Config;
