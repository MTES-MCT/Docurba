<template>
  <v-app>
    <LayoutsAppBar flat extended>
      <v-tabs v-if="$user.profile.verified" align-with-title class="header-tabs">
        <v-tab
          v-if="$user.profile.poste === 'ddt'"
          :to="{
            name: 'ddt-departement-collectivites',
            params: {departement: $user.profile.departement}
          }"
        >
          Mes collectivites
        </v-tab>
        <v-tab
          :to="{
            name: 'trames-githubRef',
            params: {githubRef: trameRef}
          }"
        >
          Trame de PAC {{ trameRef.includes('region') ? 'régionale' : 'départementale' }}
        </v-tab>
        <v-tab
          v-if="$user.profile.poste === 'ddt'"
          :to="{
            name: 'ddt-departement-pac',
            params: {departement: $user.profile.departement}
          }"
        >
          Mes PAC
        </v-tab>
        <v-tab
          v-if="ddtBetaTest"
          :to="{
            name:'ddt-departement-collectivites-enquete',
            params: {departement: $route.params.departement}
          }"
        >
          Validation des procédures
        </v-tab>
      </v-tabs>
    </LayoutsAppBar>
    <v-main class="beige">
      <v-container v-if="isLoading" class="fill-height">
        <v-row justify="center" align="center">
          <v-col cols="12">
            <VGlobalLoader />
          </v-col>
        </v-row>
      </v-container>
      <template v-else>
        <nuxt v-if="isAllowed" />
        <v-container v-else class="fill-height">
          <v-row justify="center" align="center">
            <v-col cols="12" class="mb-4">
              <div class="text-center text-h2">
                En attente de validation
              </div>
            </v-col>
            <v-col cols="12">
              <v-img height="200" contain src="/images/errors/maintenance.svg" />
            </v-col>
          </v-row>
        </v-container>
      </template>
    </v-main>
    <LayoutsFooter />
  </v-app>
</template>

<script>
import axios from 'axios'

const validationBetaDDT = [
  '25', '29', '35', '56', '58',
  '81', '89'
]

export default {
  name: 'DdtLayout',
  data () {
    return { isLoading: true }
  },
  computed: {
    isAllowed () {
      // console.log('this.$user?.profile: ', this.$user.profile)
      return (this.$user?.profile?.side === 'etat' && this.$user?.profile?.verified) || this.$isDev
    },
    trameRef () {
      const scopes = { ddt: 'dept', dreal: 'region' }
      const poste = this.$user.profile.poste
      const code = poste === 'ddt' ? this.$user.profile.departement : this.$user.profile.region

      return `${scopes[poste]}-${this.$options.filters.deptToRef(code)}`
    },
    ddtBetaTest () {
      return validationBetaDDT.includes(this.$route.params.departement)
    }
  },
  async mounted () {
    await this.$user.isReady
    this.isLoading = false

    if (this.$user.profile.side !== 'etat' && !this.$isDev) { this.$router.push('/') }

    if (this.$route.query.contact) {
      axios({
        url: '/api/pipedrive/contacted',
        method: 'post',
        data: {
          email: this.$route.query.contact
        }
      })
    }
  }
}
</script>

<style>
.header-tabs {
  border-top: solid 1px var(--v-grey-base);
  border-bottom: solid 1px var(--v-grey-base);
}
.header-tabs .v-tab {
  color: var(--v-typo-base) !important;
  text-transform: none;
}
</style>
