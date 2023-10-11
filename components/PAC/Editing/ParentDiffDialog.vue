<template>
  <v-dialog v-model="open" width="400px">
    <template #activator="{on}">
      <!-- <v-badge overlap color="grey" :icon="icons.mdiCheck" @click.stop="open = true"> -->
      <v-tooltip top>
        <template #activator="tooltip">
          <div v-show="!saved" v-on="tooltip.on">
            <slot :on="on" />
          </div>
        </template>
        <span>Marquer comme lu</span>
      </v-tooltip>
      <!-- </v-badge> -->
    </template>
    <v-card>
      <v-card-title>Marquer comme lu ?</v-card-title>
      <v-card-text>
        Si vous avez pris en compte les dernières modifications les marquer comme lus fera disparaitre l'alerte. Vous pourrez toujours comparer votre section à sa trame parente.
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn tile depressed outlined @click="open = false">
          retour
        </v-btn>
        <v-btn tile depressed color="primary" @click="saveParentSha">
          Marquer comme lu
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mdiContentSave, mdiCheck } from '@mdi/js'

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
    gitRef: {
      type: String,
      required: true
    }
  },
  data () {
    return {
      icons: { mdiContentSave, mdiCheck },
      open: this.value,
      saved: false
    }
  },
  watch: {
    value (val) {
      this.open = val
    }
  },
  methods: {
    saveParentSha () {
      this.$supabase.from('pac_sections').upsert({
        parent_sha: this.section.diff.sha,
        path: this.section.path,
        ref: this.gitRef
      }).then((res) => {
        this.saved = true
      })// .catch(err => console.log('err saving', err))

      this.open = false
    }
  }
}
</script>
