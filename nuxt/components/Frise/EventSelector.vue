<template>
  <v-row>
    <v-col :cols="isOther ? 4 : 12">
      <validation-provider v-slot="{ errors }" name="Type évènement" rules="required">
        <v-autocomplete
          v-if="filteredEvents"
          v-model="selectedEvent"
          :error-messages="errors"
          style="max-width:50%;"
          :items="filteredEvents"
          hide-details="auto"
          filled
          label="Type"
        />
      </validation-provider>
    </v-col>
    <v-col v-if="isOther">
      <validation-provider v-slot="{ errors }" name="autre évènement" rules="required">
        <v-text-field v-model="customEvent" filled :error-messages="errors" />
      </validation-provider>
    </v-col>
  </v-row>
</template>
<script>
import FormInput from '@/mixins/FormInput.js'

import PluEvents from '@/assets/data/events/PLU_events.json'
import ScotEvents from '@/assets/data/events/SCOT_events.json'
import ccEvents from '@/assets/data/events/CC_events.json'

export default {
  mixins: [FormInput],
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
      if (currDocType.match(/i|H|M/)) {
        currDocType = 'PLU'
      }
      return currDocType
    },
    internalProcedureType () {
      switch (this.procedure.type) {
        case 'Elaboration':
        case 'Révision':
          return this.procedure.current_perimetre.length > 1 && this.internalDocType !== 'CC' ? 'ppi' : 'pp'
        case 'Mise à jour':
          return 'mj'
        case 'Mise en compatibilité':
          return 'mc'
        case 'Modification':
          return this.procedure.started_before_huwart_law ? 'm' : 'mlh'
        case 'Modification simplifiée':
          return 'ms'
        case 'Révision allégée (ou RMS)':
        case 'Révision à modalité simplifiée ou Révision allégée':
          return 'rms'
        default:
          return 'aucun'
      }
    },
    filteredEvents () {
      return this.documentEvents.filter(e => e.scope_liste.includes(this.internalProcedureType))
        .sort((a, b) => a.order - b.order)
        .map(event => event.name)
        .concat(['Autre'])
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
