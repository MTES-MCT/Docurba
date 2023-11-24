export default (_, inject) => {
  inject('rules', {
    required (v) {
      if (v && typeof (v) === 'object') {
        if (typeof (v.length) === 'number') {
          return v.length > 0
        } else {
          return Object.keys(v).length > 0
        }
      } else { return !!v }
    }
  })
}
