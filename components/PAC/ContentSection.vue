<template>
  <v-expansion-panels :value="open" multiple focusable flat>
    <v-expansion-panel v-for="(section, i) in sortedSections" :id="`panel__${section.path.replaceAll(/[^A-Za-z0-9]/g, '__')}`" :key="i">
      <v-expansion-panel-header @click="openSection(section)">
        {{ section.tocCounter ? `${section.tocCounter.join('.')} - ` : '' }} {{ section.name }}
      </v-expansion-panel-header>
      <v-expansion-panel-content eager>
        <v-row>
          <v-col cols="12">
            <nuxt-content class="pac-section-content" :document="section" />
            <PACSectionsAttachementsChips
              v-if="projectId && project"
              :section="section"
              :attachement-folders="[
                project.towns[0].code_departement,
                projectId
              ]"
            />
            <PACContentSection
              v-if="section.children && section.children.length"
              :sections="section.children"
              :open="section.titre === 'Introduction' ? [0] : []"
              :editable="editable"
            />
          </v-col>
        </v-row>
        <PACSectionsAttachementsCardList v-if="projectId" :section-path="section.path" :project-id="projectId" />
      </v-expansion-panel-content>
    </v-expansion-panel>
  </v-expansion-panels>
</template>

<script>
import { mdiCommentOutline } from '@mdi/js'

export default {
  props: {
    sections: {
      type: Array,
      required: true
    },
    editable: {
      type: Boolean,
      default: false
    },
    projectId: {
      type: String,
      default () {
        return this.$route.params.projectId
      }
    },
    open: {
      type: Array,
      default () {
        return []
      }
    }
  },
  data () {
    const filesMap = {}

    this.sections.forEach((section) => {
      filesMap[section.path] = []
    })

    return {
      icons: { mdiCommentOutline },
      selectedDataSources: [],
      project: null,
      files: filesMap
    }
  },
  computed: {
    sortedSections () {
      return this.sections.map(s => s).sort((sa, sb) => {
        return sa.ordre - sb.ordre
      })
    }
  },
  async mounted () {
    if (this.projectId) {
      const { data: projects } = await this.$supabase.from('projects').select('*').eq('id', this.projectId)
      this.project = projects ? projects[0] : null
    }
  },
  methods: {
    openSection (section) {
      // Start Analytics
      this.$matomo(['trackEvent', 'PAC Content', 'Open Section', section.titre])
      // End Analytics
    }
    // fetchAttachements () {
    //   const folders = [
    //     this.project.towns[0].code_departement,
    //     this.projectId
    //   ]

    //   this.sections.forEach((section) => {
    //     folders.forEach((folder) => {
    //       this.fetchFolderFiles(folder, section)
    //     })
    //   })
    // },
    // async fetchFolderFiles (folder, section) {
    //   // const folder = section.project_id || section.dept

    //   const { data: attachements, err } = await this.$supabase
    //     .storage
    //     .from('project-annexes')
    //     .list(`${folder}${section.path}`, {
    //       limit: 100,
    //       offset: 0,
    //       sortBy: { column: 'name', order: 'asc' }
    //     })

    //   if (!err) {
    //     this.files[section.path] = []

    //     for (let i = 0; i < attachements.length; i++) {
    //       const file = attachements[i]

    //       const { data } = await this.$supabase
    //         .storage
    //         .from('project-annexes')
    //         .createSignedUrl(`${folder}${section.path}/${file.name}`, 60 * 60)

    //       file.url = data.signedURL

    //       this.files[section.path].push(file)
    //     }
    //   } else {
    //     console.log('err fetching attachements', err)
    //   }
    // }
  }
}
</script>

<style>
 .pac-section-content img {
  max-width: 100%;
 }
</style>
