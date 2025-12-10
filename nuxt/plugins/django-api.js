/* eslint-disable unicorn/no-anonymous-default-export */

export default ({ $axios }, inject) => {
  inject('djangoApi', {
    async get (path, parameters) {
      // eslint-disable-next-line n/prefer-global/process
      const { data: responseData } = await $axios.get(`${process.env.DJANGO_API_BASE_URL}${path}`, { params: parameters })
      if (responseData.results === undefined) {
        return responseData
      }

      const results = []
      results.push(...responseData.results)
      if (responseData.num_pages > 1) {
        let nextUrl = responseData.next
        while (nextUrl !== undefined) {
          const { data: response } = await $axios.get(nextUrl)
          results.push(...response.results)
          nextUrl = results.next
        }
      }

      return results
    }
  })
}
