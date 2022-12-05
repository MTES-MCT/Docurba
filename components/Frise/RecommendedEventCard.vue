<template>
  <v-card
    :to="`/projets/${projectId}/frise/add?eventType=${eventType.name}`"
    nuxt
    flat
    class="recommended-card"
  >
    <v-card-title>
      <v-avatar size="32" color="bf200" class="mr-2">
        <v-icon small color="primary">
          {{ icons.mdiCalendar }}
        </v-icon>
      </v-avatar>{{ eventType.name }}
    </v-card-title>
  </v-card>
</template>

<script>
import { mdiCalendar } from '@mdi/js'

export default {
  props: {
    eventType: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      icons: { mdiCalendar }
    }
  }
}
</script>

<style lang="scss" scoped>
.recommended-card {
  border: 1px dashed #000091;
}
</style>
