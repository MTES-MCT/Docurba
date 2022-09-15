export default (_, inject) => {
  // Default tracking code.
  const _paq = window._paq = window._paq || []
  /* tracker methods like "setCustomDimension" should be called before "trackPageView" */
  _paq.push(['trackPageView'])
  _paq.push(['enableLinkTracking']);
  (() => {
    const u = 'https://stats.data.gouv.fr/'
    _paq.push(['setTrackerUrl', u + 'piwik.php'])
    _paq.push(['setSiteId', '235'])
    const d = document; const g = d.createElement('script'); const s = d.getElementsByTagName('script')[0]
    g.async = true; g.src = u + 'piwik.js'; s.parentNode.insertBefore(g, s)

    const tracker = {}

    g.onload = () => {
      const _tracker = window.Matomo.getTracker('https://stats.data.gouv.fr/piwik.php', '235')
      Object.assign(tracker, _tracker)
    }

    // This part is specific to nuxt.
    // It should allow the use of this.$matomo in components.
    inject('matomo', tracker)
  })()
}
