/* eslint-disable no-unused-expressions */

export default ({ $supabase }, inject) => {
  window.STONLY_WID = '636871cd-8a1f-11ee-bc11-06cb0cb2a85e'

  !(function (s, t, o, n, l, y, w, g, d, e) {
    s.StonlyWidget || ((d = s.StonlyWidget = function () {
      d._api ? d._api.apply(d, arguments) : d.queue.push(arguments)
    }).scriptPath = n, d.apiPath = l, d.sPath = y, d.queue = [],
    (g = t.createElement(o)).async = !0, (e = new XMLHttpRequest()).open('GET', n + 'version?v=' + Date.now(), !0),
    e.onreadystatechange = function () {
      e.readyState === 4 && (g.src = n + 'stonly-widget.js?v=' +
  (e.status === 200 ? e.responseText : Date.now()), (w = t.getElementsByTagName(o)[0]).parentNode.insertBefore(g, w))
    }, e.send())
  }(window, document, 'script', 'https://stonly.com/js/widget/v2/'))

  $supabase.auth.onAuthStateChange(async (_, session) => {
    if (session) {
      const userId = session.user.id
      const { data: profiles } = await $supabase.from('profiles').select('side, poste').eq('user_id', userId)

      if (profiles[0]) {
        const { side, poste } = profiles[0]
        window.StonlyWidget('identify', userId, {
          side, poste
        })
      }
    }
  })

  inject('stonly', window.StonlyWidget)
}
