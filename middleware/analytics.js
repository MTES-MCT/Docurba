export default ({ $analytics, route }) => {
  // console.log('analytics midleware', process.client, process.server, route.path)

  $analytics({
    category: 'page view',
    name: process.client ? 'navigate' : 'land',
    value: route.path
  })
}
