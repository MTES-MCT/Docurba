<template>
  <v-card outlined color="alt-beige">
    <v-card-title>Répères temporels</v-card-title>
    <v-card-text>
      <v-timeline dense class="checkpoints-timeline">
        <v-timeline-item small>
          <v-btn text @click="scrollTo(checkpoints[0].eventId)">
            Aujourd'hui
          </v-btn>
        </v-timeline-item>
        <v-timeline-item
          v-for="checkpoint in checkpoints"
          :key="checkpoint.date"
          hide-dot
        >
          <v-btn text @click="scrollTo(checkpoint.eventId)">
            {{ checkpoint.text }}
          </v-btn>
        </v-timeline-item>
      </v-timeline>
    </v-card-text>
  </v-card>
</template>

<script>
import { groupBy, sortBy } from 'lodash'

export default {
  props: {
    events: {
      type: Array,
      required: true
    }
  },
  computed: {
    checkpoints () {
      const months = groupBy(this.events, event => event.date_iso.slice(0, 7))

      const checkpoints = Object.keys(months).map((month) => {
        const monthEvents = sortBy(months[month], (event) => {
          return -this.$dayjs(event.date_iso).valueOf()
        })

        return {
          text: this.$dayjs(`${month}-01`).format('MMMM YYYY'),
          date: `${month}-01`,
          eventId: monthEvents[0].id
        }
      })

      return sortBy(checkpoints, (checkpoint) => {
        return -this.$dayjs(checkpoint.date).valueOf()
      })
    }
  },
  methods: {
    scrollTo (eventId) {
      this.$vuetify.goTo(`#event-${eventId}`)
    }
  }
}
</script>

<style>
.checkpoints-timeline::before {
  background: repeating-linear-gradient(180deg, #E3E3FD, #E3E3FD 14px, #F6F6F6 14px, #F6F6F6 21px) !important;
}
</style>
