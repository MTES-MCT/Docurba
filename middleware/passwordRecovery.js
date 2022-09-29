export default ({ route }) => {
  // The user will be redirected to this url in case of password recovery.
  // https://docurba.beta.gouv.fr/#access_token=XXX&expires_in=3600&refresh_token=XXX&token_type=bearer&type=recovery

  if (process.client) {
    console.log('Route', process.client, route.hash)
  }
}
