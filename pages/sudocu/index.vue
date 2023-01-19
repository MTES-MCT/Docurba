<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <p class="text-h2">
          Import des évènements Sudocu
        </p>
        <VTownAutocomplete v-model="selectedTown" />
      </v-col>
    </v-row>
    <template v-if="!loading">
      <v-row>
        <v-col cols="12">
          <v-tabs v-model="selectedDocType">
            <v-tab v-for="docType in docTypes" :key="docType">
              {{ docType }}
            </v-tab>
          </v-tabs>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
          <FriseDocTimeline :events="events[docTypes[selectedDocType]]" no-project />
        </v-col>
      </v-row>
    </template>
  </v-container>
</template>
<script>
export default {
  name: 'Sudocu',
  data () {
    return {
      selectedTown: null,
      selectedDocType: null,
      loading: true,
      events: []
    }
  },
  computed: {
    docTypes () {
      return Object.keys(this.events)
    }
  },
  mounted () {
    this.loadCommuneEvents()
  },
  methods: {
    async loadCommuneEvents (commune) {
      const rawEvents = (await this.$supabase.from('sudocu_events').select()).data
      const formattedEvents = rawEvents.map((e) => {
        return {
          date_iso: e.dateevenement,
          type: e.libtypeevenement,
          description: '',
          actors: [],
          attachements: [],
          docType: e.codetypedocument
        }
      })
      this.events = formattedEvents.reduce(function (r, a) {
        r[a.docType] = r[a.docType] || []
        r[a.docType].push(a)
        return r
      }, Object.create(null))

      this.selectedDocType = 0
      console.log('test: ', this.events, ' this.selectedDocType: ', this.selectedDocType, ' selectedDocType: ', this.events[this.selectedDocType])
      this.loading = false
    }
  }
}
</script>
