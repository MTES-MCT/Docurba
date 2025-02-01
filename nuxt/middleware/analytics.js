export default ({ $supabase, $analytics, route, app }) => {
  const { resolved } = app.router.resolve(route.path)

  if (resolved.matched.length > 0) {
    $analytics({
      category: 'page view',
      name: process.client ? 'navigate' : 'land',
      value: route.path
    })
  }
}
