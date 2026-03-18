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
    <!-- <ProceduresUpdateForm :procedure="procedure" /> -->
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
      icons: { mdiChevronLeft },
      snackbar: { text: '', val: false }
    }
  },
  async mounted () {
    this.$user.isReady.then(() => {
      // if (this.$user?.profile?.poste === 'ddt' || this.$user?.profile?.poste === 'dreal') {
      //   this.$nuxt.setLayout('ddt')
      // }
    })
    const { data: procedure, error: errorProcedure } = await this.$supabase.from('procedures').select('id', 'owner_id').eq('id', this.$route.params.procedureId)
    if (errorProcedure) { throw errorProcedure }
    this.procedure = procedure[0]

    if (this.$user.canUpdateProcedure({ procedure: this.procedure })) {
      // eslint-disable-next-line no-console
      console.log('Vous ne pouvez pas modifier cette procédure.')
      localStorage.setItem('snackbarDict', JSON.stringify({ text: 'Vous ne pouvez pas modifier cette procédure.', color: 'error' }))
      this.$router.back()
    }
  }
}
</script>
