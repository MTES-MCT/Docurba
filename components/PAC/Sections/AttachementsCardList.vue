<template>
  <v-row>
    <v-col v-for="source in cardsDataList" :key="source.id" cols="12" sm="6" md="4">
      <DataSourceCard :source="source" />
    </v-col>
  </v-row>
</template>

<script>
import axios from 'axios'

export default {
  props: {
    sectionPath: {
      type: String,
      required: true
    },
    projectId: {
      type: String,
      required: true
    }
  },
  data () {
    return {
      cardsDataList: []
    }
  },
  async mounted () {
    const { data: sources } = await this.$supabase.from('sections_data_sources').select('*').match({
      project_id: this.projectId,
      section_path: this.sectionPath
    })

    const sourcesCardsData = await Promise.all(sources.map(async (source) => {
      const { data } = await axios({
        url: source.url,
        meyhod: 'get'
      })

      return Object.assign(data, { sourceId: source.id })
    }))

    this.cardsDataList = sourcesCardsData
  }
}
</script>
