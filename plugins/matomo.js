export default (_, inject) => {
  // Default tracking code.
  const _paq = window._paq = window._paq || [] /* tracker methods like "setCustomDimension" should be called before "trackPageView" */
  _paq.push(['trackPageView'])
  _paq.push(['enableLinkTracking']);
  (function () {
    const u = 'https://stats.beta.gouv.fr/'
    _paq.push(['setTrackerUrl', u + 'matomo.php'])
    _paq.push(['setSiteId', '69'])
    const d = document; const g = d.createElement('script'); const s = d.getElementsByTagName('script')[0]
    g.async = true; g.src = u + 'matomo.js'
    s.parentNode.insertBefore(g, s)
  })()

  // This part is specific to nuxt.
  // It should allow the use of this.$matomo in components instead of _paq.push(arr)
  // Exemple: this.$matomo(['trackEvent', 'Contact', 'Email Link Click', 'name@example.com'])
  inject('matomo', (argsArr) => {
    window._paq.push(argsArr)
  })
}
