<template>
  <LayoutsCustomApp>
    <template #headerPageTitle>
      - {{ project ? project.name : '' }}
    </template>
    <v-container v-if="!loading" fluid>
      <v-row>
        <v-col :cols="collapsedTree ? 1 : 4" class="collapse-transition">
          <client-only>
            <PACTreeviewEditing
              :value="project.PAC"
              :pac-data="PAC"
              :collapsed="collapsedTree"
              table="pac_sections_project"
              :project-id="$route.params.projectId"
              @open="selectSection"
              @add="addNewSection"
              @remove="deleteSection"
              @collapse="collapsedTree = !collapsedTree"
              @input="changeSelectedSections"
            />
          </client-only>
        </v-col>
        <v-col v-if="selectedSection" :cols="collapsedTree ? 11 : 8" class="fill-height collapse-transition">
          <PACContentSectionEditing
            :section="selectedSection"
            :pac-data="PAC"
            @save="saveSection"
          />
        </v-col>
        <v-col v-else cols="">
          <v-card flat color="g100">
            <v-card-text>Selectionnez une section à éditer.</v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
    <VGlobalLoader v-else />
  </LayoutsCustomApp>
</template>

<script>

import unified from 'unified'
import remarkParse from 'remark-parse'
import { omitBy, isNil } from 'lodash'

import unifiedPAC from '@/mixins/unifiedPac.js'

export default {
  mixins: [unifiedPAC],
  layout: 'app',
  async asyncData ({ $content }) {
    const PAC = await $content('PAC', {
      deep: true,
      text: true
    }).fetch()

    const originalPAC = PAC.map((section) => {
      return Object.assign({}, section)
    })

    return {
      PAC,
      originalPAC
    }
  },
  data () {
    return {
      project: null,
      loading: true,
      collapsedTree: false,
      selectedSection: null,
      projectSectionsSub: null
    }
  },
  async mounted () {
    const mdParser = unified().use(remarkParse)
    this.mdParser = mdParser

    const projectId = this.$route.params.projectId

    const { data: projects } = await this.$supabase.from('projects').select('*').eq('id', projectId)
    this.project = projects ? projects[0] : null

    // Subscribe to project changes for easy flux update
    this.projectSectionsSub = this.$supabase.from(`pac_sections_project:project_id=eq.${projectId}`).on('*', (update) => {
      const sectionIndex = this.PAC.findIndex(s => s.path === update.new.path)
      if (sectionIndex >= 0) {
        this.PAC.splice(sectionIndex, 1, Object.assign({}, this.PAC[sectionIndex], omitBy(update.new, isNil)))
      }
    }).subscribe()

    // Get the data from DB for each level of PAC for this project.
    const { data: deptSections } = await this.$supabase.from('pac_sections_dept').select('*').eq('dept', this.project.town.code_departement)
    const { data: projectSections } = await this.$supabase.from('pac_sections_project').select('*').eq('project_id', this.project.id)

    // Merge data of multiple PACs using unifiedPac.js mixin.
    this.PAC = this.unifyPacs([projectSections, deptSections, this.PAC])

    this.PAC.forEach((section) => {
      if (section.text) {
        section.body = mdParser.parse(section.text)
      }
    })

    this.loading = false
  },
  beforeDestroy () {
    if (this.projectSectionsSub) {
      this.$supabase.removeSubscription(this.projectSectionsSub)
    }
  },
  methods: {
    // This is duplicate from /projects/trame.vue
    selectSection (section) {
      const { text, titre, path, slug, dir, ordre } = this.PAC.find(s => s.path === section.path)

      this.selectedSection = {
        text,
        titre,
        path,
        slug,
        dir,
        ordre,
        project_id: this.project.id
      }
    },
    async saveSection (editedSection) {
      const { data: savedSection } = await this.$supabase.from('pac_sections_project').select('id').match({
        project_id: this.project.id, // This need to be dynamic.
        path: this.selectedSection.path
      })

      const newData = Object.assign({
        // dept: this.departementCode
      }, this.selectedSection, editedSection)

      if (savedSection[0]) { newData.id = savedSection[0].id }

      try {
        if (savedSection[0]) {
          await this.$supabase.from('pac_sections_project').upsert(newData)
        } else {
          await this.$supabase.from('pac_sections_project').insert([newData])
        }

        const sectionIndex = this.PAC.findIndex(s => s.path === newData.path)

        // this.PAC[sectionIndex] = newData
        this.PAC.splice(sectionIndex, 1, newData)
      } catch (err) {
        // eslint-disable-next-line no-console
        console.log('Error saving data')
      }
    },
    async addNewSection (newSection) {
      // newSection.dept = this.departementCode
      const { data: savedSection, err } = await this.$supabase.from('pac_sections_project').insert([Object.assign({
        project_id: this.project.id
      }, newSection)])

      if (savedSection && !err) {
        // console.log(savedSection)
        this.PAC.push(Object.assign({
          body: this.mdParser.parse(savedSection.text)
        }, savedSection[0]))
      } else {
        // eslint-disable-next-line no-console
        console.log('error adding new section', savedSection, err)
      }
    },
    async deleteSection (deletedSection) {
      const { data, err } = await this.$supabase
        .from('pac_sections_project')
        .delete()
        .match({
          project_id: this.project.id,
          path: deletedSection.path
        })

      // TODO: this will not work if section was added in trame AND project.
      // Maybe in edit mode of project, you can only delete projectSection, not trame section.
      // Like in trame you can not delete global sections.
      // Still the splice here should inject by a dept/trame section if it exist.
      if (data && !err) {
        const deletedSectionIndex = this.PAC.findIndex(s => s.path === deletedSection.path)
        const originalSection = this.originalPAC.find(s => s.path === deletedSection.path)

        if (originalSection) {
          this.PAC.splice(deletedSectionIndex, 1, originalSection)
        } else { this.PAC.splice(deletedSectionIndex, 1) }
      } else {
        // eslint-disable-next-line no-console
        console.log('err deleting a section')
      }
    },
    async changeSelectedSections (selectedSections) {
      // This make it so we can't save sections as objects in reading mode for comments and checked features.
      await this.$supabase.from('projects').update({
        PAC: selectedSections
      }).eq('id', this.project.id)
    }
  }
}
</script>

<style scoped>
.collapse-transition {
  transition: max-width 200ms;
}
</style>
