<template>
  <v-dialog v-model="dialog" width="500">
    <v-card>
      <v-card-title>Mes documents</v-card-title>
      <v-card-text>
        <v-tabs-items v-model="modalState">
          <v-tab-item id="list">
            Doc List
          </v-tab-item>
          <v-tab-item id="create">
            Create a new doc
          </v-tab-item>
        </v-tabs-items>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="primary" @click="modalState = 'create'">
          Nouveau
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: 'DocumentsDialog',
  props: {
    value: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      modalState: 'list'
    }
  },
  computed: {
    dialog: {
      get () {
        return this.value || false
      },
      set (val) {
        this.$emit('input', val)
      }
    }
  }
}
</script>
