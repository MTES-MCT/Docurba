<template>
  <v-card flat :color="backgroundColor">
    <v-card-text class="section-card">
      <v-expansion-panels v-model="openedSections" multiple flat>
        <v-hover v-slot="{hover}">
          <v-expansion-panel>
            <v-expansion-panel-header :color="backgroundColor">
              <v-row align="center" dense>
                <v-col v-if="project.id && editable" cols="auto">
                  <v-checkbox
                    v-model="isSelected"
                    :color="isVisible ? 'primary' : 'g600'"
                    hide-details
                    class="mt-0"
                    @click.prevent.stop
                    @change="selectionChange"
                  />
                </v-col>
                <v-col cols="">
                  <h2 class="section-title d-flex align-center">
                    <span v-if="!editEnabled">{{ section.name }}</span>
                    <v-text-field
                      v-else
                      v-model="sectionName"
                      dense
                      filled
                      hide-details
                      @click.stop
                    />
                    <v-chip
                      v-if="section.diff && isEditable"
                      label
                      color="bf200"
                      text-color="primary lighten-2"
                      class="ml-2"
                    >
                      {{ section.diff.label }}
                    </v-chip>
                    <v-badge v-if="section.diffCount" color="primary" inline :content="section.diffCount" />
                  </h2>
                  <!-- <span v-show="lastEditDate" class="text-caption">Modifié le: {{ lastEditDate }}</span> -->
                </v-col>
                <v-col v-if="(isOpen || hover) && editable" cols="auto">
                  <v-tooltip bottom>
                    <template #activator="{on}">
                      <v-btn icon small v-on="on" @click.stop="$emit('changeOrder', section.path, -1)">
                        <v-icon>{{ icons.mdiArrowUp }}</v-icon>
                      </v-btn>
                    </template>
                    Changer l'ordre
                  </v-tooltip>
                  <v-tooltip bottom>
                    <template #activator="{on}">
                      <v-btn icon small v-on="on" @click.stop="$emit('changeOrder', section.path, 1)">
                        <v-icon>{{ icons.mdiArrowDown }}</v-icon>
                      </v-btn>
                    </template>
                    Changer l'ordre
                  </v-tooltip>
                </v-col>
                <v-col v-if="(isOpen || hover || editEnabled) && isEditable" cols="auto" class="ml-4">
                  <v-tooltip v-if="!editEnabled" bottom>
                    <template #activator="{on}">
                      <v-btn icon small v-on="on" @click.stop="editEnabled = true; openedSections = [0]">
                        <v-icon color="primary lighten-2">
                          {{ icons.mdiPencil }}
                        </v-icon>
                      </v-btn>
                    </template>
                    Editer la section
                  </v-tooltip>
                  <template v-else>
                    <PACEditingCancelDialog :section="section" @cancel="cancelEditing" />
                    <v-tooltip bottom>
                      <template #activator="{on}">
                        <v-btn icon small :loading="saving" v-on="on" @click.stop="saveSection">
                          <v-icon color="primary lighten-2">
                            {{ icons.mdiContentSave }}
                          </v-icon>
                        </v-btn>
                      </template>
                      Enregistrer
                    </v-tooltip>
                  </template>
                </v-col>
                <v-col v-if="(isOpen || hover || editEnabled || deleteDialog) && isEditable && deletable" cols="auto">
                  <PACEditingGitRemoveSectionDialog
                    v-model="deleteDialog"
                    show-activator
                    :section="section"
                    :git-ref="gitRef"
                    v-on="$listeners"
                  />
                </v-col>
              </v-row>
            </v-expansion-panel-header>
            <v-expansion-panel-content class="rounded">
              <v-row v-if="editEnabled">
                <v-col :cols="(diff.visible && diff.body) ? 6 : 12">
                  <VTiptap v-if="editEnabled" v-model="sectionMarkdown" class="mt-6">
                    <PACSectionsAttachementsDialog
                      :section="section"
                      :git-ref="gitRef"
                    />
                    <v-tooltip bottom>
                      <template #activator="{on}">
                        <v-btn icon tile v-on="on" @click="toggleDiff">
                          <v-icon>{{ icons.mdiFileCompare }}</v-icon>
                        </v-btn>
                      </template>
                      Comparer à la {{ diff.label }}
                    </v-tooltip>
                  </VTiptap>
                </v-col>
                <v-col v-if="diff.visible && diff.body" cols="6">
                  <PACEditingDiffCard class="mt-6" :diff="diff" :label="diff.label" />
                </v-col>
              </v-row>
              <v-row v-else>
                <v-col cols="12">
                  <PACEditingReadOnlyCard v-if="editable && !isEditable" :section="section" class="mt-4" />
                  <nuxt-content class="pac-section-content mt-4" :document="sectionContent" />
                </v-col>
              </v-row>
              <PACSectionsAttachementsChips
                :section="section"
                :git-ref="gitRef"
                :project="project"
                :editable="editable"
              />
              <v-row v-if="section.children && section.children.length">
                <v-col
                  v-for="child in section.children"
                  :key="child.url"
                  cols="12"
                >
                  <PACSectionCard
                    :section="child"
                    :git-ref="gitRef"
                    :project="project"
                    :editable="editable"
                    :deletable="editable"
                    :parent-selected="isVisible"
                    v-on="$listeners"
                    @removed="sectionRemoved"
                  />
                </v-col>
              </v-row>
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-hover>
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
            <v-col cols="auto" class="text-center">
              <span><v-icon>{{ icons.mdiPlus }}</v-icon> Ajouter une sous-section dans <br> <b>{{ section.name }}</b> </span>
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
import {
  mdiPlus, mdiPencil, mdiContentSave,
  mdiClose, mdiFileCompare,
  mdiArrowDown, mdiArrowUp
} from '@mdi/js'
import { encode } from 'js-base64'
import departements from '@/assets/data/departements-france.json'

import cadreJuridique from '@/assets/data/CadreJuridique.json'

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
    deletable: {
      type: Boolean,
      default: false
    },
    project: {
      type: Object,
      default () { return {} }
    },
    parentSelected: {
      type: Boolean,
      default: true
    }
  },
  data () {
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

    const selectedPaths = this.project.PAC || []
    // const sectionPath = this.section.type === 'dir' ? `${this.section.path}/intro.md` : this.section.path

    return {
      icons: {
        mdiPlus,
        mdiPencil,
        mdiContentSave,
        mdiClose,
        mdiFileCompare,
        mdiArrowDown,
        mdiArrowUp
      },
      deleteDialog: false,
      isSelected: selectedPaths.includes(this.section.path),
      sectionName: this.section.name,
      sectionText: '',
      // sectionContent: { body: null },
      sectionMarkdown: '',
      sectionHistory: null,
      editEnabled: false,
      openedSections: [],
      saving: false,
      errorSaving: false,
      errorDiff: false,
      headRef,
      diff: { body: null, visible: false, label: `Trame ${headRef.includes('dept-') ? 'départementale' : 'régionale'}` }
    }
  },
  computed: {
    isOpen () {
      return this.openedSections.length
    },
    isVisible () {
      return this.isSelected && this.parentSelected
    },
    backgroundColor () {
      if (this.project.id && (!this.isSelected || !this.parentSelected)) {
        return 'g300'
      }

      return this.isOpen ? 'primary lighten-4' : 'white'
    },
    sectionContent () {
      return {
        body: this.$md.compile(this.sectionMarkdown)
      }
    },
    isEditable () {
      if (this.gitRef === 'main') {
        return this.editable
      } else {
        return this.editable && !cadreJuridique.includes(this.section.path)
      }
    },
    lastEditDate () {
      if (this.sectionHistory) {
        return this.$dayjs(this.sectionHistory.commit.author.date).format('DD MMM YYYY')
      } else {
        return ''
      }
    }
  },
  watch: {
    editEnabled () {
      this.$emit('edited', this.section.path, this.editEnabled)
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
        // this.sectionContent.body = this.$md.compile(this.sectionText)
        this.sectionMarkdown = this.$md.parse(this.sectionText)
      } catch (err) {
        // eslint-disable-next-line no-console
        console.log(err, sectionContent)
      }

      if (this.editable) {
        const { data: sectionHistory } = await axios({
          method: 'get',
          url: '/api/trames/history',
          params: {
            path,
            ref: this.gitRef
          }
        })

        this.sectionHistory = sectionHistory
      }
    },
    async updateName () {
      await axios({
        method: 'post',
        url: `/api/trames/tree/${this.gitRef}`,
        data: {
          section: this.section,
          newName: this.sectionName
        }
      })

      this.$emit('changeTree', this.section, this.sectionName)
    },
    async saveSection () {
      this.saving = true
      let filePath = this.section.type === 'dir' ? `${this.section.path}/intro.md` : this.section.path

      if (this.section.name !== this.sectionName) {
        const nameIndex = filePath.lastIndexOf(this.section.name)
        filePath = `${filePath.substring(0, nameIndex)}${this.sectionName}${this.section.type === 'file' ? '.md' : ''}`

        await this.updateName() // This should emit a 'changeTree' event that shoud update section.path in props.
      }

      try {
        // console.log('is path updated ?', filePath)

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

        // this.sectionContent.body = this.$md.compile(this.sectionMarkdown)
        this.sectionText = this.sectionMarkdown
        this.editEnabled = false
      } catch (err) {
        // eslint-disable-next-line no-console
        console.log('Error saving data', err)

        this.errorSaving = true
      }

      this.saving = false
    },
    sectionAdded (newSection) {
      // This could probably go into parent with an event. But it's not a big issue to have it here.
      // A Section card could also use a computed based on children length to determine if it's a dir or a file and adapt its path accordingly.
      // eslint-disable-next-line vue/no-mutating-props
      this.section.children.push(newSection)
      if (this.section.type === 'file') {
        // eslint-disable-next-line vue/no-mutating-props
        this.section.type = 'dir'
        // eslint-disable-next-line vue/no-mutating-props
        this.section.path = this.section.path.replace('.md', '')
      }
    },
    sectionRemoved (section) {
      // eslint-disable-next-line vue/no-mutating-props
      this.section.children = this.section.children.filter((c) => {
        return c.path !== section.path
      })
    },
    selectionChange () {
      this.$emit('selectionChange', {
        path: this.section.path,
        selected: this.isSelected
      })
    },
    cancelEditing () {
      this.sectionMarkdown = this.$md.parse(this.sectionText)
      this.editEnabled = false
    },
    async fetchDiff () {
      try {
        const { data: diffSectionContent } = await axios({
          method: 'get',
          url: '/api/trames/file',
          params: {
            path: this.section.type === 'dir' ? `${this.section.path}/intro.md` : this.section.path,
            ref: this.headRef
          }
        })

        console.log('diffSectionContent', diffSectionContent)

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
