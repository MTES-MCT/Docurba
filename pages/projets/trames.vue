<template>
  <LayoutsCustomApp>
    <v-container fluid>
      <v-row>
        <v-col cols="4">
          <client-only>
            <PACTreeviewEditing :pac-data="PAC" @open="selectSection" />
          </client-only>
        </v-col>
        <v-col v-if="selectedSection" cols="8">
          <PACContentSectionEditing :text="selectedSection.text" :titre="selectedSection.titre" @save="saveSection" />
        </v-col>
        <v-col v-else cols="8">
          <v-card flat color="g100">
            <v-card-text>Selectionnez une section à éditer.</v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </LayoutsCustomApp>
</template>

<script>

import { unified } from 'unified'
import remarkParse from 'remark-parse'

export default {
  layout: 'app',
  async asyncData ({ $content, $supabase }) {
    const PAC = await $content('PAC', {
      deep: true,
      text: true
    }).fetch()

    // TODO: Make dept eq dynamique with user data.
    const { data: deptSections } = await $supabase.from('pac_sections_dept').select('*').eq('dept', '10')

    return {
      PAC,
      deptSections
    }
  },
  data () {
    return {
      selectedSection: null
    }
  },
  mounted () {
    const mdParser = unified().use(remarkParse)

    this.deptSections.forEach((section) => {
      section.body = mdParser.parse(section.text)

      console.log(section.body)
    })
  },
  methods: {
    selectSection (section) {
      const { text, titre, path } = section

      this.selectedSection = {
        text, titre, path
      }
    },
    async saveSection (editedSection) {
      const { data, error } = await this.$supabase.from('pac_sections_dept').insert([Object.assign({
        path: this.selectedSection.path,
        dept: '10' // TODO: Make this dynamic from admin user data
      }, editedSection)])

      if (!error && data) {
        console.log(data)
        // TODO: Replace PAC at path by the saved section using the content parser.
      } else {
        // eslint-disable-next-line no-console
        console.log('Error saving section', error, data)
      }
    }
  }
}
</script>
