<template>
  <div v-if="procedure">
    <v-container class="px-0 mt-8">
      <v-row align="end" class="mb-1">
        <v-col cols="auto">
          <button
            class="text-decoration-none d-flex align-center"
            @click="$router.back()"
          >
            <v-icon color="primary" small class="mr-2">
              {{ icons.mdiChevronLeft }}
            </v-icon>
            Retour
          </button>
          <h1>Modification de procédure</h1>
        </v-col>
      </v-row>
    </v-container>
    <ProceduresUpdateForm :procedure="procedure" />
  </div>
  <VGlobalLoader v-else />
</template>
<script>
import { mdiChevronLeft } from '@mdi/js'
export default {
  name: 'ProcedureUpdate',
  data () {
    return {
      procedure: null,
      icons: { mdiChevronLeft }
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

    // if (!this.$user.canCreateProcedure({ collectivite: this.collectivite })) {
    //   console.warn('Pas assez de droits pour créer une procédure sur ce périmètre')
    //   this.$nuxt.context.redirect(302, `/collectivites/${this.$route.params.collectiviteId}`)
    // }
  }
}
</script>
