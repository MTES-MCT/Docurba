export default (_, inject) => {
  // usage in components: this.$print(PATH_TO_PRINT)
  // Exemple: this.$print('/print/:projectId')
  inject('print', (path) => {
    return new Promise((resolve) => {
      const iframe = document.createElement('iframe')

      function setPrint () {
        iframe.contentWindow.onbeforeunload = closePrint
        iframe.contentWindow.onafterprint = closePrint
        resolve()
        // this.contentWindow.focus() // Required for IE
        iframe.contentWindow.print()
      }

      function closePrint () {
        document.body.removeChild(iframe.__container__)
      }

      window.addEventListener('message', setPrint)

      // iframe.onload = setPrint
      iframe.src = `${window.location.origin}${path}`
      iframe.style.position = 'fixed'
      // iframe.style.display = 'none'
      iframe.style.right = '0'
      iframe.style.bottom = '0'
      iframe.style.width = '210mm'
      iframe.style.height = '0'
      iframe.style.border = '0'
      document.body.appendChild(iframe)
    })
  })
}
