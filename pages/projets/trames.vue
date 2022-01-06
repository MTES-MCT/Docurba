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

import unified from 'unified'
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

    const mdParser = unified().use(remarkParse)

    deptSections.forEach((section) => {
      section.body = mdParser.parse(section.text)
    })

    PAC.forEach((section, i) => {
      const deptSection = deptSections.find(s => s.path === section.path)

      if (deptSection) {
        PAC[i] = deptSection
      }
    })

    return {
      PAC
    }
  },
  data () {
    return {
      selectedSection: null
    }
  },
  methods: {
    selectSection (section) {
      const { text, titre, path, slug, dir } = section

      this.selectedSection = {
        text, titre, path, slug, dir
      }
    },
    async saveSection (editedSection) {
      const { data: savedSection } = await this.$supabase.from('pac_sections_dept').select('id').match({
        dept: '10', // This need to be dynamic.
        path: this.selectedSection.path
      })

      console.log(savedSection)

      try {
        if (savedSection[0]) {
          await this.$supabase.from('pac_sections_dept').upsert(Object.assign({
            id: savedSection[0].id,
            dept: '10'
          }, this.selectedSection, editedSection))
        } else {
          await this.$supabase.from('pac_sections_dept').insert([Object.assign({
            dept: '10' // TODO: Make this dynamic from admin user data
          }, this.selectedSection, editedSection)])
        }
      } catch (err) {
        // eslint-disable-next-line no-console
        console.log('Error saving data')
      }
    }
  }
}
</script>
