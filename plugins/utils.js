export default ({ app }, inject) => {
  const utils = {
    formatEventProfileToCreator (event) {
      if (event.profiles) {
        let creator = null
        if (event.profiles.firstname && event.profiles.lastname) {
          creator = { avatar: event.profiles.firstname[0], label: `${event.profiles.firstname} ${event.profiles.lastname}` }
        } else if (event.profiles.email) {
          creator = { avatar: event.profiles?.email[0], label: `${event.profiles?.email}` }
        }
        creator.color = event.profiles.side === 'etat' ? '#69DF97' : '#FA7659'
        return creator
      } else if (event.from_sudocuh) {
        return { avatar: 'S', label: 'Sudocuh', color: '#3A3A3A' }
      } else {
        return { avatar: 'D', label: 'Docurba', color: 'primary' }
      }
    }
  }
  inject('utils', utils)
}
