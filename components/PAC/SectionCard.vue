<template>
  <v-card flat :color="backgroundColor">
    <v-card-text class="section-card">
      <v-expansion-panels v-model="openedSections" multiple flat>
        <v-expansion-panel>
          <v-expansion-panel-header :color="backgroundColor">
            <v-row align="center" dense>
              <v-col v-if="project.id && editable" cols="auto">
                <v-checkbox
                  v-model="isSelected"
                  color="primary"
                  hide-details
                  class="mt-0"
                  @click.prevent.stop
                  @change="selectionChange"
                />
              </v-col>
              <v-col cols="">
                <h2 class="section-title d-flex align-center">
                  {{ section.name }}
                  <v-chip
                    v-if="section.diff && editable"
                    label
                    color="bf200"
                    text-color="primary lighten-2"
                    class="ml-2"
                  >
                    {{ section.diff.label }}
                  </v-chip>
                </h2>
              </v-col>
              <v-col v-if="isOpen && editable" cols="auto">
                <v-btn v-if="!editEnabled" icon @click.stop="editEnabled = true">
                  <v-icon>{{ icons.mdiPencil }}</v-icon>
                </v-btn>
                <template v-else>
                  <PACEditingCancelDialog :section="section" @cancel="cancelEditing" />
                  <v-btn icon :loading="saving" @click.stop="saveSection">
                    <v-icon>{{ icons.mdiContentSave }}</v-icon>
                  </v-btn>
                </template>
              </v-col>
            </v-row>
          </v-expansion-panel-header>
          <v-expansion-panel-content class="rounded">
            <v-row v-if="editEnabled">
              <v-col :cols="(diff.visible && diff.body) ? 6 : 12">
                <VTiptap v-if="editEnabled" v-model="sectionMarkdown" class="mt-6">
                  <!-- <PACSectionsAttachementsDialog
                    :section="section"
                  /> -->
                  <v-btn icon tile @click="toggleDiff">
                    <v-icon>{{ icons.mdiFileCompare }}</v-icon>
                  </v-btn>
                </VTiptap>
              </v-col>
              <v-col v-if="diff.visible && diff.body" cols="6">
                <PACEditingDiffCard class="mt-6" :diff="diff" :label="'Trame departementale'" />
              </v-col>
            </v-row>
            <v-row v-else>
              <v-col cols="12">
                <nuxt-content class="pac-section-content mt-4" :document="sectionContent" />
              </v-col>
            </v-row>
            <v-row v-if="section.children && section.children.length">
              <v-col
                v-for="child in section.children"
                :key="child.path"
                cols="12"
              >
                <PACSectionCard
                  :section="child"
                  :git-ref="gitRef"
                  :project="project"
                  :editable="editable"
                  @selectionChange="dispatchSelectionChange"
                />
              </v-col>
            </v-row>
          </v-expansion-panel-content>
        </v-expansion-panel>
      </v-expansion-panels>
      <PACEditingGitAddSectionDialog
        v-if="editable && isOpen"
        :parent="section"
        :git-ref="gitRef"
        @added="sectionAdded"
      >
        <template #activator="{on}">
          <v-row align="center" class="my-3 pointer" v-on="on">
            <v-col cols="">
              <v-divider />
            </v-col>
            <v-col cols="auto">
              <span><v-icon>{{ icons.mdiPlus }}</v-icon> Ajouter une sous-section </span>
            </v-col>
            <v-col cols="">
              <v-divider />
            </v-col>
          </v-row>
        </template>
      </PACEditingGitAddSectionDialog>
    </v-card-text>
    <v-snackbar v-model="errorSaving" top :timeout="-1" color="error">
      Une erreur s'est produite, vos modifications sur "{{ section.name }}" ne sont pas sauvegardées.
      <template #action>
        <v-btn icon @click="errorSaving = false">
          <v-icon>{{ icons.mdiClose }}</v-icon>
        </v-btn>
      </template>
    </v-snackbar>
    <v-snackbar v-model="errorDiff" top :timeout="4000" color="error">
      La section {{ section.name }} n'est pas trouvable au niveau {{ diff.label }}.
      <template #action>
        <v-btn icon @click="errorDiff = false">
          <v-icon>{{ icons.mdiClose }}</v-icon>
        </v-btn>
      </template>
    </v-snackbar>
  </v-card>
</template>

<script>

import axios from 'axios'
import { mdiPlus, mdiPencil, mdiContentSave, mdiClose, mdiFileCompare } from '@mdi/js'
import { encode } from 'js-base64'
import departements from '@/assets/data/departements-france.json'

export default {
  props: {
    section: {
      type: Object,
      required: true
    },
    gitRef: {
      type: String,
      required: true
    },
    editable: {
      type: Boolean,
      default: false
    },
    project: {
      type: Object,
      default () { return {} }
    }
  },
  data () {
    const selectedPaths = this.project.PAC || []
    // const sectionPath = this.section.type === 'dir' ? `${this.section.path}/intro.md` : this.section.path

    return {
      icons: {
        mdiPlus,
        mdiPencil,
        mdiContentSave,
        mdiClose,
        mdiFileCompare
      },
      isSelected: selectedPaths.includes(this.section.path),
      sectionText: '',
      sectionContent: { body: null },
      sectionMarkdown: '',
      editEnabled: false,
      openedSections: [],
      saving: false,
      errorSaving: false,
      errorDiff: false,
      diff: { body: null, visible: false, label: '' }
    }
  },
  computed: {
    isOpen () {
      return this.openedSections.length
    },
    backgroundColor () {
      if (this.project.id && !this.isSelected) {
        return 'g300'
      }

      return this.isOpen ? 'primary lighten-4' : 'white'
    }
  },
  mounted () {
    this.fetchSectionContent()
  },
  methods: {
    async fetchSectionContent () {
      const path = `/${this.section.path}${this.section.type === 'dir' ? '/intro.md' : ''}`

      const { data: sectionContent } = await axios({
        method: 'get',
        url: '/api/trames/file',
        params: {
          path,
          ref: this.gitRef
        }
      })

      // console.log(sectionContent)
      try {
        this.sectionText = sectionContent.replace(/---([\s\S]*)---/, '')
        this.sectionContent.body = this.$md.compile(this.sectionText)
        this.sectionMarkdown = this.$md.parse(this.sectionText)
      } catch (err) {
        // eslint-disable-next-line no-console
        console.log(err, sectionContent)
      }
    },
    async saveSection () {
      this.saving = true

      try {
        const filePath = this.section.type === 'dir' ? `${this.section.path}/intro.md` : this.section.path

        await axios({
          method: 'post',
          url: `/api/trames/${this.gitRef}`,
          data: {
            userId: this.$user.id,
            commit: {
              path: filePath,
              content: encode(this.sectionMarkdown),
              sha: this.section.type === 'dir' ? this.section.introSha : this.section.sha
            }
          }
        })

        if (this.project && this.project.id) {
          this.$notifications.notifyUpdate(this.project.id)
        }

        this.sectionContent.body = this.$md.compile(this.sectionMarkdown)
        this.editEnabled = false
      } catch (err) {
        // eslint-disable-next-line no-console
        console.log('Error saving data', err)

        this.errorSaving = true
      }

      this.saving = false
    },
    sectionAdded (newSection) {
      // eslint-disable-next-line vue/no-mutating-props
      this.section.children.push(newSection)
    },
    selectionChange () {
      this.$emit('selectionChange', {
        path: this.section.path,
        selected: this.isSelected
      })
    },
    dispatchSelectionChange (selection) {
      this.$emit('selectionChange', selection)
    },
    cancelEditing () {
      this.sectionMarkdown = this.$md.parse(this.sectionText)
      this.editEnabled = false
    },
    async fetchDiff () {
      let headRef = 'main'

      if (this.project && this.project.id) {
        headRef = `dept-${this.project.towns ? this.project.towns[0].code_departement : ''}`
      }

      if (this.gitRef.includes('dept-')) {
        const dept = this.gitRef.replace('dept-', '')
        // eslint-disable-next-line eqeqeq
        const region = departements.find(d => d.code_departement == dept).code_region
        headRef = `region-${region}`
      }

      this.diff.label = `Trame ${headRef.includes('dept-') ? 'départementale' : 'régionale'}`

      try {
        const { data: diffSectionContent } = await axios({
          method: 'get',
          url: '/api/trames/file',
          params: {
            path: this.section.type === 'dir' ? `${this.section.path}/intro.md` : this.section.path,
            ref: headRef
          }
        })

        this.diff.body = this.$md.compile(diffSectionContent.replace(/---([\s\S]*)---/, ''))
      } catch (err) {
        this.diff.body = null
        this.errorDiff = true
      }
    },
    async toggleDiff () {
      if (!this.diff.body) {
        await this.fetchDiff()
      }

      this.diff.visible = !this.diff.visible
    }
  }
}
</script>

<style scoped>
.section-card {
  border: 1px solid #E3E3FD;
  border-color: #E3E3FD !important;
}

.section-title {
  font-size: 20px;
}
</style>
