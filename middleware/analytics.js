export default ({ $analytics, route, app }) => {
  $analytics({
    category: 'page view',
    name: process.client ? 'navigate' : 'land',
    value: route.path
  })
}
