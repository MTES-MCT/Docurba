import _ from 'lodash'
import axios from 'axios'

export default ({ app, $supabase, $utils, $user }, inject) => {
  const sharing = {
    async  addToCollabs (procedure, collabs, collectivite) {
      let toInsert = collabs.map(e => ({
        user_email: e.email,
        project_id: procedure.project_id,
        shared_by: $user.id,
        notified: false,
        role: 'write_frise',
        archived: false,
        dev_test: true
      }))

      // TODO: ATTENTION RISQUE DE NE PAS MARCHER SUR LES SECONDAIRES a cause du project_id
      // Il faut founir le project_id de la procedure principale
      const sender = {
        user_email: $user.email,
        project_id: procedure.project_id ?? procedure.secondary_procedure_of.project_id,
        shared_by: $user.id,
        notified: false,
        role: 'write_frise',
        archived: false,
        dev_test: true
      }

      toInsert = [...toInsert, sender]
      console.log('TO INSERT: ', toInsert)
      const { error: errorInsertedCollabs } = await $supabase.from('projects_sharing').upsert(toInsert, { onConflict: 'project_id,user_email,role', ignoreDuplicates: true }).select()
      if (errorInsertedCollabs) { console.log('errorInsertedCollabs: ', errorInsertedCollabs) }

      let title = 'Invitation à collaborer sur Docurba'
      if ($user.profile.departement && $user.profile.side === 'etat') { title = `La DDT (M) du ${$user.profile.departement} vous invite à collaborer sur Docurba` }
      if (collectivite?.intitule && $user.profile.side === 'collectivite') { title = `La collectivité ${collectivite?.intitule} vous invite à collaborer sur Docurba` }
      await axios({
        url: '/api/slack/notify/frp_shared',
        method: 'post',
        data: {
          from: {
            email: $user.email,
            firstname: $user.profile.firstname,
            lastname: $user.profile.lastname,
            poste: `${$user.profile.poste ?? ''} ${$user.profile.other_poste ?? ''}`
          },
          to: {
            emailsFormatted: toInsert.map(e => e.user_email).reduce((acc, curr) => acc + ', ' + curr, '').slice(2),
            emails: toInsert.map(e => e.user_email)
          },
          type: 'frp',
          procedure: {
            id: procedure.id,
            project_id: procedure.project_id,
            url: `/frise/${procedure.id}`,
            name: $utils.formatProcedureName(procedure, collectivite)
          },
          title
        }
      })
    },
    async getSuggestedCollaborators (collectivite) {
      const {
        data: stateProfiles,
        error: errorCollaborators
      } = await $supabase.from('profiles').select('*').eq('departement', collectivite.departementCode).eq('side', 'etat').neq('email', $user.email)

      const { data: collectiviteProfiles, error: errorCollectiviteProfiles } = await $supabase.from('profiles').select('*')
        .eq('side', 'collectivite')
        .or(`collectivite_id.eq.${collectivite.code}, collectivite_id.eq.${collectivite.intercommunaliteCode}`)
      if (errorCollectiviteProfiles) { console.log('errorCollectiviteProfiles: ', errorCollectiviteProfiles) }

      let collaborators = [...stateProfiles, ...collectiviteProfiles].map(e => $utils.formatProfileToCreator(e))
      if (errorCollaborators) { throw errorCollaborators }

      collaborators = this.excludeTestCollabs(collaborators)
      return collaborators
    },
    async  getCollaborators (procedure, collectivite) {
      let legacyCollabs = []
      if (!procedure.shareable) {
        console.log('IS NOT SHAREABLE')
        const adminDept = _.uniq(procedure.procedures_perimetres.map(p => p.departement))
        const { data: stateProfiles, error: errorStateProfiles } = await $supabase.from('profiles').select('*')
          .in('departement', adminDept)
          .eq('side', 'etat')

        if (errorStateProfiles) { console.log('errorStateProfiles: ', errorStateProfiles) }

        const { data: collectiviteProfiles, error: errorCollectiviteProfiles } = await $supabase.from('profiles').select('*')
          .eq('side', 'collectivite')
          .or(`collectivite_id.eq.${collectivite.code}, collectivite_id.eq.${collectivite.intercommunaliteCode}`)
        if (errorCollectiviteProfiles) { console.log('errorCollectiviteProfiles: ', errorCollectiviteProfiles) }

        legacyCollabs = [...stateProfiles ?? [], ...collectiviteProfiles ?? []].map(e => ({ ...e, legacy_sudocu: true }))
      }

      const { data: collabsData, error: errorCollabs } = await $supabase.from('projects_sharing')
        .select('*')
        .eq('project_id', procedure.project_id)
        .eq('role', 'write_frise')
      if (errorCollabs) { console.log('errorCollabs: ', errorCollabs) }
      console.log('collabsData: ', collabsData, ' procedure.project_id: ', procedure.project_id)
      const emails = _.uniqBy(collabsData, e => e.user_email).map(e => e.user_email)

      const { data: profilesData, error: errorProfiles } = await $supabase.from('profiles').select('*').in('email', emails)
      if (errorCollabs) { console.log('errorProfiles: ', errorProfiles) }
      const allCollaborators = [...profilesData ?? [], ...legacyCollabs ?? []]
      const formattedProfiles = allCollaborators.map((e) => {
        if (e.user_id === procedure.owner_id) {
          e.initiator = true
        }
        return $utils.formatProfileToCreator(e)
      })

      const noProfilesCollabs = emails.filter(e => !profilesData.find(prof => prof.email === e)).map(e => ($utils.formatProfileToCreator({ email: e })))
      const finalCollabs = [...noProfilesCollabs, ...formattedProfiles]
      const uniqFinalCollabs = _.uniqBy(finalCollabs, e => e.email)
      return uniqFinalCollabs
      // const realCollabsOnly = this.excludeTestCollabs(uniqFinalCollabs)
      // return realCollabsOnly
    },
    excludeTestCollabs (collabs) {
      return collabs.filter((collab) => {
        const email = collab.email.toLowerCase()
        return !email.includes('test') &&
        !email.includes('docurba.beta.gouv') &&
        !email.includes('yopmail') &&
        !email.includes('okie09@hotmail.fr') &&
        !email.includes('celia.vermicelli@gmail.com') &&
        // !email.includes('julien@quantedsquare.com') &&
        !email.includes('fabien@quantedsquare.com') &&
        !email.includes('julien.zmiro@gmail.com') &&
        !email.includes(' vermicellicelia@gmail.com')
      })
    }
  }
  inject('sharing', sharing)
}
