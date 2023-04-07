<template>
  <v-card flat :color="isOpen ? 'primary lighten-4' : 'white'">
    <v-card-text class="section-card">
      <v-expansion-panels v-model="openedSections" multiple flat>
        <v-expansion-panel>
          <v-expansion-panel-header :color="isOpen ? 'primary lighten-4' : 'white'">
            <v-row dense>
              <v-col cols="">
                <h2 class="section-title">
                  {{ section.name }}
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
              <v-col cols="12">
                <VTiptap v-if="editEnabled" v-model="sectionMarkdown" class="mt-6">
                  <!-- <PACSectionsAttachementsDialog
                    :section="section"
                  /> -->
                </VTiptap>
              </v-col>
            </v-row>
            <v-row v-else>
              <v-col cols="12">
                <nuxt-content class="pac-section-content mt-4" :document="sectionContent" />
              </v-col>
            </v-row>
            <v-row v-if="section.children">
              <v-col
                v-for="child in section.children"
                :key="child.path"
                cols="12"
              >
                <PACSectionCard
                  :section="child"
                  :git-ref="gitRef"
                  :editable="editable"
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
  </v-card>
</template>

<script>
import axios from 'axios'
import { mdiPlus, mdiPencil, mdiContentSave, mdiClose } from '@mdi/js'
import { encode } from 'js-base64'

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
    }
  },
  data () {
    return {
      icons: {
        mdiPlus,
        mdiPencil,
        mdiContentSave,
        mdiClose
      },
      projectId: this.gitRef.includes('projet-') ? this.gitRef.replace('projet-', '') : null,
      sectionText: '',
      sectionContent: {},
      sectionMarkdown: '',
      editEnabled: false,
      openedSections: [],
      saving: false,
      errorSaving: false
    }
  },
  computed: {
    isOpen () {
      return this.openedSections.length
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

        if (this.projectId) {
          this.$notifications.notifyUpdate(this.projectId)
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
    cancelEditing () {
      this.sectionMarkdown = this.$md.parse(this.sectionText)
      this.editEnabled = false
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
