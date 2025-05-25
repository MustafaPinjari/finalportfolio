module.exports = {
    content: ["./*.{html,js}"],
    theme: {
        extend: {
            fontFamily : {
                "ovo" : ["Ovo"],
                "outfit" : ["Outfit"]
            },
            colors:{
                lightHover : '#fcf4ff',
                darkHover : '#2a004a',
                darkTheme : '#11001F'
            },
            
            animation: {
                'spin-slow': 'spin 6s linear infinite',
            },
            boxShadow:{
                'black' : '4px 4px 0 #000',
                'white' : '4px 4px 0 #fff'
            }
            
            
        },
        plugins: [
            require('@tailwindcss/typography'),
        ],
        theme: {
            extend: {
                typography: {
                    DEFAULT: {
                        css: {
                            color: '#ffffff',
                            h1: { color: '#ff7f50' },
                            h2: { color: '#ff7f50' },
                            h3: { color: '#ff7f50' },
                            strong: { color: '#ff7f50' },
                            a: { color: '#ff7f50' },
                            blockquote: { color: '#ffffff' },
                            code: { color: '#ff7f50' },
                        },
                    },
                },
            },
        },
    },
    }

