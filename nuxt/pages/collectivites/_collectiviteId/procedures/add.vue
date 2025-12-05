<template>
  <div v-if="collectivite">
    <v-container class="px-0 mt-8">
      <v-row align="end" class="mb-1">
        <v-col cols="auto">
          <nuxt-link
            class="text-decoration-none d-flex align-center"
            :to="`/collectivites/${$route.params.collectiviteId}`"
          >
            <v-icon color="primary" small class="mr-2">
              {{ icons.mdiChevronLeft }}
            </v-icon>
            {{ collectivite.intitule }}
          </nuxt-link>
          <h1>Nouvelle procédure</h1>
        </v-col>
      </v-row>
    </v-container>
    <ProceduresInsertTabs :collectivite="collectivite" />
  </div>
  <VGlobalLoader v-else />
</template>
<script>
import { mdiChevronLeft } from '@mdi/js'
export default {
  name: 'ProcedureAdd',
  data () {
    return {
      collectivite: null,
      icons: { mdiChevronLeft }
    }
  },
  async mounted () {
    const collectivites = await this.$nuxt3api(`/api/geo/search/collectivites?code=${this.$route.params.collectiviteId}&populate=true`)
    this.collectivite = collectivites[0]

    if (!this.$user.canCreateProcedure({ collectivite: this.collectivite })) {
      console.warn('Pas assez de droits pour créer une procédure sur ce périmètre')
      this.$nuxt.context.redirect(302, `/collectivites/${this.$route.params.collectiviteId}`)
    }
  }
}
</script>
