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
                <v-btn icon @click.stop="editEnabled = true">
                  <v-icon>{{ icons.mdiPencil }}</v-icon>
                </v-btn>
              </v-col>
            </v-row>
          </v-expansion-panel-header>
          <v-expansion-panel-content class="rounded">
            <v-row v-if="editEnabled">
              <v-col cols="12">
                <VTiptap v-if="editEnabled" v-model="sectionMarkdown">
                  <PACSectionsAttachementsDialog
                    :section="section"
                  />
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
                />
              </v-col>
            </v-row>
          </v-expansion-panel-content>
        </v-expansion-panel>
      </v-expansion-panels>
      <v-row v-if="editable && isOpen" align="center" class="my-3 pointer">
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
    </v-card-text>
  </v-card>
</template>

<script>
import axios from 'axios'
import { mdiPlus, mdiPencil } from '@mdi/js'

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
        mdiPencil
      },
      sectionText: '',
      sectionContent: {},
      sectionMarkdown: '',
      editEnabled: false,
      openedSections: []
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
        this.sectionMarkdown = this.$md.parse(this.sectiontext)
      } catch (err) {
        // eslint-disable-next-line no-console
        console.log(err, sectionContent)
      }
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
