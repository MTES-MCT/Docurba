export default (_, inject) => {
  inject('isDev', process.env.NODE_ENV === 'development')
}
