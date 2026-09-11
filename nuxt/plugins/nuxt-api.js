import Qs from 'qs'

export default ({ $axios, $user }, inject) => {
  const nuxtAxios = $axios.create({
    paramsSerializer: params => Qs.stringify(params, { arrayFormat: 'repeat', encode: false })
  })

  function getRequestHeaders () {
    return $user.supabase_access_token
      ? { 'Supabase-Authorization': $user.supabase_access_token }
      : undefined
  }

  inject('nuxtApi', {
    async get (path, params) {
      const { data, error } = await nuxtAxios.get(path, {
        headers: getRequestHeaders(),
        params
      })

      if (error) {
        throw error
      }

      return data
    },
    async post (path, params) {
      const { data, error } = await nuxtAxios.post(path, params, {
        headers: getRequestHeaders()
      })

      if (error) {
        throw error
      }

      return data
    }
  })
}
