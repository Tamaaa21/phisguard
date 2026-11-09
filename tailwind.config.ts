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
        background: "var(--background)",
        "background-alt": "var(--background-alt)",
        "background-3": "var(--background-3)",
        surface: "var(--surface)",
        "surface-alt": "var(--surface-alt)",
        "surface-3": "var(--surface-3)",
        "surface-4": "var(--surface-4)",
        "surface-green": "var(--surface-green)",
        "surface-amber": "var(--surface-amber)",
        accent: "var(--accent)",
        "accent-alt": "var(--accent-alt)",
        "accent-3": "var(--accent-3)",
        "accent-4": "var(--accent-4)",
        "accent-5": "var(--accent-5)",
        "accent-amber": "var(--accent-amber)",
        "text-primary": "var(--text-primary)",
        "text-secondary": "var(--text-secondary)",
        "text-tertiary": "var(--text-tertiary)",
      },
      fontFamily: {
        sans: ["var(--font-geist-sans)", "Geist", "system-ui", "sans-serif"],
        mono: ["var(--font-jetbrains-mono)", "JetBrains Mono", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
