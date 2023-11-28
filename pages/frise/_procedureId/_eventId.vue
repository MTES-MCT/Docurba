<template>
  <v-container>
    <v-row>
      <v-col cols="12" class="mt-6">
        <nuxt-link :to="`/frise/${$route.params.procedureId}`" class="text-decoration-none d-flex align-center">
          <v-icon color="primary" small class="mr-2">
            {{ icons.mdiChevronLeft }}
          </v-icon>
          Revenir à la feuille de route
        </nuxt-link>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h1">
          Modification d'évènement
        </h1>
      </v-col>
      <FriseEventForm v-if="!loading" v-model="event" :procedure="procedure" :type-du="$route.query.typeDu" />
      <VGlobalLoader v-else />
    </v-row>
  </v-container>
</template>

<script>
import { mdiChevronLeft } from '@mdi/js'

export default {
  data () {
    return {
      icons: { mdiChevronLeft },
      procedure: null,
      event: null,
      loading: true
    }
  },
  async mounted () {
    this.$user.isReady.then(() => {
      if (this.$user?.profile?.poste === 'ddt' || this.$user?.profile?.poste === 'dreal') {
        this.$nuxt.setLayout('ddt')
      }
    })

    const { data: procedure, error: errorProcedure } = await this.$supabase.from('procedures').select('project_id, id').eq('id', this.$route.params.procedureId)
    if (errorProcedure) { throw errorProcedure }
    this.procedure = procedure[0]

    const { data: event, error: errorEvent } = await this.$supabase.from('doc_frise_events').select('*').eq('id', this.$route.params.eventId)
    if (errorEvent) { throw errorEvent }
    this.event = event[0]
    console.log('this.event: ', event)
    this.loading = false
  }
}
</script>
