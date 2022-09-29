export default ({ $matomo, route }) => {
  if (process.client) {
    $matomo(['trackPageView'])
  }
}
