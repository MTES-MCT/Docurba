<template>
  <v-card flat outlined color="primary lighten-1">
    <v-card-text>
      <v-expansion-panels flat>
        <v-expansion-panel>
          <v-expansion-panel-header>
            {{ section.name }}
          </v-expansion-panel-header>
          <v-expansion-panel-content>
            <v-row>
              <v-col cols="12">
                <VTiptap v-if="editEnabled" v-model="editedSection.text" :readonly="isReadonly">
                  <PACSectionsAttachementsDialog
                    :section="section"
                  />
                </VTiptap>
                <nuxt-content v-else class="pac-section-content" :document="sectionContent" />
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
    </v-card-text>
  </v-card>
</template>

<script>
import axios from 'axios'

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
      sectionText: '',
      sectionContent: {},
      sectionMarkdown: '',
      editEnabled: false
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

      this.sectionText = sectionContent.replace(/---([\s\S]*)---/, '')
      this.sectionContent.body = this.$md.compile(this.sectionText)
      this.sectionMarkdown = this.$md.parse(this.sectiontext)
    }
  }
}
</script>
