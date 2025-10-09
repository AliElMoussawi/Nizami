/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,ts}",
  ],
  theme: {
    extend: {
      width: {
        '128': '32rem',
        '164': '41rem',
      },
      fontFamily: {
        poppins: ["Bahij TheSansArabic", "sans-serif"],
        lato: ["Bahij TheSansArabic", "sans-serif"],
      },
      colors: {
        grey1: '#C0E8D4',
        grey2: '#f4f4ff',
        grey3: '#B6DDC7',
        grey4: '#f0f3fe',
        grey5: '#7C7C7C',
        grey6: '#3A4558',
        grey7: '#263755',
        grey8: '#475467',
        grey9: '#EBEBEB',
        grey10: '#A2A3AF',
        grey11: '#8892A6',
        grey12: '#232A36',
        grey13: '#F6F6F6',
        blue1: '#079953',
        red1: '#FFF1F1',
        red2: '#F04438',
        red3: '#B32318',
        indigo1: '#E8FFEB',
        indigo2: '#ffdfdc',
        purple1: '#C0E8D4',
        purple2: '#E8F6ED',
        purple3: '#E8F6ED',
        purple4: '#3B2E8E',
        purple5: '#07a559',
        purple6: '#7F56D9',
        purple7: '#8B5CF6',
        purple8: '#F5F3FF',
        green1: '#66C61C',

        grey201: '#F8F5FF',
        green201: '#F1FFF4',
        green202: '#E8F6ED',
        green203: '#067B43',
      }
    },
  },
  plugins: [],
}

