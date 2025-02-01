// This could be changed to be dynamic in dev mode ?
// const BASE_URL = 'http://localhost:3001'
const BASE_URL = 'https://nuxt3.docurba.incubateur.net'

export default (_, inject) => {
  inject('nuxt3api', async function (path) {
    const res = await fetch(`${BASE_URL}${path}`)
    return await res.json()
  })
}
