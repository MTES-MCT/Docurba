<template>
  <DataSourcesList v-if="!loading" :region="currentRegion" :data-sources="dataset" :themes="themes" />
  <VGlobalLoader v-else />
</template>

<script>
export default {
  data () {
    return {
      loading: true,
      project: null,
      dataset: null,
      themes: null
    }
  },
  computed: {
    currentRegion () {
      return this.project.region
    }
  },
  async mounted () {
    const projectId = this.$route.params.projectId

    const { data: projects } = await this.$supabase.from('projects').select('*').eq('id', projectId)
    this.project = projects ? projects[0] : null

    if (this.project) {
      const { dataset, themes } = await this.$daturba.getData(this.currentRegion, this.project.towns.map(t => t.code_commune_INSEE))

      this.dataset = dataset
      this.themes = themes

      // Start Analytics
      this.$matomo([
        'trackEvent', 'Projet PAC', 'Data',
          `${this.project.doc_type} - ${this.project.epci ? this.project.epci.label : this.project.towns[0].nom_commune}`
      ])
      // End Analytics
    }

    this.loading = false
  }
}
</script>
