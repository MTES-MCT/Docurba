export default (_, inject) => {
  inject('gtag', () => {
    const gtagScript = document.createElement('script')
    gtagScript.async = true
    gtagScript.setAttribute('src', 'https://www.googletagmanager.com/gtag/js?id=AW-11434835828')
    document.head.appendChild(gtagScript)

    window.dataLayer = window.dataLayer || []
    window.gtag = function () { window.dataLayer.push(arguments) }
    window.gtag('js', new Date())
    window.gtag('config', 'AW-11434835828')
  })
}
