<template>
  <div class="mt-4">
    <div v-for="(section, i) in sortedSections" :key="i">
      <template v-if="(section.children && section.children.length) || section.slug === 'intro'">
        <nuxt-content :document="section" />
        <PACSectionsAttachementsChips v-if="files[section.path]" small :files="files[section.path]" />
        <PACContentSection v-if="section.children && section.children.length" :sections="section.children" :editable="editable" />
      </template>
      <template v-else>
        <v-expansion-panels :id="`panel__${section.path.replaceAll(/[^A-Za-z0-9]/g, '__')}`" flat>
          <v-expansion-panel>
            <v-hover v-slot="{hover}">
              <v-expansion-panel-header>
                <v-row align="center">
                  <v-col cols="auto">
                    {{ section.titre }}
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
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>
      </template>
    </div>
  </div>
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
    }
  },
  data () {
    const filesMap = {}

    this.sections.forEach((section) => {
      filesMap[section.path] = []
    })

    return {
      icons: { mdiCommentOutline },
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
    fetchAttachements () {
      const folders = [
        this.project.town.code_departement,
        this.prjectId
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
        .list(`/${folder}${section.path}`, {
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
            .createSignedUrl(`/${folder}${section.path}/${file.name}`, 60 * 60)

          file.url = data.signedURL
          this.files[section.path].push(file)
        }
      }
    }
  }
}
</script>
