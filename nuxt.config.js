export default {
  // Global page headers: https://go.nuxtjs.dev/config-head
  head: {
    titleTemplate: '%s - docurba',
    title: 'docurba',
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { hid: 'description', name: 'description', content: '' }
    ],
    link: [
      { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
    ]
  },

  // Global CSS: https://go.nuxtjs.dev/config-css
  css: [
  ],

  // Plugins to run before rendering page: https://go.nuxtjs.dev/config-plugins
  plugins: [
    { src: '~/plugins/composition.js' },
    { src: '~/plugins/supabase.js' },
    { src: '~/plugins/user.js' }
  ],

  // Auto import components: https://go.nuxtjs.dev/config-components
  components: true,

  // Modules for dev and build (recommended): https://go.nuxtjs.dev/config-modules
  buildModules: [
    // https://go.nuxtjs.dev/eslint
    '@nuxtjs/eslint-module',
    // https://go.nuxtjs.dev/vuetify
    '@nuxtjs/vuetify'
  ],

  // Modules: https://go.nuxtjs.dev/config-modules
  modules: [
    // https://go.nuxtjs.dev/axios
    '@nuxtjs/axios',
    // https://go.nuxtjs.dev/pwa
    '@nuxtjs/pwa',
    // https://go.nuxtjs.dev/content
    '@nuxt/content'
  ],

  serverMiddleware: [
    { path: '/api/communes', handler: '~/server-middleware/communes.js' }
  ],

  // Axios module configuration: https://go.nuxtjs.dev/config-axios
  axios: {},

  // PWA module configuration: https://go.nuxtjs.dev/pwa
  pwa: {
    manifest: {
      lang: 'fr'
    }
  },

  // Content module configuration: https://go.nuxtjs.dev/config-content
  content: {},

  // Vuetify module configuration: https://go.nuxtjs.dev/config-vuetify
  vuetify: {
    treeShake: true,
    customVariables: ['~/assets/variables.scss'],
    icons: {
      iconfont: 'mdiSvg'
    },
    theme: {
      // dark: true,
      themes: {
        options: { customProperties: true },
        light: {
          primary: '#000091',
          secondary: '#e1000f',
          bf500: '#000091',
          'bf500-plain': '#000091',
          'w-bf500': '#fff',
          'bf300-plain': '#9a9aff',
          bf300: '#9a9aff',
          'bf200-bf300': '#ececff',
          'bf100-g750': '#f5f5ff',
          g800: '#1e1e1e',
          g700: '#383838',
          g600: '#6a6a6a',
          g500: '#9c9c9c',
          g400: '#cecece',
          g300: '#e7e7e7',
          g200: '#f0f0f0',
          g100: '#f8f8f8',
          w: '#fff',
          beige: '#f9f8f6',
          'g800-plain': '#1e1e1e',
          'g600-g400': '#6a6a6a',
          'g400-t': '#cecece',
          'g100-g800': '#f8f8f8',
          'w-g750': '#fff',
          focus: '#2a7ffe',
          info: '#0762c8',
          success: '#008941',
          error: '#e10600',
          rm300: '#f7bfc3',
          rm500: '#e1000f',
          'c-green-warm': '#169B62'
        }
      }
    },
    defaultAssets: {
      icons: false
    }
  },

  // Build Configuration: https://go.nuxtjs.dev/config-build
  build: {
    standalone: true
    // transpile: ['d3', 'd3-geo', 'internmap']
  }
}
