<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1>Mes porter à connaissance (PAC)</h1>
      </v-col>
      <v-col v-if="!loading" cols="12">
        <v-row>
          <v-col cols="4">
            <v-text-field v-model="search" outlined hide-details label="Recherche" :append-icon="icons.mdiMagnify" />
          </v-col>
        </v-row>
        <v-row>
          <v-col v-for="project in filteredProjects" :key="project.key" cols="12">
            <DashboardEmptyProjectCard :project="project" :collectivity="project.collectivity" />
          </v-col>
        </v-row>
      </v-col>
      <VGlobalLoader v-else />
    </v-row>
  </v-container>
</template>

<script>
import { mdiMagnify } from '@mdi/js'
import axios from 'axios'

export default {
  layout: 'ddt',
  data () {
    return {
      projects: [],
      search: '',
      icons: {
        mdiMagnify
      },
      loading: true
    }
  },
  computed: {
    filteredProjects () {
      if (!this.search) { return this.projects }

      const normalizedSearch = this.search.toLocaleLowerCase().normalize('NFKD').replace(/\p{Diacritic}/gu, '')

      return this.projects.filter((project) => {
        let searchString = `${project.name} ${project.doc_type} ${project.collectivity.intitule} ${project.collectivity.code}`
        searchString = searchString.toLocaleLowerCase().normalize('NFKD').replace(/\p{Diacritic}/gu, '')

        return searchString.includes(normalizedSearch)
      })
    }
  },
  async mounted () {
    const { data: communes } = await axios('/api/geo/communes?departementCode=01')
    const { data: intercomunalites } = await axios('/api/geo/intercommunalites?departementCode=01')

    // console.log(communes, intercomunalites)

    const { data: projects } = await this.$supabase.from('projects').select('id, name, doc_type, towns, collectivite_id, PAC, trame, region').match({
      owner: this.$user.id,
      archived: false
    })

    function findCollectivity (code) {
      return intercomunalites.find(i => i.code === code) || communes.find(c => c.code === code)
    }

    projects.forEach((project) => {
      const collectivity = findCollectivity(project.collectivite_id)
      project.collectivity = collectivity
    })

    this.projects = projects.filter(project => !!project.collectivity)
    this.loading = false
  }
}
</script>
