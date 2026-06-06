import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', "sans-serif"],
        mono: ['"Fira Code"', "ui-monospace", "monospace"],
      },
      colors: {
        decision: {
          saved:     "#059669",
          blocked:   "#DC2626",
          duplicate: "#D97706",
          skipped:   "#6B7280",
          error:     "#7C3AED",
          messy:     "#EA580C",
        },
      },
      boxShadow: {
        card: "0 1px 3px 0 rgb(0 0 0 / 0.07), 0 1px 2px -1px rgb(0 0 0 / 0.07)",
      },
    },
  },
  plugins: [],
} satisfies Config;
