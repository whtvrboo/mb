import type { Config } from 'tailwindcss'

export default <Config>{
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        "primary": "#eecd2b",
        "primary-500": "#eecd2b", // Mapping for Nuxt UI if needed
        "background-light": "#f8f8f6",
        "background-dark": "#221f10",
      },
      fontFamily: {
        "display": ["Space Grotesk", "sans-serif"],
        "sans": ["Space Grotesk", "sans-serif"] // Set as default sans
      },
      borderRadius: {
        "DEFAULT": "0.5rem",
        "lg": "1rem",
        "xl": "1.5rem",
        "full": "9999px"
      },
      boxShadow: {
        'neobrutalism': '4px 4px 0px 0px #221f10',
        'neobrutalism-lg': '6px 6px 0px 0px #221f10',
        'neobrutalism-sm': '2px 2px 0px 0px #221f10',
      }
    }
  }
}
