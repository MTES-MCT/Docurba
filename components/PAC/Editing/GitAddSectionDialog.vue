<template>
  <v-dialog v-model="dialog" width="500">
    <template #activator="{on}">
      <slot name="activator" :on="on">
        <v-btn
          v-show="showActivator"
          depressed
          tile
          small
          icon
          :loading="loading"
          v-on="on"
        >
          <v-icon>{{ icons.mdiPlus }}</v-icon>
        </v-btn>
      </slot>
    </template>
    <v-card>
      <v-card-title>Ajouter une section</v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12">
            <v-text-field v-model="sectionName" label="Nom" :error-messages="errorMessage" />
          </v-col>
        </v-row>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="primary" tile outlined @click="dialog = false">
          Annuler
        </v-btn>
        <v-btn
          :disabled="!!errorMessage"
          color="primary"
          :loading="loading"
          tile
          depressed
          @click="addSection"
        >
          Ajouter
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import axios from 'axios'
import { mdiPlus } from '@mdi/js'
import { encode } from 'js-base64'

export default {
  props: {
    parent: {
      type: Object,
      required: true
    },
    showActivator: {
      type: Boolean,
      default: true
    },
    gitRef: {
      type: String,
      required: true
    }
  },
  data () {
    return {
      icons: { mdiPlus },
      dialog: false,
      loading: false,
      sectionName: 'Nouvelle section'
    }
  },
  computed: {
    projectId () {
      return this.gitRef.includes('projet') ? this.gitRef.replace('projet-', '') : null
    },
    errorMessage () {
      if (this.parent.children) {
        const sameNameChild = this.parent.children.find(c => c.name === this.sectionName)

        if (sameNameChild) { return 'Une section porte déjà ce nom.' }
      }

      if (this.sectionName.includes('/')) {
        return 'Le caractère / est interdit.'
      }

      return null
    }
  },
  methods: {
    async addSection () {
      this.loading = true
      const dir = this.parent.type === 'file' ? this.parent.path.replace('.md', '') : this.parent.path

      if (this.parent.type === 'file') {
        const { data: parentContent } = await axios({
          method: 'get',
          url: '/api/trames/file',
          params: {
            path: this.parent.path,
            ref: this.gitRef
          }
        })

        axios({
          method: 'delete',
          url: `/api/trames/${this.gitRef}`,
          data: {
            userId: this.$user.id,
            commit: {
              path: this.parent.path,
              sha: this.parent.sha
            }
          }
        })

        await axios({
          method: 'post',
          url: `/api/trames/${this.gitRef}`,
          data: {
            userId: this.$user.id,
            commit: {
              path: `${dir}/intro.md`,
              content: encode(parentContent)
            }
          }
        })
      }

      const newSectionPath = `${dir}/${this.sectionName}`

      if (this.projectId) {
        const { data: projects } = await this.$supabase.from('projects').select('PAC').eq('id', this.projectId)
        const paths = projects[0].PAC
        paths.push(newSectionPath)
        await this.$supabase.from('projects').update({ PAC: paths }).eq('id', this.projectId)
      }

      const { data: { data: { content: file } } } = await axios({
        method: 'post',
        url: `/api/trames/${this.gitRef}`,
        data: {
          userId: this.$user.id,
          commit: {
            path: `${newSectionPath}.md`,
            content: encode('Nouvelle section')
          }
        }
      })

      // console.log(file)
      file.name = file.name.replace('.md', '')
      file.children = []

      this.dialog = false
      this.$emit('added', file, this.parent)
      this.loading = false
    }
  }
}
</script>
