<template>
  <LayoutsCustomApp>
    <template v-if="!loading" #headerPageTitle>
      - {{ (project && project.id ? project.name : $route.params.githubRef) | githubRef }}
    </template>
    <v-container v-if="!loading">
      <v-row>
        <v-col v-for="section in sections" :key="section.url" cols="12">
          <PACSectionCard
            :section="section"
            :git-ref="gitRef"
            :project="project"
          />
        </v-col>
      </v-row>
    </v-container>
    <VGlobalLoader v-else />
  </LayoutsCustomApp>
</template>

<script>
import axios from 'axios'
import orderSections from '@/mixins/orderSections.js'

export default {
  mixins: [orderSections],
  layout: 'app',
  data () {
    return {
      project: {},
      sections: [],
      gitRef: this.$route.params.githubRef,
      loading: true
    }
  },
  async mounted () {
    if (this.gitRef.includes('projet-')) {
      const projectId = this.gitRef.replace('projet-', '')

      const { data: projects } = await this.$supabase.from('projects').select('*').eq('id', projectId)
      this.project = projects ? projects[0] : {}
    }

    const { data: sections } = await axios({
      method: 'get',
      url: `/api/trames/tree/${this.gitRef}`
    })

    const { data: supSections } = await this.$supabase.from('pac_sections').select('*').in('ref', [
        `projet-${this.project.id}`,
        `dept-${this.project.towns ? this.project.towns[0].code_departement : ''}`,
        `region-${this.project.towns ? this.project.towns[0].code_region : ''}`,
        'main',
        this.gitRef
    ])

    this.orderSections(sections, supSections)

    function parseSection (section) {
      return Object.assign({
        children: section.children ? section.children.map(section => parseSection(section)) : []
      }, section)
    }

    this.sections = sections.map((section) => {
      return parseSection(section)
    })

    this.loading = false
  }
}
</script>
