import axios from 'axios'
import departements from '@/assets/data/INSEE/departements_small.json'

export default ({ $supabase, $isDev, app }, inject) => {
  async function sendEvent (event) {
    const route = app.router.currentRoute

    const {
      data: { user }
    } = await $supabase.auth.getUser()

    let {
      collectiviteId
    } = route.params

    // TODO: ajouter le handle des gitRef ici
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
        const { data: collectivite } = await axios(`https://nuxt3.docurba.incubateur.net/api/geo/search/collectivites?code=${collectiviteId}`)
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
        user_id: user.id,
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
