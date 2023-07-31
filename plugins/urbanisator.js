import axios from 'axios'
import regions from '@/assets/data/Regions.json'

export default ({ route, store, $supabase, $user, $dayjs, $sudocu }, inject) => {
  inject('urbanisator', {
    isEpci (collectiviteId) {
      return collectiviteId.toString().length > 5
    },
    getRegionDetails (regionCode) {
      if (typeof regionCode === 'number') { regionCode = regionCode.toString() }
      return regions.find(e => e.code.toString().padStart(2, '0') === regionCode)
    },
    // This is not used
    // async createProject ({ collectiviteId, docType, typeProcedure, attachementsProcedure = null, startDate = null }) {
    //   try {
    //     // TODO: Attention en fonction du type de procedure, traitement possible pour faire des sub procedure
    //     const project = Object.assign({
    //       owner: $user.id,
    //       doc_type: this.DUType,
    //       collectivite_id: collectiviteId,
    //       // TODO FAIRE UN WEBHOOK POUR UPDATE TOWNS & EPCI
    //       towns: this.isEpci ? this.collectivite.towns : [this.collectivite],
    //       epci: this.isEpci ? { EPCI: this.collectivite.EPCI } : null

    //     })
    //     const { data: newProject, error: errorNewProject } = await this.$supabase.from('projects').insert([project]).select()
    //     if (errorNewProject) { throw new Error(errorNewProject) }
    //     const newEvents = [{
    //       type: typeProcedure,
    //       // Date spécifié dans la dépot de prescription, sinon date du jour
    //       date_iso: startDate ?? $dayjs().format('YYYY-MM-DD'),
    //       description: '',
    //       // TODO: Depend du user role, on ne l'a pas encore fait, a mettre a jour quand on aura le systeme
    //       actors: [],
    //       // TODO: ATTACH LE DOCUMENT DE PRESCRIPTION ?
    //       attachements: [],
    //       project_id: newProject[0].id
    //     }, {
    //       type: 'Socle de PAC',
    //       date_iso: $dayjs().format('YYYY-MM-DD'),
    //       description: 'Vous pouvez consulter votre Socle de PAC',
    //       actors: [],
    //       attachements: attachementsProcedure,
    //       project_id: newProject[0].id
    //     }]
    //     const { data: savedEvents, error: errorSavedEvents } = await $supabase.from('doc_frise_events').insert(newEvents).select()
    //     if (errorSavedEvents) { throw new Error(errorSavedEvents) }
    //     return { project: newProject, events: savedEvents }
    //   } catch (error) {
    //     // eslint-disable-next-line no-console
    //     console.log('Error createProject: ', error)
    //   }
    // },
    async getCurrentCollectivite (collectiviteId) {
      try {
        const { data: collectivite } = await axios({
          url: `/api/${this.isEpci(collectiviteId) ? 'epci' : 'communes'}/${collectiviteId}`,
          method: 'get'
        })

        const isEpci = this.isEpci(collectiviteId)
        collectivite.id = isEpci ? collectivite.EPCI : collectivite.code_commune_INSEE.toString().padStart(5, '0')
        collectivite.name = isEpci ? collectivite.label : collectivite.nom_commune
        collectivite.type = isEpci ? 'epci' : 'commune'
        const regionCode = isEpci ? collectivite.towns[0].code_region : collectivite.code_region
        collectivite.region = this.getRegionDetails(regionCode)
        return collectivite
      } catch (error) {
        // eslint-disable-next-line no-console
        console.log('Error getCurrentCollectivite: ', error)
      }
    },
    async getProjectsProcedures (collectiviteId) {
      // Fetching user procedure for now. Should also fetch public projects at some point.
      // Or more simply fetch based on collectivite column but need to make a script to update projects.
      const { data: projects } = await $supabase.from('projects').select('id, name, doc_type, towns, collectivite_id').match({
        owner: $user.id, // TODO: fetch shared projects.
        collectivite_id: collectiviteId
      })

      const projectsIds = projects.map(p => p.id)

      const { data: procedures } = await $supabase.from('procedures').select('*').in('project_id', projectsIds)

      procedures.forEach((procedure) => {
        procedure.project = projects.find(p => p.id === procedure.project_id)

        procedure.procSecs = procedures.filter(proc => proc.procedure_id === procedure.id)
      })

      projects.forEach((project) => {
        project.procedures = procedures.filter((proc) => {
          return proc.project_id === project.id
        })
      })

      return {
        projects,
        procedures
      }
    }
  })
}
