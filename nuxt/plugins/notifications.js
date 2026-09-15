export default ({ $nuxtApi }, inject) => {
  inject('notifications', {
    notifyUpdate (projectId) {
      return $nuxtApi.post('/api/projects/notify/update', {
        projectId
      })
    }
  })
}
