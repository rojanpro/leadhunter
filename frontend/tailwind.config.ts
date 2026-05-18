import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}", "./components/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        border: "#d8dee9",
        background: "#f7f8fb",
        foreground: "#18212f",
        primary: "#0f766e",
        accent: "#b45309",
        muted: "#eef1f5"
      }
    }
  },
  plugins: []
};

export default config;
