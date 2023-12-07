<template>
  <div class="d-flex" :style="{ gap: '0.5rem', flexWrap: 'wrap' }">
    <v-card
      v-for="attachment in attachments"
      :key="attachment.id"
      class="d-flex flex-column"
      width="16rem"
      flat
      outlined
    >
      <v-card-title>
        <div class="d-flex" :style="{ width: '100%', justifyContent: 'space-between' }">
          <div>{{ attachment.title }}</div>
          <v-btn icon small @click="openDialog(attachment)">
            <v-icon small>
              {{ icons.mdiClose }}
            </v-icon>
          </v-btn>
        </div>
      </v-card-title>
      <v-card-text>
        <v-chip>{{ sources[attachment.source] }}</v-chip>
        <div class="mt-2">
          {{ attachment.category }}
        </div>
      </v-card-text>
      <v-spacer />
      <v-card-actions>
        <v-btn
          text
          color="primary"
          :href="attachment.url"
          target="_blank"
        >
          Voir la ressource
        </v-btn>
      </v-card-actions>
    </v-card>
    <v-dialog v-if="selectedAttachment" max-width="600px" :value="dialog">
      <v-card>
        <v-card-title>
          Supprimer {{ selectedAttachment.title }} ?
        </v-card-title>

        <v-card-actions>
          <v-spacer />
          <v-btn depressed tile text color="primary" @click="dialog = false">
            Annuler
          </v-btn>
          <v-btn depressed tile color="primary" @click="removeAttachment(selectedAttachment)">
            Supprimer
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mdiClose } from '@mdi/js'

export default {
  model: {
    prop: 'attachments',
    event: 'input'
  },
  props: {
    section: {
      type: Object,
      required: true
    },
    gitRef: {
      type: String,
      required: true
    },
    attachments: {
      type: Array,
      required: true
    }
  },
  data () {
    return {
      dialog: false,
      selectedAttachment: null,
      subscription: null,
      icons: {
        mdiClose
      },
      sources: {
        BASE_TERRITORIALE: 'Base territoriale',
        GEORISQUES: 'GéoRisques',
        INPN: 'INPN'
      }
    }
  },
  methods: {
    openDialog (attachment) {
      this.selectedAttachment = attachment
      this.dialog = true
    },
    async removeAttachment (attachment) {
      await this.$supabase.from('pac_sections_data').delete().eq('id', attachment.id)
      this.$emit('input', this.attachments.filter(a => a.id !== attachment.id))
      this.dialog = false
    }
  }
}
</script>
