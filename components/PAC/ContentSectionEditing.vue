<template>
  <v-row>
    <v-col cols="12">
      <v-text-field v-model="editedSection.titre" label="titre" filled hide-details />
    </v-col>
    <v-col cols="12">
      <VTiptap v-model="editedSection.text" />
    </v-col>
    <v-fab-transition>
      <v-btn
        v-show="modified"
        fixed
        bottom
        right
        fab
        color="primary"
        @click="saveSection"
      >
        <v-icon color="white">
          {{ icons.mdiContentSave }}
        </v-icon>
      </v-btn>
    </v-fab-transition>
  </v-row>
</template>
<script>
import { mdiContentSave } from '@mdi/js'

export default {
  props: {
    text: {
      type: String,
      default: ''
    },
    titre: {
      type: String,
      default: ''
    }
  },
  data () {
    return {
      editedSection: {
        text: this.text,
        titre: this.titre
      },
      modified: false,
      icons: {
        mdiContentSave
      }
    }
  },
  watch: {
    text () {
      this.editedSection.text = this.text
    },
    titre () {
      this.editedSection.titre = this.titre
    },
    editedSection: {
      deep: true,
      handler () {
        if (this.titre !== this.editedSection.titre || this.editedSection.text !== this.text) {
          this.modified = true
        } else {
          this.modified = false
        }
      }
    }
  },
  methods: {
    saveSection () {
      this.$emit('save', this.editedSection)
      this.modified = false
    }
  }
}
</script>
