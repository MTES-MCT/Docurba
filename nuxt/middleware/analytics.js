export default ({ $supabase, $analytics, route, app }) => {
  // Skipping the first page event trigger because the user is not available
  // during server rendering
  if (!process.client) {
    return
  }

  const { resolved } = app.router.resolve(route.path)

  if (resolved.matched.length > 0) {
    $analytics({
      category: 'page view',
      name: 'navigate',
      value: route.path
    })
  }
}
