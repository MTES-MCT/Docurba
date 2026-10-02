import Qs from 'qs'

export default ({ $axios, $user }, inject) => {
  const nuxtAxios = $axios.create({
    baseURL: process.env.APP_URL,
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
      const { data, error } = await nuxtAxios(path, {
        ...config,
        headers: {
          'Supabase-Authorization': $user.supabase_access_token || undefined,
          ...(config.headers ?? {})
        }
      })

      if (error) {
        throw error
      }

      return data
    }
  })
}
