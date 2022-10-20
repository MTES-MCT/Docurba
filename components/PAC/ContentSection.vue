<template>
  <v-expansion-panels :value="open" multiple focusable flat>
    <v-expansion-panel v-for="(section, i) in sortedSections" :id="`panel__${section.path.replaceAll(/[^A-Za-z0-9]/g, '__')}`" :key="i">
      <v-hover v-slot="{hover}">
        <v-expansion-panel-header @click="openSection(section)">
          <v-row align="center">
            <v-col cols="auto">
              {{ section.tocCounter ? `${section.tocCounter.join('.')} - ` : '' }} {{ section.titre }}
            </v-col>
            <v-spacer />
            <v-col v-if="editable" cols="auto" class="py-0">
              <v-dialog max-width="1000">
                <template #activator="{on}">
                  <v-badge
                    :content="section.comments.length"
                    :value="section.comments.length"
                    offset-x="17"
                    offset-y="17"
                  >
                    <v-btn
                      v-show="hover || section.comments.length"
                      depressed
                      tile
                      icon
                      v-on="on"
                    >
                      <v-icon color="secondary">
                        {{ icons.mdiCommentOutline }}
                      </v-icon>
                    </v-btn>
                  </v-badge>
                </template>
                <PACCommentCard :section="section" />
              </v-dialog>
            </v-col>
          </v-row>
        </v-expansion-panel-header>
      </v-hover>
      <v-expansion-panel-content eager>
        <nuxt-content :document="section" />
        <PACSectionsAttachementsChips v-if="files[section.path]" small :files="files[section.path]" />
        <PACContentSection
          v-if="section.children && section.children.length"
          :sections="section.children"
          :open="section.titre === 'Introduction' ? [0] : []"
          :editable="editable"
        />
        <PACSectionsAttachementsCardList :section-path="section.path" :project-id="projectId" />
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

      if (this.project) {
        this.fetchAttachements()
      }
    }
  },
  methods: {
    openSection (section) {
      // Start Analytics
      this.$matomo(['trackEvent', 'PAC Content', 'Open Section', section.titre])
      // End Analytics
    },
    fetchAttachements () {
      const folders = [
        this.project.towns[0].code_departement,
        this.projectId
      ]

      this.sections.forEach((section) => {
        folders.forEach((folder) => {
          this.fetchFolderFiles(folder, section)
        })
      })
    },
    async fetchFolderFiles (folder, section) {
      // const folder = section.project_id || section.dept

      const { data: attachements, err } = await this.$supabase
        .storage
        .from('project-annexes')
        .list(`${folder}${section.path}`, {
          limit: 100,
          offset: 0,
          sortBy: { column: 'name', order: 'asc' }
        })

      if (!err) {
        this.files[section.path] = []

        for (let i = 0; i < attachements.length; i++) {
          const file = attachements[i]

          const { data } = await this.$supabase
            .storage
            .from('project-annexes')
            .createSignedUrl(`${folder}${section.path}/${file.name}`, 60 * 60)

          file.url = data.signedURL

          this.files[section.path].push(file)
        }
      } else {
        console.log('err fetching attachements', err)
      }
    }
  }
}
</script>
