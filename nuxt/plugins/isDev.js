export default (_, inject) => {
  inject('isDev', process.env.USER_ENVIRONMENT === 'development')
}
