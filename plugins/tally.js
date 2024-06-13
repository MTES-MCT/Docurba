export default (_, inject) => {
  const tallyScript = document.createElement('script')
  tallyScript.setAttribute('src', 'https://tally.so/widgets/embed.js')
  tallyScript.setAttribute('async', true)
  document.head.appendChild(tallyScript)

  inject('tally', (formId, config = { max: 3 }) => {
    const displayedKey = `tally-displayed-${formId}`
    const timestampKey = `tally-timestamp-${formId}`

    // const formTimestamp = window.localStorage.getItem(timestampKey) || 0
    const formNb = window.localStorage.getItem(displayedKey) || 0

    // const weeks = 1000 * 60 * 60 * 24 * 7 * 3
    // const delay = Date.now() - formTimestamp

    if (formNb < config.max) {
      const options = Object.assign({
        hideTitle: true,
        doNotShowAfterSubmit: true
      }, config)

      setTimeout(() => {
        localStorage.setItem(displayedKey, +formNb + 1)
        localStorage.setItem(timestampKey, Date.now())
        window.Tally.openPopup(formId, options)
      }, 3000)
    }
  })
}
