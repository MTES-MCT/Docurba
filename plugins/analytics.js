export default ({ $supabase, route, $user, $isDev }, inject) => {
  async function sendEvent (event) {
    if (!$isDev) {
      await $supabase.from('analytics_events').insert([Object.assign({
        user_id: $user.id,
        path: route.path
      }, event)])
    }
  }

  inject('analytics', sendEvent)
}
