import Qs from 'qs'

export default ({ $axios }, inject) => {
  const nuxtAxios = $axios.create({
    paramsSerializer: params => Qs.stringify(params, {
      arrayFormat: 'repeat',
      encode: false
    })
  })

  inject('nuxtApi', {
    delete (path, data = {}, config = {}) {
      return this.request(path, {
        method: 'delete',
        data,
        ...config
      })
    },
    get (path, params = {}, config = {}) {
      return this.request(path, {
        method: 'get',
        params,
        ...config
      })
    },
    post (path, data = {}, config = {}) {
      return this.request(path, {
        method: 'post',
        data,
        ...config
      })
    },
    put (path, data = {}, config = {}) {
      return this.request(path, {
        method: 'put',
        data,
        ...config
      })
    },
    async request (path, config = {}) {
      const { data, error } = await nuxtAxios(path, config)

      if (error) {
        throw error
      }

      return data
    }
  })
}
