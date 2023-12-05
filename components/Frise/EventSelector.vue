<template>
  <v-row>
    <v-col :cols="isOther ? 4 : 12">
      <v-autocomplete
        v-if="filteredEvents"
        v-model="selectedEvent"
        style="max-width:50%;"
        :items="filteredEvents"
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
    procedure: {
      type: Object,
      required: true
    },
    eventType: {
      type: String,
      required: true
    }
  },
  data () {
    return {
      customEvent: null,
      selectedEvent: null
    }
  },
  computed: {
    documentEvents () {
      const documentsEvents = {
        PLU: PluEvents,
        PLUi: PluEvents,
        POS: PluEvents,
        SCOT: ScotEvents,
        CC: ccEvents
      }
      console.log('internalDocType:', this.internalDocType)
      return documentsEvents[this.internalDocType]
    },
    internalDocType () {
      let currDocType = this.procedure.doc_type
      if (currDocType.includes('i')) {
        currDocType = currDocType.replace('i', '')
      }
      return currDocType
    },
    filteredEvents () {
      console.log('this.procedure: ', this.procedure)
      let internalType = 'aucun'
      const isIntercommunal = this.procedure.current_perimetre.length > 1

      const secondairesTypes = {
        'Révision à modalité simplifiée ou Révision allégée': 'rms',
        Modification: 'm',
        'Modification simplifiée': 'ms',
        'Mise en comptabilité': 'mc',
        'Mise à jour': 'mj'
      }
      if (secondairesTypes[this.procedure.type]) { internalType = secondairesTypes[this.procedure.type] }
      if (['Elaboration', 'Révision'].includes(this.procedure.type)) {
        if (isIntercommunal && this.internalDocType !== 'CC') { internalType = 'ppi' } else { internalType = 'pp' }
      }

      return this.documentEvents.filter(e => e.scope_liste.includes(internalType))
        .map(event => event.name)
        .sort((a, b) => a.order - b.order).concat(['Autre'])
    },
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
  },
  mounted () {
    console.log('this.eventType: ', this.eventType)
    const selectedEvent = this.documentEvents.find(event => event.name === this.eventType)
    console.log('selectedEvent: ', selectedEvent)

    this.customEvent = selectedEvent ? '' : this.eventType
    this.selectedEvent = selectedEvent ? selectedEvent.name : (this.eventType ? 'Autre' : '')
  }
}
</script>
