<template>
  <v-dialog v-model="open" width="300px">
    <template #activator="{on}">
      <v-btn small icon v-on="on">
        <v-icon>{{ icons.mdiClose }}</v-icon>
      </v-btn>
    </template>
    <v-card>
      <v-card-title>Annuler ?</v-card-title>
      <v-card-text>
        Vos changements sur "{{ section.name }}" seront perdus.
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn tile depressed outlined @click="open = false">
          retour
        </v-btn>
        <v-btn tile depressed color="primary" @click="cancel">
          confirmer
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mdiContentSave, mdiClose } from '@mdi/js'

export default {
  props: {
    value: {
      type: Boolean,
      default: false
    },
    section: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      icons: { mdiContentSave, mdiClose },
      open: this.value
    }
  },
  watch: {
    value (val) {
      this.open = val
    }
  },
  methods: {
    cancel () {
      this.$emit('cancel')
      this.open = false
    }
  }
}
</script>
