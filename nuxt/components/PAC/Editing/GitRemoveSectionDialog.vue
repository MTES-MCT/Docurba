<template>
  <v-dialog
    v-model="dialog"
    width="500"
  >
    <template #activator="{on}">
      <v-btn
        v-show="showActivator"
        depressed
        small
        icon
        :loading="loading"
        v-on="on"
      >
        <v-icon>{{ icons.mdiDelete }}</v-icon>
      </v-btn>
    </template>
    <v-card>
      <v-card-title>Supprimer {{ section.name }}</v-card-title>
      <v-card-text>
        Etes vous sur de vouloir supprimer cette section ? Attention, les sous-sections seront elles aussi suprimées.
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn depressed tile color="primary" :loading="loading" @click="removeSection">
          Supprimer
        </v-btn>
        <v-btn depressed tile color="primary" outlined @click="dialog = false">
          Annuler
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
<script>
import axios from 'axios'
import { mdiDelete } from '@mdi/js'

export default {
  props: {
    value: {
      type: Boolean,
      default: false
    },
    section: {
      type: Object,
      required: true
    },
    showActivator: {
      type: Boolean,
      default: false
    },
    gitRef: {
      type: String,
      required: true
    }
  },
  data () {
    return {
      icons: { mdiDelete },
      dialog: this.value,
      loading: false
    }
  },
  watch: {
    dialog () {
      this.$emit('input', this.dialog)
    }
  },
  methods: {
    async deleteSection (section) {
      // Todo, this could use git API tree to avoid making a call for each children.
      if (section.type === 'file') {
        await axios({
          method: 'delete',
          url: `/api/trames/${this.gitRef}`,
          data: {
            userId: this.$user.id,
            commit: {
              path: section.path,
              sha: section.sha
            }
          }
        })
      } else if (section.type === 'dir') {
        await axios({
          method: 'delete',
          url: `/api/trames/${this.gitRef}`,
          data: {
            userId: this.$user.id,
            commit: {
              path: `${section.path}/intro.md`,
              sha: section.introSha
            }
          }
        })

        await Promise.all(section.children.map((child) => {
          return this.deleteSection(child)
        }))
      }
    },
    async removeSection () {
      this.loading = true

      await this.deleteSection(this.section)

      this.dialog = false
      this.loading = false
      this.$emit('removed', this.section)
    }
  }
}
</script>
