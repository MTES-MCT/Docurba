<template>
  <v-row>
    <v-col cols="12">
      <v-timeline align-top class="doc-timeline">
        <v-timeline-item small>
          <v-btn nuxt color="primary" :to="`/projets/${projectId}/frise/add`">
            Ajouter un événement
          </v-btn>
        </v-timeline-item>
      </v-timeline>
    </v-col>
    <v-col cols="12">
      <v-timeline align-top class="doc-timeline">
        <v-timeline-item v-for="event in orderedEvents" :key="event.id" small right>
          <template #opposite>
            <v-chip>{{ formatDate(event.date_iso) }}</v-chip>
          </template>
          <FriseDocEventCard :event="event" />
        </v-timeline-item>
      </v-timeline>
    </v-col>
  </v-row>
</template>

<script>
import dayjs from 'dayjs'
import { sortBy } from 'lodash'

export default {
  props: {
    projectId: {
      type: String,
      default () {
        return this.$route.params.projectId
      }
    }
  },
  data () {
    return {
      events: []
    }
  },
  computed: {
    orderedEvents () {
      return sortBy(this.events, (event) => {
        return -dayjs(event.date_iso).valueOf()
      })
    }
  },
  async mounted () {
    const { data: events } = await this.$supabase.from('doc_frise_events').select('*').eq('project_id', this.projectId)
    this.events = events
  },
  methods: {
    formatDate (isoDate) {
      return dayjs(isoDate).format('DD/MM/YYYY')
    }
  }
}
</script>

<style>
.doc-timeline .v-timeline-item__opposite {
  align-self: baseline;
  max-width: calc(25% - 48px);
}

.doc-timeline .v-timeline-item__body {
  max-width: calc(75% - 48px) !important;
  flex: 3 3 auto;
}

.doc-timeline::before {
  left: calc(25% - 1px) !important;
}

.doc-timeline .v-card:before {
  display: none;
}
</style>
