<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <p class="text-h2">
          Import des évènements Sudocu
        </p>
        <VTownAutocomplete v-model="selectedTown" />
      </v-col>
      <v-col cols="12">
        <v-btn color="primary" depressed :loading="loading" @click="loadCommuneEvents">
          Visualiser
        </v-btn>
      </v-col>
    </v-row>
    <v-row v-if="!loading && events && docTypes.length === 0">
      <v-col cols="12">
        <div>Pas d'events pour cette commune</div>
      </v-col>
    </v-row>
    <template v-else-if="!loading && events && docTypes.length > 0">
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
      loading: false,
      events: null
    }
  },
  computed: {
    docTypes () {
      return Object.keys(this.events)
    }
  },
  mounted () {
    // this.loadCommuneEvents()
  },
  methods: {
    async loadCommuneEvents (commune) {
      const rawEvents = (await this.$supabase.from('sudocu_events').select().eq('codeinseecommune', this.selectedTown.code_commune_INSEE.toString().padStart(5, '0'))).data
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
      console.log('events: ', this.events)
      this.loading = false
    }
  }
}
</script>
