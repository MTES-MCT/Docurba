export default function ({ store, route }) {
  store.commit('routeQueries', route.query)
}
