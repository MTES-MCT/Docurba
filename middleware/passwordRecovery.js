export default ({ route }) => {
  // The user will be redirected to this url in case of password recovery.
  // https://docurba.beta.gouv.fr/#access_token=XXX&expires_in=3600&refresh_token=XXX&token_type=bearer&type=recovery

  console.log('Route', process.client, route)

  if (route.hash && route.hash.includes('type=recovery')) {
    console.log('route.hash', process.client, route.hash)
    route.push(`${route.path}${route.hash.replace('#', '?')}`)
  }
}
