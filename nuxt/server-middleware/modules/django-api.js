import axios from 'axios'
import qs from 'qs'

const djangoAxios = axios.create({
  baseURL: process.env.DJANGO_API_BASE_URL,
  paramsSerializer: params => qs.stringify(params, {
    arrayFormat: 'repeat',
    encode: false
  })
})

module.exports = {
  async get (path, params) {
    const { data } = await djangoAxios.get(path, { params })

    if (!('results' in data)) {
      return data
    }

    const results = [...data.results]

    if (data.num_pages > 1) {
      let nextUrl = data.next

      while (nextUrl) {
        const { data: nextData } = await axios.get(nextUrl)
        results.push(...nextData.results)
        nextUrl = nextData.next
      }
    }

    return results
  }
}
