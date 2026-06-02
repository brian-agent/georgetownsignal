/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./app/**/*.{ts,tsx}','./components/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          green:'#1e4d35','green-mid':'#2d6b49','green-light':'#e8f2ec',
          amber:'#c47c1a','amber-light':'#fdf3e0',
          parchment:'#f7f4ef',ink:'#1a1208',rule:'#d4c9b5',
        },
      },
      fontFamily: {
        serif: ['Playfair Display','Georgia','serif'],
        sans:  ['Inter','system-ui','sans-serif'],
      },
    },
  },
  plugins: [],
}
