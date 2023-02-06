<template>
  <v-dialog
    v-model="dialog"
    width="500"
  >
    <template #activator="{on}">
      <v-btn
        v-show="showActivator"
        depressed
        tile
        small
        icon
        :loading="loading"
        v-on="on"
      >
        <v-icon>{{ icons.mdiDelete }}</v-icon>
      </v-btn>
    </template>
    <template #default>
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
    </template>
  </v-dialog>
</template>
<script>
import axios from 'axios'
import { mdiDelete } from '@mdi/js'

export default {
  props: {
    section: {
      type: Object,
      required: true
    },
    showActivator: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      icons: { mdiDelete },
      dialog: false,
      loading: false
    }
  },
  methods: {
    async removeSection () {
      this.loading = true

      await axios({
        method: 'delete',
        url: '/api/trames/test', // TODO: replace test by actual ref: dept, projectId or region,
        data: {
          userId: this.$user.id,
          commit: {
            path: this.section.path,
            sha: this.section.sha
          }
        }
      })

      this.dialog = false
      this.$emit('update')
      this.laoding = false
    }
  }
}
</script>
