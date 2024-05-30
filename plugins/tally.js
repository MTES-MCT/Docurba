export default (_, inject) => {
  const tallyScript = document.createElement('script')
  tallyScript.setAttribute('src', 'https://tally.so/widgets/embed.js')
  tallyScript.setAttribute('async', true)
  document.head.appendChild(tallyScript)

  inject('tally', (formId, config) => {
    const displayedKey = `tally-displayed-${formId}`
    const timestampKey = `tally-timestamp-${formId}`

    const formTimestamp = window.localStorage.getItem(timestampKey) || 0
    const formNb = window.localStorage.getItem(displayedKey) || 0

    const weeks = 1000 * 60 * 60 * 24 * 7 * 3
    const delay = Date.now() - formTimestamp

    if (formNb < 3 && delay > weeks) {
      window.TallyConfig = {
        formId,
        popup: Object.assign({
          open: {
            trigger: 'time',
            ms: 3000
          },
          hideTitle: true,
          autoClose: 2000,
          doNotShowAfterSubmit: true
        }, config)
      }

      setTimeout(() => {
        window.Tally.openPopup(formId)
      }, 3000)

      localStorage.setItem(displayedKey, +formNb + 1)
      localStorage.setItem(timestampKey, Date.now())
    }
  })
}
