export default (_, inject) => {
  inject('nuxt3api', async function (path) {
    const res = await fetch(`${process.env.NUXT3_API_URL}${path}`)
    return await res.json()
  })
}
