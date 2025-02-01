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
      <v-col cols="12" class="pt-0">
        <h1 class="text-h1">
          Ajouter un événement
        </h1>
      </v-col>
    </v-row>
    <FriseEventForm v-if="procedure" :procedure="procedure" :type-du="$route.query.typeDu" />
  </v-container>
</template>

<script>
import { mdiChevronLeft } from '@mdi/js'

export default {
  name: 'AddTimelineEvent',
  layout ({ $user }) {
    if ($user?.profile?.poste === 'ddt' || $user?.profile?.poste === 'dreal') {
      return 'ddt'
    } else {
      return 'default'
    }
  },
  data () {
    return {
      icons: {
        mdiChevronLeft
      },
      procedure: null
    }
  },
  async mounted () {
    this.$user.isReady.then(() => {
      if (this.$user?.profile?.poste === 'ddt' || this.$user?.profile?.poste === 'dreal') {
        this.$nuxt.setLayout('ddt')
      }
    })
    const { data: procedure, error: errorProcedure } = await this.$supabase.from('procedures').select('project_id, id, type, doc_type, current_perimetre, collectivite_porteuse_id').eq('id', this.$route.params.procedureId)
    if (errorProcedure) { throw errorProcedure }
    this.procedure = procedure[0]
  }
}
</script>
