<template>
  <v-card flat :color="backgroundColor" class="section-card">
    <v-card-text :class="section.ghost ? 'section-card-text--ghost' : 'section-card-text'">
      <v-expansion-panels flat :value="isOpen ? 0 : null" @change="isOpen = $event === 0">
        <v-hover v-slot="{hover}">
          <v-expansion-panel>
            <v-expansion-panel-header :color="backgroundColor">
              <v-row align="center" dense>
                <v-col v-if="project.id && editable" cols="auto">
                  <v-checkbox
                    v-model="isSelected"
                    :disabled="section.ghost"
                    :color="isVisible ? 'primary' : 'g600'"
                    hide-details
                    class="mt-0"
                    @click.prevent.stop
                    @change="selectionChange"
                  />
                </v-col>
                <v-col cols="" class="p-relative">
                  <v-btn
                    v-if="lastEditDate && editable"
                    absolute
                    text
                    disabled
                    small
                    class="text-caption text-right px-1"
                    :style="{left: '0px', bottom: '-20px'}"
                  >
                    Modifié le: {{ lastEditDate }}
                  </v-btn>
                  <h2 class="d-flex align-center">
                    <span v-if="!editEnabled" :class="section.ghost ? 'section-title--ghost' : 'section-title'">{{ section.name }}</span>
                    <v-text-field
                      v-else
                      v-model="sectionName"
                      dense
                      filled
                      hide-details
                      @click.stop
                    />
                    <PACEditingParentDiffDialog v-if="section.diff && isEditable" :section="section" :git-ref="gitRef">
                      <template #default="{on}">
                        <v-chip
                          label
                          color="bf200"
                          text-color="primary lighten-2"
                          class="ml-2"
                          v-on="on"
                        >
                          {{ section.diff.label }}
                        </v-chip>
                      </template>
                    </PACEditingParentDiffDialog>
                    <v-badge v-if="section.diffCount && isEditable" color="primary" class="ml-2" inline :content="section.diffCount" />
                    <v-badge v-if="ghostCount && editable" color="" class="ghost-count-badge ml-2" inline :content="ghostCount" />
                    <v-tooltip v-if="section.isDuplicated" top max-width="300px">
                      <template #activator="{on}">
                        <v-chip
                          label
                          color="bf200"
                          text-color="primary lighten-2"
                          class="ml-2"
                          v-on="on"
                        >
                          Doublon
                        </v-chip>
                      </template>
                      Cette section est en double. N'hésitez pas à corriger le doublon en supprimant une des deux sections pour éviter des confusions ou des pertes de données. Notre conseil : conserver la section qui comporte des éléments pré-rédigés.
                    </v-tooltip>
                  </h2>
                </v-col>
                <v-col v-if="(isOpen || hover) && !editable" cols="auto">
                  <v-tooltip bottom>
                    <template #activator="{on}">
                      <v-btn icon small v-on="on" @click.stop="copyLinkToClipboard">
                        <v-icon>{{ icons.mdiLinkVariant }}</v-icon>
                      </v-btn>
                    </template>
                    Copier le lien vers la section
                  </v-tooltip>
                </v-col>
                <v-col v-if="(isOpen || hover) && editable && !section.ghost" cols="auto">
                  <v-tooltip bottom>
                    <template #activator="{on}">
                      <v-btn icon small v-on="on" @click.stop="$emit('changeOrder', section, -1)">
                        <v-icon>{{ icons.mdiArrowUp }}</v-icon>
                      </v-btn>
                    </template>
                    Changer l'ordre
                  </v-tooltip>
                  <v-tooltip bottom>
                    <template #activator="{on}">
                      <v-btn icon small v-on="on" @click.stop="$emit('changeOrder', section, 1)">
                        <v-icon>{{ icons.mdiArrowDown }}</v-icon>
                      </v-btn>
                    </template>
                    Changer l'ordre
                  </v-tooltip>
                </v-col>
                <v-col v-if="(isOpen || hover || editEnabled) && isEditable" cols="auto" class="ml-4">
                  <v-tooltip v-if="!editEnabled" bottom>
                    <template #activator="{on}">
                      <v-btn icon small v-on="on" @click.stop="editEnabled = true; isOpen = true">
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
                <v-col v-if="section.ghost" cols="auto">
                  <v-tooltip bottom>
                    <template #activator="{on}">
                      <v-btn icon small :loading="saving" v-on="on" @click.stop="copyGhostSection">
                        <v-icon color="primary lighten-2">
                          {{ icons.mdiPlus }}
                        </v-icon>
                      </v-btn>
                    </template>
                    Ajouter la section
                  </v-tooltip>
                </v-col>
              </v-row>
            </v-expansion-panel-header>
            <v-expansion-panel-content class="rounded">
              <v-row v-if="editEnabled">
                <v-col :cols="(diff.visible && diff.body) ? 6 : 12">
                  <VTiptap v-if="editEnabled" v-model="sectionMarkdown" class="mt-6">
                    <PACSectionsFileAttachmentsDialog
                      :section="section"
                      :git-ref="gitRef"
                    />
                    <PACSectionsDataAttachmentsDialog
                      v-if="project.id"
                      v-model="dataAttachments"
                      :section="section"
                      :project="project"
                      :git-ref="gitRef"
                    />
                    <v-tooltip bottom>
                      <template #activator="{on}">
                        <v-btn icon tile :disabled="!section.inParentProject" v-on="on" @click="toggleDiff">
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
                <v-col cols="12" :style="{position: 'relative'}">
                  <PACEditingReadOnlyCard v-if="!section.ghost && editable && !isEditable" :section="section" :git-ref="gitRef" class="mt-4" />
                  <nuxt-content class="pac-section-content mt-4" :document="sectionContent" />
                </v-col>
              </v-row>
              <v-row>
                <v-col class="d-flex flex-column" :style="{ gap: '0.5rem' }">
                  <PACSectionsFileAttachmentsChips
                    :section="section"
                    :git-ref="gitRef"
                    :project="project"
                    :editable="editable"
                  />
                  <PACSectionsDataAttachmentsCards
                    v-model="dataAttachments"
                    :section="section"
                    :git-ref="gitRef"
                  />
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
                    :git-ref="section.ghost ? headRef : gitRef"
                    :project="project"
                    :editable="editable && !section.ghost"
                    :deletable="editable && !section.ghost"
                    :parent-selected="isVisible"
                    :opened-path="openedPath"
                    v-on="{ ...$listeners, removed: sectionRemoved }"
                  />
                </v-col>
              </v-row>
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-hover>
      </v-expansion-panels>
      <PACEditingGitAddSectionDialog
        v-if="editable && isOpen && !section.ghost"
        :parent="section"
        :git-ref="gitRef"
        @added="sectionAdded"
        @introCreated="updateSectionType"
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
  mdiArrowDown, mdiArrowUp,
  mdiLinkVariant
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
    },
    openedPath: {
      type: String,
      default: null
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
        mdiFileCompare,
        mdiArrowDown,
        mdiArrowUp,
        mdiLinkVariant
      },
      deleteDialog: false,
      isSelected: selectedPaths.includes(this.section.path),
      sectionName: this.section.name,
      sectionText: '',
      // sectionContent: { body: null },
      sectionMarkdown: '',
      editEnabled: false,
      isOpen: false,
      saving: false,
      errorSaving: false,
      errorDiff: false,
      diff: { body: null, visible: false, label: `Trame ${this.project?.id ? 'départementale' : 'régionale'}` },
      dataAttachments: []
    }
  },
  computed: {
    headRef () {
      let headRef = 'main'

      if (this.project && this.project.id) {
        headRef = `dept-${this.$options.filters.deptToRef(this.project.trame)}`
      }

      if (this.gitRef.includes('dept-')) {
        const dept = this.gitRef.replace('dept-', '')
        // eslint-disable-next-line eqeqeq
        const region = departements.find(d => d.code_departement == dept).code_region
        headRef = `region-${region}`
      }

      return headRef
    },
    isVisible () {
      return this.isSelected && this.parentSelected
    },
    backgroundColor () {
      if (this.section.ghost) {
        return 'primary lighten-4'
      }

      if (this.project.id && (!this.isSelected || !this.parentSelected)) {
        return 'g300'
      }

      return this.isOpen ? 'primary lighten-4' : 'white'
    },
    sectionContent () {
      const body = this.$md.compile(this.sectionMarkdown)

      return {
        body
      }
    },
    isEditable () {
      if (this.gitRef === 'main') {
        return this.editable
      } else {
        return this.editable && !cadreJuridique.includes(this.section.path) && !this.section.ghost
      }
    },
    lastEditDate () {
      if (this.section.editDate) {
        return this.$dayjs(this.section.editDate).format('DD MMM YYYY')
      } else {
        return ''
      }
    },
    ghostCount () {
      if (this.section.ghost) { return 0 }

      let count = 0

      function countGhostChildren (children) {
        for (const child of children) {
          if (child.ghost) {
            ++count
          } else if (child.children?.length) {
            countGhostChildren(child.children)
          }
        }
      }

      countGhostChildren(this.section.children)

      return count
    }
  },
  watch: {
    editEnabled () {
      this.$emit('edited', this.section.path, this.editEnabled)
    },
    isOpen () {
      if (this.isOpen) {
        this.$analytics({
          category: 'pac',
          name: 'open section',
          value: this.section.name,
          data: this.section
        })

        if (!this.section.ghost && this.editable && this.section.children[0] && !this.section.children[0].editDate) {
          this.fetchChildrenHistories()
        }
      }
    },
    isSelected () {
      this.$analytics({
        category: 'pac',
        name: `${this.isSelected ? 'select' : 'unselect'} section`,
        value: this.section.name,
        data: this.section
      })
    },
    openedPath: {
      handler (path) {
        if (path && path.startsWith(this.section.path)) {
          this.isOpen = true

          if (this.openedPath && this.openedPath === this.section.path && this.$el) {
            this.$el.scrollIntoView({ behavior: 'smooth' })
            this.$emit('opened')
          }
        }
      },
      immediate: true
    }
  },
  async mounted () {
    await Promise.all([
      this.fetchSectionContent(),
      this.fetchDataAttachments()
    ])

    if (this.openedPath && this.openedPath === this.section.path) {
      this.$el.scrollIntoView({ behavior: 'smooth' })
      this.$emit('opened')
    }
  },
  methods: {
    async fetchSectionContent () {
      const path = `${this.section.path}${this.section.type === 'dir' ? '/intro.md' : ''}`

      const { data: sectionContent } = await axios({
        method: 'get',
        url: '/api/trames/file',
        params: {
          path,
          ref: this.section.ghost ? this.headRef : this.gitRef
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
    },
    async fetchChildrenHistories () {
      const { data: histories } = await axios.get(`/api/trames/tree/${this.gitRef}/history`, {
        params: {
          paths: this.section.children
            .filter(child => !child.ghost)
            .map(child => child.type === 'file' ? child.path : (child.path + '/intro.md'))
        }
      })

      // eslint-disable-next-line vue/no-mutating-props
      this.section.children = this.section.children.map((child) => {
        return {
          ...child,
          editDate: histories.find(h => h.path.replace('/intro.md', '') === child.path)?.commit?.date
        }
      })
    },
    async fetchDataAttachments () {
      const { data } = await this.$supabase.from('pac_sections_data').select('*').match({
        path: this.section.path,
        ref: this.gitRef
      })
      this.dataAttachments = data
    },
    async updateName () {
      const { path, type, name } = this.section

      await axios({
        method: 'post',
        url: `/api/trames/tree/${this.gitRef}`,
        data: {
          section: { path, type, name },
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

        await this.updateName()
      }

      try {
        // console.log('is path updated ?', filePath)
        const { data: { data: { content: savedFile } } } = await axios({
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

        if (this.section.type === 'dir') {
          // eslint-disable-next-line vue/no-mutating-props
          this.section.introSha = savedFile.sha
        } else {
          // eslint-disable-next-line vue/no-mutating-props
          this.section.sha = savedFile.sha
        }

        const { data: history } = await axios.get(`/api/trames/tree/${this.gitRef}/history`, {
          params: {
            paths: [this.section.type === 'file' ? this.section.path : (this.section.path + '/intro.md')]
          }
        })

        // eslint-disable-next-line vue/no-mutating-props
        this.section.editDate = history[0]?.commit?.date

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

      this.$analytics({
        category: 'pac',
        name: 'update section',
        value: this.section.name
      })

      this.saving = false
    },
    async copyGhostSection () {
      this.saving = true

      await axios({
        method: 'put',
        url: `/api/trames/${this.gitRef}/copy`,
        data: {
          ghostRef: this.headRef,
          path: this.section.path
        }
      })

      // eslint-disable-next-line vue/no-mutating-props
      this.section.ghost = false
      this.saving = false

      this.$emit('changeOrder', this.section, 0)
    },
    updateSectionType (introFile) {
      if (this.section.type === 'file') {
        // eslint-disable-next-line vue/no-mutating-props
        this.section.type = 'dir'
        // eslint-disable-next-line vue/no-mutating-props
        this.section.path = this.section.path.replace('.md', '')
        // eslint-disable-next-line vue/no-mutating-props
        this.section.introSha = introFile.sha
      }
    },
    sectionAdded (newSection) {
      // This could probably go into parent with an event. But it's not a big issue to have it here.
      // A Section card could also use a computed based on children length to determine if it's a dir or a file and adapt its path accordingly.
      // eslint-disable-next-line vue/no-mutating-props
      this.section.children.push(newSection)

      this.$analytics({
        category: 'pac',
        name: 'add section',
        value: newSection.name,
        data: newSection
      })
    },
    async sectionRemoved (section) {
      const duplicated = this.section.children.find(c => c.name === section.name)
      if (duplicated) { duplicated.isDuplicated = false }

      // eslint-disable-next-line vue/no-mutating-props
      this.section.children = this.section.children.filter((c) => {
        return c.path !== section.path
      })

      const { data } = await axios.get(`/api/trames/tree/${this.headRef}`, {
        params: {
          path: this.section.path // parent section path
        }
      })

      const ghostSection = data.find(s => s.name === section.name)
      if (ghostSection) {
        ghostSection.ghost = true
        // eslint-disable-next-line vue/no-mutating-props
        this.section.children.push(ghostSection)
      }
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
    },
    copyLinkToClipboard () {
      const { href } = this.$router.resolve({ ...this.$route, query: { ...this.$route.query, path: this.section.path } })
      navigator.clipboard.writeText(location.origin + href)
    }
  }
}
</script>

<style scoped>
.section-card {
  scroll-margin-top: 150px;
}

.section-card-text {
  border: 1px solid var(--v-primary-lighten1);
  border-color: var(--v-primary-lighten1) !important;
}

.section-card-text--ghost {
  background-color: var(--v-primary-lighten4);
  border: 1px dashed #1765c9 !important;
}

.section-title {
  font-size: 20px;
}

.section-title--ghost {
  font-size: 20px;
  opacity: 0.5;
}
</style>

<style>
.pac-section-content img {
  max-width: 100%;
}

.pac-section-content p:empty:before {
  content: ' ';
  white-space: pre;
}

.pac-section-content h1, .pac-section-content h2, .pac-section-content h3, .pac-section-content h4, .pac-section-content p {
  margin-bottom: 14px;
}

.ghost-count-badge .v-badge__badge {
  background-color: var(--v-primary-lighten4);
  border: 1px dashed #1765c9 !important;
  color: #1765c9 !important;
  display: inline-flex;
  align-items: center;
}

.v-item-group.v-expansion-panels, .v-item-group.v-expansion-panels .v-expansion-panel, .v-item-group.v-expansion-panels .v-expansion-panel-header, .v-item-group.v-expansion-panels .v-expansion-panel-content {
  transition: none !important;
}
</style>
