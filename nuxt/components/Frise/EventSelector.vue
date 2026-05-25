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
import { getDocumentTypeEvents, getProcedureEventsScope } from '@/plugins/event'

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
      return getDocumentTypeEvents(this.procedure.doc_type)
    },
    internalProcedureType () {
      return getProcedureEventsScope(this.procedure)
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
