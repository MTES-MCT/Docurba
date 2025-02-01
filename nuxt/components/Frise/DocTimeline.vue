<template>
  <v-row justify="end">
    <template v-if="!noProject && !censored">
      <v-col cols="12">
        <v-timeline align-top class="doc-timeline pt-0 mt-6">
          <v-timeline-item color="#E3E3FD" small>
            <v-btn nuxt color="primary" :to="{name: 'frise-procedureId-add', params: {procedureId: $route.params.procedureId}}">
              Ajouter un événement
            </v-btn>
          </v-timeline-item>
          <v-timeline-item right hide-dot>
            <span class="black--text"><b>Évènements suggérés par Docurba :</b></span>
          </v-timeline-item>
          <v-timeline-item v-for="event in recommendedEvents" :key="`recommended-${event.order}`" hide-dot right>
            <FriseRecommendedEventCard :event-type="event" />
          </v-timeline-item>
        </v-timeline>
      </v-col>
      <v-col offset="3" cols="9" class="pl-0">
        <v-divider />
      </v-col>
    </template>
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
          <FriseDocEventCard :event="event" :censored="censored" />
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
    censored: {
      type: Boolean,
      default: () => true
    },
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
      const eventsDisplayed = this.events.filter(e => !this.censored || e.visibility === 'public' || !e.visibility)
      return sortBy(eventsDisplayed, (event) => {
        return -this.$dayjs(event.date_iso).valueOf()
      })
    },
    recommendedEvents () {
      const lastEventType = this.documentEvents.find(event => this.orderedEvents[0].type === event.name)
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
