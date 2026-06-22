import Qs from 'qs'

export default ({ $axios, $user }, inject) => {
  const djangoAxios = $axios.create({
    baseURL: process.env.DJANGO_API_BASE_URL,
    paramsSerializer: params => Qs.stringify(params, { arrayFormat: 'repeat', encode: false })
  })
  inject('djangoApi', {
    async get (path, parameters) {
      const requestOpts = { params: parameters }
      if ($user.supabase_access_token) {
        requestOpts.headers = { 'Supabase-Authorization': $user.supabase_access_token }
      }
      const { data: responseData } = await djangoAxios.get(path, requestOpts)
      if (responseData.results === undefined) {
        return responseData
      }

      const results = []
      results.push(...responseData.results)
      if (responseData.num_pages > 1) {
        let nextUrl = responseData.next
        while (nextUrl !== null) {
          const { data: response } = await $axios.get(nextUrl)
          results.push(...response.results)
          nextUrl = response.next
        }
      }

      return results
    }
  })
}
