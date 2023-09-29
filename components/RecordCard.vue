<template>
  <v-card flat outlined class="d-flex flex-column">
    <v-card-title class="break-word">
      {{ record.title }}
    </v-card-title>
    <v-card-text class="record-description">
      {{ record.description }}
    </v-card-text>
    <v-spacer />
    <v-card-actions>
      <div class="record-card-actions">
        <v-btn
          v-for="dl in downloadLinks"
          :key="dl.url"
          class="download-button"
          :href="dl.url"
          text
          tile
          block
          color="primary"
        >
          <v-icon>
            {{ icons.mdiDownload }}
          </v-icon>
          {{ (dl.description || dl.name) ?? 'Télécharger' }}
        </v-btn>
        <v-btn
          depressed
          tile
          block
          color="primary"
          :href="record.url"
          target="_blank"
        >
          Voir la ressource
        </v-btn>
      </div>
    </v-card-actions>
  </v-card>
</template>

<script>
import { mdiDownload } from '@mdi/js'

export default {
  props: {
    record: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      icons: {
        mdiDownload
      }
    }
  },
  computed: {
    downloadLinks () {
      return this.record.links.filter(link => link.protocol?.startsWith('WWW:DOWNLOAD'))
    }
  }
}
</script>

<style>
.record-description {
  max-height: 200px;
  overflow-y: auto;
}

.record-card-actions {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.download-button .v-btn__content {
  max-width: 100%;
  display: block;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}
</style>
