<template>
  <v-row>
    <v-col v-if="mixedProcedures" cols="12">
      <DashboardDUItem
        v-for="(procedure,i) in mixedProcedures"
        :key="'du_' + i"
        :procedure="procedure"
        censored
      />
    </v-col>
  </v-row>
</template>

<script>
import SudocuEvents from '@/mixins/SudocuEvents.js'

export default {
  mixins: [SudocuEvents],
  data () {
    return {
      docurbaDU: null
    }
  },
  computed: {
    mixedProcedures () {
      const sudocuProcedures = this.procedures ?? []
      return sudocuProcedures.concat(this.docurbaDU ?? [])
    }
  },
  async mounted () {
    await this.loadDocurbaProcedures()
  },
  methods: {
    async loadDocurbaProcedures () {
      const query = this.$supabase.from('projects').select('*, doc_frise_events(*)').match({
        owner: this.$user.id
      })

      let DUs
      if (this.$route.query.isEpci === 'true') {
        console.log('Loading EPCI Ducorba DU')
        DUs = await query.eq('epci->EPCI', this.$route.params.collectiviteId)
      } else {
        DUs = await query.contains('towns', JSON.stringify([{ code_commune_INSEE: this.$route.params.collectiviteId }]))
      }

      if (DUs.data) {
        this.docurbaDU = DUs.data.map(e => ({
          idProcedure: e.id,
          docType: e.doc_type,
          events: e.doc_frise_events.map(i => ({ ...i, docType: e.doc_type, idProcedure: e.id })),
          date_iso: this.$dayjs(e.created_at).format('YYYY-MM-DD'),
          procSecs: []
        }))
      }
      console.log('DUs: ', this.docurbaDU)
    }
  }
}
</script>
