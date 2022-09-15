export default ({ $matomo, route }) => {
  if (process.client) {
    if ($matomo && $matomo.trackPageView) {
      $matomo.trackPageView()
    } else {
      window._paq.push(['trackPageView'])
    }
  }
}
