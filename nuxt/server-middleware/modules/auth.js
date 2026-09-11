import supabase from './supabase'

export async function requireAuthenticated (req, validate = () => true) {
  const jwt = req.headers['supabase-authorization']

  if (!jwt) {
    throw new Error('Authentication failed')
  }

  const { data: userData, error: userError } = await supabase.auth.getUser(jwt)

  if (userError || !userData?.user) {
    throw new Error('Authentication failed')
  }

  const { data: profile, profileError } = await supabase.from('profiles')
    .select('*')
    .eq('email', userData.user.email)
    .limit(1)
    .maybeSingle()

  if (
    profileError ||
    !profile ||
    (!profile.is_admin && !validate(profile))
  ) {
    throw new Error('Authentication failed')
  }

  return profile
}

export async function requireProcedureSharable (req, validate = () => true) {
  const profile = await requireVerified(req, validate)

  if (profile.is_admin) {
    return profile
  }

  const procedureId = req.body?.procedure?.id

  if (!procedureId) {
    throw new Error('Authentication failed')
  }

  const { data: procedure, error: procedureError } = await supabase.from('procedures')
    .select('collectivite_porteuse_id,procedures_perimetres(collectivite_code,collectivite_type)')
    .eq('id', procedureId)
    .limit(1)
    .maybeSingle()

  if (procedureError || !procedure || ((
    profile.side !== 'etat' ||
    procedure.procedures_perimetres.every(
      ({ departement }) => departement !== profile.departement
    )
  ) && (
    profile.side !== 'collectivite' ||
    (
      procedure.collectivite_porteuse_id !== profile.collectivite_id &&
      procedure.procedures_perimetres.every(perimetre =>
        perimetre.collectivite_type !== 'COM' ||
        perimetre.collectivite_code !== profile.collectivite_id
      )
    )
  ))) {
    throw new Error('Authentication failed')
  }

  return profile
}

export async function requireRefRoles (req, roles, validate = () => true) {
  const profile = await requireStateAgent(req, profile =>
    ['ddt', 'dreal'].includes(profile.poste) && validate(profile)
  )

  if (profile.is_admin) {
    return profile
  }

  const ref = req.body?.ref

  if (!ref) {
    throw new Error('Authentication failed')
  }
  if (ref.includes('projet-')) {
    const projectId = ref.replace('projet-', '')
    const { data: project, error: projectError } = await supabase.from('projects')
      .select('owner')
      .eq('id', projectId)
      .limit(1)
      .maybeSingle()
    const { data: sharings, error: sharingsError } = await supabase.from('projects_sharing')
      .select('role')
      .match({
        project_id: projectId,
        user_email: profile.email
      })

    if (projectError || sharingsError || (
      project?.owner !== profile.user_id &&
      !sharings.find(({ role }) => roles.includes(role))
    )) {
      throw new Error('Authentication failed')
    }
  } else if (ref.includes('dept-')) {
    if (profile.poste !== 'ddt' || !ref.includes(+profile.departement)) {
      throw new Error('Authentication failed')
    }
  } else if (ref.includes('region-')) {
    if (profile.poste !== 'dreal' || !ref.includes(+profile.region)) {
      throw new Error('Authentication failed')
    }
  }

  return profile
}

export function requireStateAgent (req, validate = () => true) {
  return requireVerified(req, profile =>
    profile.side === 'etat' && validate(profile)
  )
}

export function requireVerified (req, validate = () => true) {
  return requireAuthenticated(req, profile =>
    profile.verified && validate(profile)
  )
}
