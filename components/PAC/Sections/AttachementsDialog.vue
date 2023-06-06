<template>
  <v-dialog v-model="dialog" fullscreen hide-overlay>
    <template #activator="{on}">
      <v-btn depressed tile icon v-on="on">
        <v-icon>{{ icons.mdiPaperclip }}</v-icon>
      </v-btn>
    </template>
    <v-card>
      <v-card-title>
        <span>Ajouter une annexe à la section: {{ section.titre }}</span>
        <v-spacer />
        <v-btn icon @click="dialog = false">
          <v-icon>{{ icons.mdiClose }}</v-icon>
        </v-btn>
      </v-card-title>
      <v-tabs v-model="ressourcesTab" grow>
        <v-tab>
          Fichiers
        </v-tab>
        <v-tab disabled>
          Data
        </v-tab>
      </v-tabs>
      <v-tabs-items v-model="ressourcesTab">
        <v-tab-item>
          <VFileDropzone class="drop-zone" @change="setFiles">
            <v-card-text>
              <v-row justify="center">
                <v-col v-if="!files.length" cols="3">
                  <v-sheet color="g100" height="182px" class="d-flex align-center justify-center">
                    <v-icon large color="primary">
                      {{ icons.mdiPlus }}
                    </v-icon>
                  </v-sheet>
                </v-col>
                <v-col
                  v-for="(file, i) in files"
                  :key="`${file.name}--${i}`"
                  cols="3"
                >
                  <v-sheet
                    elevation="1"
                    class="pa-2"
                    height="182px"
                  >
                    {{ file.name }}
                  </v-sheet>
                </v-col>
              </v-row>
            </v-card-text>
          </VFileDropzone>
          <v-card-actions>
            <v-spacer />
            <v-btn depressed tile color="primary" :loading="loading" @click="uploadFiles">
              Ajouter
            </v-btn>
            <v-btn depressed tile color="primary" outlined @click="dialog = false">
              Annuler
            </v-btn>
          </v-card-actions>
        </v-tab-item>
        <v-tab-item v-if="isProject">
          <v-card-text>
            <DataSourcesList
              v-if="!loadingData"
              :region="currentRegion"
              :data-sources="dataset"
              :themes="themes"
              selectable
              :selection="selectedDataSources"
              @add="addDatasourceToSection"
              @remove="removeDatasourceToSection"
            />
            <VGlobalLoader v-else />
          </v-card-text>
        </v-tab-item>
      </v-tabs-items>
    </v-card>
  </v-dialog>
</template>

<script>
import { mdiPlus, mdiPaperclip, mdiClose } from '@mdi/js'
import { v4 as uuidv4 } from 'uuid'

export default {
  props: {
    section: {
      type: Object,
      required: true
    },
    gitRef: {
      type: String,
      required: true
    }
  },
  data () {
    return {
      icons: {
        mdiPlus,
        mdiPaperclip,
        mdiClose
      },
      ressourcesTab: 0,
      files: [],
      loading: false,
      dialog: false,
      loadingData: true,
      project: null,
      dataset: null,
      themes: null,
      selectedDataSources: []
    }
  },
  computed: {
    isProject () {
      return !!this.section.project_id
    },
    currentRegion () {
      return this.project.region
    }
  },
  watch: {
    'section.path' () {
      if (this.isProject) {
        this.getSectionDataSources()
      }
    }
  },
  async mounted () {
    // This should be log only once as the edit composant should only be used once.
    // console.log('fetch project data')

    if (this.isProject) {
      const projectId = this.section.project_id

      const { data: projects } = await this.$supabase.from('projects').select('*').eq('id', projectId)
      this.project = projects ? projects[0] : null

      if (this.project) {
        const { dataset, themes } = await this.$daturba.getData(this.currentRegion, this.project.towns.map(t => t.code_commune_INSEE))

        this.dataset = dataset
        this.themes = themes
      }

      this.getSectionDataSources()
    }

    this.loadingData = false
  },
  methods: {
    async getSectionDataSources () {
      const { data: sources } = await this.$supabase.from('sections_data_sources').select('*').match({
        project_id: this.section.project_id,
        section_path: this.section.path
      })

      this.selectedDataSources = sources
    },
    setFiles (files) {
      // console.log('change files', files)
      this.files = files
    },
    async uploadFiles () {
      // console.log(this.files)
      this.loading = true

      if (this.files.length) {
        const { data: sectionsData } = await this.$supabase.from('pac_sections').select('attachements').match({
          path: this.section.path,
          ref: this.gitRef
        })

        const attachements = sectionsData[0] ? sectionsData[0].attachements : []

        for (let fileIndex = 0; fileIndex < this.files.length; fileIndex++) {
          const file = this.files[fileIndex]

          const fileId = uuidv4()

          attachements.push({
            id: fileId,
            name: file.name
          })

          console.log(`${this.gitRef}/${this.section.path}/${fileId}`)

          await this.$supabase.storage
            .from('project-annexes')
            .upload(`${this.gitRef}/${fileId}`, file)
        }

        await this.$supabase.from('pac_sections').upsert({
          path: this.section.path,
          ref: this.gitRef,
          attachements
        })
      }

      this.$emit('upload')

      this.loading = false
      this.dialog = false
    },
    async addDatasourceToSection (source) {
      const sourceUrl = this.$daturba.getCardDataUrl(this.currentRegion, source)

      // console.log('Source url', sourceUrl)
      const { data: savedSource } = await this.$supabase.from('sections_data_sources').insert([{
        project_id: this.section.project_id,
        url: sourceUrl,
        section_path: this.section.path
      }]).select()

      // console.log(savedSource)

      this.selectedDataSources = this.selectedDataSources.concat(savedSource)
    },
    async removeDatasourceToSection (source) {
      const sourceUrl = this.$daturba.getCardDataUrl(this.currentRegion, source)

      this.selectedDataSources = this.selectedDataSources.filter((s) => {
        return s.url !== sourceUrl
      })

      await this.$supabase.from('sections_data_sources').delete().match({
        project_id: this.section.project_id,
        url: sourceUrl,
        section_path: this.section.path
      })
    }
  }
}
</script>

<style scoped>
 .drop-zone {
   cursor: pointer;
 }
</style>
