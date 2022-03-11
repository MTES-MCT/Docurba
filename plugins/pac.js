export default (_, inject) => {
  inject('PAC', {
    pathToAnchor (path) {
      return path.replaceAll(/[^A-Za-z0-9]/g, '__')
    }
  })
}
