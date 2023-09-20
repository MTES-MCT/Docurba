export default {
  // Global page headers: https://go.nuxtjs.dev/config-head
  head: {
    titleTemplate: '%s - Docurba',
    title: 'Docurba',
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { hid: 'description', name: 'description', content: '' }
    ],
    link: [
      { rel: 'icon', type: 'image/png', href: '/favicon.png' }
    ],
    script: [
      // { src: 'https://stats.data.gouv.fr/piwik.js', async: true }
    ]
  },
  // Global CSS: https://go.nuxtjs.dev/config-css
  css: [
  ],

  // Plugins to run before rendering page: https://go.nuxtjs.dev/config-plugins
  plugins: [

    { src: '~/plugins/dayjs.js' },
    { src: '~/plugins/isDev.js' },
    { src: '~/plugins/composition.js' },
    { src: '~/plugins/supabase.js' },
    { src: '~/plugins/supabaseAdmin.js', mode: 'server' },
    { src: '~/plugins/user.js' }, // Need to be after supabase plugin
    { src: '~/plugins/auth.js' }, // Need to be after user plugin
    { src: '~/plugins/pac.js' },
    { src: '~/plugins/daturba.js' },
    { src: '~/plugins/matomo.js', mode: 'client' },
    { src: '~/plugins/mdParser.js' },
    { src: '~/plugins/print.js', mode: 'client' },
    { src: '~/plugins/rules.js' },
    { src: '~/plugins/notifications.js', mode: 'client' },
    { src: '~/plugins/githubRefs.js' },
    { src: '~/plugins/urbanisator.js' },
    { src: '~/plugins/sudocu.js', mode: 'client' }
  ],

  // Auto import components: https://go.nuxtjs.dev/config-components
  components: true,

  // Modules for dev and build (recommended): https://go.nuxtjs.dev/config-modules
  buildModules: [
    // https://go.nuxtjs.dev/eslint
    '@nuxtjs/eslint-module',
    // https://go.nuxtjs.dev/vuetify
    '@nuxtjs/vuetify',
    '@nuxt/postcss8'
  ],

  // Modules: https://go.nuxtjs.dev/config-modules
  modules: [
    // https://go.nuxtjs.dev/axios
    '@nuxtjs/axios',
    // https://go.nuxtjs.dev/pwa
    '@nuxtjs/pwa',
    // https://go.nuxtjs.dev/content
    '@nuxt/content'
    // '@nuxtjs/sentry'
  ],
  // sentry: {
  //   dsn: 'https://f6730834cb3a4f14988bdf86b2e0b8bd@o4505403744649216.ingest.sentry.io/4505403746877440',
  //   tracing: {
  //     tracesSampleRate: 1.0
  //   },
  //   clientIntegrations: {
  //     CaptureConsole: {},
  //     Replay: {}
  //   },
  //   clientConfig: {
  //     // This sets the sample rate to be 10%. You may want this to be 100% while
  //     // in development and sample at a lower rate in production
  //     replaysSessionSampleRate: 0.1,
  //     // If the entire session is not sampled, use the below sample rate to sample
  //     // sessions when an error occurs.
  //     replaysOnErrorSampleRate: 1.0
  //   }
  // },
  render: {
    csp: {
      // hashAlgorithm: 'sha256',
      policies: {
        // 'default-src': ["'self'"],
        'script-src': [
          // "'self'",
          'https://stats.data.gouv.fr/piwik.js',
          'https://tally.so/widgets/embed.js'
        ]
      }
      // addMeta: true
    }
  },

  serverMiddleware: [
    '~/server-middleware/redirects.js',
    { path: '/api/admin', handler: '~/server-middleware/admin.js' },
    { path: '/api/auth', handler: '~/server-middleware/auth.js' },
    { path: '/api/communes', handler: '~/server-middleware/communes.js' },
    { path: '/api/epci', handler: '~/server-middleware/EPCI.js' },
    { path: '/api/geoide', handler: '~/server-middleware/geoide.js' },
    { path: '/api/georisques', handler: '~/server-middleware/georisques.js' },
    { path: '/api/pdf', handler: '~/server-middleware/pdf.js' },
    { path: '/api/pipedrive', handler: '~/server-middleware/pipedrive.js' },
    { path: '/api/projects', handler: '~/server-middleware/projects.js' },
    { path: '/api/slack', handler: '~/server-middleware/slack.js' },
    { path: '/api/stats', handler: '~/server-middleware/stats.js' },
    { path: '/api/trames', handler: '~/server-middleware/trames.js' },
    // Public documented APIs
    { path: '/api/geo', handler: '~/server-middleware/geo.js' },
    { path: '/api/urba', handler: '~/server-middleware/urba.js' }
  ],

  // Axios module configuration: https://go.nuxtjs.dev/config-axios
  axios: {},

  // PWA module configuration: https://go.nuxtjs.dev/pwa
  pwa: {
    manifest: {
      lang: 'fr'
    },
    workbox: {
      cleanupOutdatedCaches: true
    }
  },

  // Vue router
  router: {
    middleware: ['matomo']
  },

  // Content module configuration: https://go.nuxtjs.dev/config-content
  content: {},

  // Vuetify module configuration: https://go.nuxtjs.dev/config-vuetify
  vuetify: {
    treeShake: true,
    customVariables: ['~/assets/variables.scss'],
    icons: {
      iconfont: 'mdiSvg',
      chevronRight: 'mdiChevronRight'

    },
    theme: {
      options: { customProperties: true },
      themes: {
        light: {
          ongoing: {
            base: '#745B47',
            lighten1: '#F7ECE4'
          },
          typo: {
            base: '#232323'
          },
          primary: {
            base: '#000091',
            lighten1: '#E3E3FD',
            lighten2: '#0063CB',
            lighten3: '#F7F7FB',
            lighten4: '#F5F5FE'
          },
          grey: {
            base: '#DDDDDD'
          },
          secondary: '#e1000f',
          bf500: '#000091',
          'bf500-plain': '#000091',
          'w-bf500': '#fff',
          'bf300-plain': '#9a9aff',
          bf300: '#9a9aff',
          bf200: '#E8EDFF',
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
          beige: '#F9F8F6',
          'alt-beige': '#F6F6F6',
          'g800-plain': '#1e1e1e',
          'g600-g400': '#6a6a6a',
          'g400-t': '#cecece',
          'g100-g800': '#f8f8f8',
          'w-g750': '#fff',
          focus: '#6A6AF4',
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
      font: false,
      icons: false
    }
  },

  // Build Configuration: https://go.nuxtjs.dev/config-build
  build: {
    standalone: true,
    extend (config, { isClient }) {
      // Extend only webpack config for client-bundle
      if (isClient) {
        config.devtool = 'source-map'
      }
    }
    // filenames: {
    //   app: ({ isDev }) => '[name].js',
    //   chunk: ({ isDev }) => '[name].js',
    //   css: ({ isDev }) => '[name].css',
    //   img: ({ isDev }) => 'img/[name].[ext]',
    //   font: ({ isDev }) => 'fonts/[name].[ext]',
    //   video: ({ isDev }) => 'videos/[name].[ext]'
    // }
    // filenames: {
    //   app: ({ isDev }) => isDev ? '[name].js' : '[contenthash].js',
    //   chunk: ({ isDev }) => isDev ? '[name].js' : '[contenthash].js',
    //   css: ({ isDev }) => isDev ? '[name].css' : '[contenthash].css',
    //   img: ({ isDev }) => isDev ? '[path][name].[ext]' : 'img/[contenthash:7].[ext]',
    //   font: ({ isDev }) => isDev ? '[path][name].[ext]' : 'fonts/[contenthash:7].[ext]',
    //   video: ({ isDev }) => isDev ? '[path][name].[ext]' : 'videos/[contenthash:7].[ext]'
    // }
    // transpile: ['d3', 'd3-geo', 'internmap']
  }
}
