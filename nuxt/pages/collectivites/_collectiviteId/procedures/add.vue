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
    // const collectivites = await this.$nuxt3api(`/api/geo/search/collectivites?code= ${this.$route.params.collectiviteId}&populate=true`)

        // {
        // "type": "CA",
        // "intitule": "Haut - Bugey Agglomération",
        // "siren": "200042935",
        // "code": "200042935",
        // "regionCode": "84",
        // "departementCode": "01",
        // "competencePLU": true,
        // "competenceSCOT": true,
        // "membres": [
        //               {
        //         "type": "COM",
        //         "intitule": "Bellignat",
        //         "siren": "210100319",
        //         "code": "01031"
        //     },
        // ],
        // "groupements": [
        //     {
        //         "type": "SMF",
        //         "intitule": "SIVU de la Combe de Vaux",
        //         "siren": "200052041",
        //         "code": "200052041"
        //     },
        //   ]
        // TODO: check if it's flat or one-level only.

    const collectivites = await this.$djangoApi.get('/api-internes/collectivites/', {
      code: this.$route.params.collectiviteId,
      avec_membres:true,
      avec_groupements: true,
    })
    this.collectivite = collectivites[0]

    if (!this.$user.canCreateProcedure({ collectivite: this.collectivite })) {
      console.warn('Pas assez de droits pour créer une procédure sur ce périmètre')
      this.$nuxt.context.redirect(302, `/collectivites/${this.$route.params.collectiviteId}`)
    }
  }
}
</script>
