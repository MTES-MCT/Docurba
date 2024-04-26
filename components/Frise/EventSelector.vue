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
          hide-details
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
// import ScotEvents from '@/assets/data/events/SCOT_events.json'
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
        // TODO: On utilise la meme liste d'event que les PLU en attendant d'être a jour sur les SCOT
        SCOT: PluEvents,
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
    filteredEvents () {
      console.log('this.procedure: ', this.procedure)
      let internalType = 'aucun'
      const isIntercommunal = this.procedure.current_perimetre.length > 1

      const secondairesTypes = {
        'Révision à modalité simplifiée ou Révision allégée': 'rms',
        'Révision allégée (ou RMS)': 'rms',
        Modification: 'm',
        'Modification simplifiée': 'ms',
        'Mise en compatibilité': 'mc',
        'Mise à jour': 'mj'
      }
      if (secondairesTypes[this.procedure.type]) { internalType = secondairesTypes[this.procedure.type] }
      if (['Elaboration', 'Révision'].includes(this.procedure.type)) {
        if (isIntercommunal && this.internalDocType !== 'CC') { internalType = 'ppi' } else { internalType = 'pp' }
      }
      console.log(' this.documentEvents: ', this.documentEvents, ' internalType: ', internalType, ' this.procedure.type: ', this.procedure.type)
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
