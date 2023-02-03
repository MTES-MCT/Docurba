<template>
  <v-row justify="end">
    <v-col cols="12">
      <v-timeline v-if="!noProject" align-top class="doc-timeline pt-0 mt-6">
        <v-timeline-item color="#E3E3FD" small>
          <v-btn nuxt color="primary" :to="`/projets/${projectId}/frise/add`">
            Ajouter un événement
          </v-btn>
        </v-timeline-item>
        <v-timeline-item right hide-dot>
          <span class="black--text"><b>Évènements suggérés par Docurba :</b></span>
        </v-timeline-item>
        <v-timeline-item
          v-for="event in recommendedEvents"
          :key="`recommended-${event.order}`"
          hide-dot
          right
        >
          <FriseRecommendedEventCard :event-type="event" />
        </v-timeline-item>
      </v-timeline>
    </v-col>
    <v-col v-if="!noProject" offset="3" cols="9" class="pl-0">
      <v-divider />
    </v-col>
    <v-col cols="12">
      <v-timeline align-top class="doc-timeline">
        <v-timeline-item
          v-for="event in orderedEvents"
          :id="`event-${event.id}`"
          :key="event.id"
          :color="event.color"
          small
          right
        >
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
import { sortBy } from 'lodash'
import documentEvents from '@/assets/data/DU_events.json'

export default {
  props: {
    noProject: {
      type: Boolean,
      default: () => false
    },
    projectId: {
      type: String,
      default () {
        return this.$route.params.projectId
      }
    },
    events: {
      type: Array,
      required: true
    }
  },
  data () {
    return {
      documentEvents
    }
  },
  computed: {
    orderedEvents () {
      return sortBy(this.events, (event) => {
        return -this.$dayjs(event.date_iso).valueOf()
      })
    },
    recommendedEvents () {
      const lastEventType = this.orderedEvents.find((event) => {
        return this.documentEvents.find(eventType => eventType.name === event)
      })

      const lastEventOrder = lastEventType ? lastEventType.order : -1

      const recommendedEvents = [
        this.findRecommendedEventType(lastEventOrder, 2),
        this.findRecommendedEventType(lastEventOrder, 1)
      ]

      return recommendedEvents.filter(e => !!e)
    }
  },
  methods: {
    findRecommendedEventType (order, priority) {
      return this.documentEvents.find((eventType) => {
        return eventType.recommended === priority && eventType.order > order
      })
    },
    formatDate (isoDate) {
      return this.$dayjs(isoDate).format('DD/MM/YYYY')
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
  left: calc(25% - 2px) !important;
  width: 4px;
  background: repeating-linear-gradient(180deg, #E3E3FD, #E3E3FD 14px, #FFFFFF 14px, #FFFFFF 21px) !important;
}

.doc-timeline .v-card:before {
  display: none;
}

.doc-timeline .v-timeline-item__dot {
  box-shadow: none !important;
}
</style>
