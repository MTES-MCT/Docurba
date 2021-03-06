export default (_, inject) => {
  // usage in components: this.$print(PATH_TO_PRINT)
  // Exemple: this.$print('/print/:projectId')
  inject('print', (path) => {
    return new Promise((resolve) => {
      function closePrint () {
        document.body.removeChild(this.__container__)
      }

      function setPrint () {
        setTimeout(() => {
          this.contentWindow.__container__ = this
          this.contentWindow.onbeforeunload = closePrint
          this.contentWindow.onafterprint = closePrint
          resolve()
          // this.contentWindow.focus() // Required for IE
          this.contentWindow.print()
        }, 2000)
      }

      const iframe = document.createElement('iframe')
      iframe.onload = setPrint
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
