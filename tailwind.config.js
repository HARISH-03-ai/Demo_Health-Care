module.exports = {
  content: ["./templates/**/*.{html,js}", "./static/**/*.js"],
  theme: {
    extend: {
      fontFamily: {
        poppins: ["Poppins"],
        adobe: ['kepler-std-semicondensed-dis', "sans-serif"],   // name from Typekit
      }
    },
  },
  plugins: [],
};