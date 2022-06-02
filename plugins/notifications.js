import axios from 'axios'

export default (_, inject) => {
  inject('notifications', {
    notifyUpdate (projectId) {
      return axios({
        method: 'post',
        url: '/api/projects/notify/update',
        data: {
          projectId
        }
      })
    }
  })
}
