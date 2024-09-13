export default ({ redirect, $user, $supabase }, inject) => {
  inject('refRole', async (gitRef, allowedRoles, publicUrl) => {
    await $user.isReady

    if (!['ddt', 'dreal'].includes($user.profile.poste)) {
      redirect(publicUrl)
    } if ($user.profile.is_admin) {
      return true
    } else if (gitRef.includes('projet-')) {
      const { data: projects } = await $supabase.from('projects')
        .select('owner').eq('id', gitRef.replace('projet-', ''))

      const { data: sharings } = await $supabase
        .from('projects_sharing')
        .select('id, role')
        .match({
          user_email: $user.email,
          project_id: gitRef.replace('projet-', '')
        })

      const sharing = sharings.find((s) => {
        return allowedRoles.includes(s.role)
      })

      if (projects[0].owner !== $user.id && !sharing) {
        redirect(publicUrl)
      }
    } else if (gitRef.includes('dept-')) {
      if ($user.profile.poste !== 'ddt' || !gitRef.includes(+$user.profile.departement)) {
        redirect(publicUrl)
      }
    } else if (gitRef.includes('region-')) {
      if ($user.profile.poste !== 'dreal' || !gitRef.includes(+$user.profile.region)) {
        redirect(publicUrl)
      }
    }
  })
}
