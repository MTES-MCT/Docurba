export default function ({ store, route }) {
  console.log('MIDDLEWARE: ', route.query)
  store.commit('routeQueries', route.query)
}
