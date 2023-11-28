<template>
  <v-row>
    <v-col :cols="isOther ? 4 : 12">
      <v-autocomplete
        v-model="selectedEvent"
        style="max-width:50%;"
        :items="eventsNames"
        hide-details
        filled
        label="Type"
      />
    </v-col>
    <v-col v-show="isOther">
      <v-text-field v-model="customEvent" hide-details filled />
    </v-col>
  </v-row>
</template>
<script>
import PluEvents from '@/assets/data/events/PLU_events.json'
import ScotEvents from '@/assets/data/events/SCOT_events.json'
import ccEvents from '@/assets/data/events/CC_events.json'

export default {
  model: {
    prop: 'eventType',
    event: 'input'
  },
  props: {
    typeDu: {
      type: String,
      required: true
    },
    eventType: {
      type: String,
      required: true
    }
  },
  data () {
    const documentsEvents = {
      PLU: PluEvents,
      scot: ScotEvents,
      cc: ccEvents
    }
    console.log('typeDu: ', this.typeDu)
    const documentEvents = documentsEvents[this.typeDu]
    const selectedEvent = documentEvents.find((event) => {
      return event.name === this.eventType
    })

    const names = documentEvents.map(event => event.name).sort((a, b) => a.order - b.order)
    names.push('Autre')

    return {
      documentEvents,
      customEvent: selectedEvent ? '' : this.eventType,
      eventsNames: names,
      selectedEvent: selectedEvent ? selectedEvent.name : (this.eventType ? 'Autre' : '')
    }
  },
  computed: {
    isOther () {
      return this.selectedEvent === 'Autre'
    }
  },
  watch: {
    selectedEvent () {
      if (!this.isOther) {
        this.$emit('input', this.selectedEvent)
      } else { this.$emit('input', this.customEvent) }
    },
    customEvent () {
      if (this.isOther) {
        this.$emit('input', this.customEvent)
      }
    }
  }
}
</script>
