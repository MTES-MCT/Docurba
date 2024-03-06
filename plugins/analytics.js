import axios from 'axios'
import departements from '@/assets/data/INSEE/departements_small.json'

export default ({ $supabase, $user, $isDev, app }, inject) => {
  async function sendEvent (event) {
    const route = app.router.currentRoute

    let {
      collectiviteId
    } = route.params

    const {
      projectId,
      procedureId
    } = route.params

    let dept = route.params.departement || null
    let region = null

    if (procedureId) {
      const { data: procedures } = await $supabase.from('procedures').select('collectivite_porteuse_id').eq('id', procedureId)
      collectiviteId = procedures[0].collectivite_porteuse_id
    }

    if (projectId) {
      const { data: projects } = await $supabase.from('projects').select('collectivite_id').eq('id', projectId)
      collectiviteId = projects[0].collectivite_id
    }

    if (collectiviteId) {
      try {
        const baseUrl = $isDev ? 'http://localhost:3000' : 'https://docurba.beta.gouv.fr'
        const { data: collectivite } = await axios(`${baseUrl}/api/geo/collectivites/${collectiviteId}`)
        dept = collectivite.departementCode
      } catch (err) {
        // eslint-disable-next-line no-console
        console.log('error analytics', collectiviteId)
      }
    }

    if (dept) {
      region = departements.find(d => d.code === dept).region.code
    }

    // console.log('analytics', collectiviteId, dept, region)

    if (!$isDev) {
      await $supabase.from('analytics_events').insert([Object.assign({
        user_id: $user.id,
        path: route.path,
        collectivite_id: collectiviteId,
        project_id: projectId,
        procedure_id: procedureId,
        dept,
        region
      }, event)])
    }
  }

  inject('analytics', sendEvent)
}
