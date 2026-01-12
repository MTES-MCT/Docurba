<template>
  <v-app>
    <!-- Keeping this in case we want to make annoncements. -->
    <!-- <v-dialog v-model="showTally" eager max-width="500px">
      <v-sheet color="white">
        <iframe
          data-tally-src="https://tally.so/embed/m6kNJP?alignLeft=1&transparentBackground=1&dynamicHeight=1"
          loading="lazy"
          width="100%"
          height="650"
          frameborder="0"
          marginheight="0"
          marginwidth="0"
          title="🎨 Nouveau Tableau de Bord !"
        />
      </v-sheet>
    </v-dialog> -->
    <LayoutsAppBar flat extended>
      <v-tabs v-if="$user.profile.verified" align-with-title class="header-tabs">
        <v-tab
          v-if="$user.canViewSectionCollectivites({ departement: $user.profile.departement })"
          :to="{
            name: 'ddt-departement-collectivites',
            params: {departement: $user.profile.departement}
          }"
        >
          Mes collectivités
        </v-tab>
        <v-tab
          v-if="$user.canViewSectionProcedures({ departement: $user.profile.departement })"
          :to="`/ddt/${$user.profile.departement}/procedures`"
        >
          Mes procédures
        </v-tab>
        <v-tab
          v-if="$user.canViewSectionTramesPAC()"
          :to="{
            name: 'trames-githubRef',
            params: {githubRef: trameRef}
          }"
        >
          Trame de PAC {{ trameRef.includes('region') ? 'régionale' : 'départementale' }}
        </v-tab>
        <v-tab
          v-if="$user.canViewSectionPAC()"
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
        <nuxt v-if="isVerified" />
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

const validationBetaDDT = []

export default {
  name: 'DdtLayout',
  data () {
    return {
      isLoading: true
      // showTally: false
    }
  },
  computed: {
    isVerified () {
      return this.$user?.profile?.verified || this.$user.profile.is_admin
    },
    trameRef () {
      if (this.$user.canViewSectionTramesPAC()) {
        const scopes = { ddt: 'dept', dreal: 'region' }
        const poste = this.$user.profile.poste
        const code = poste === 'ddt' ? this.$user.profile.departement : this.$user.profile.region

        return `${scopes[poste]}-${this.$options.filters.deptToRef(code)}`
      }
      return ''
    },
    ddtBetaTest () {
      return validationBetaDDT.includes(this.$route.params.departement)
    }
  },
  async mounted () {
    await this.$user.isReady
    this.isLoading = false

    if (!['etat', 'ppa'].includes(this.$user.profile.side)) {
      console.warn('Page réservée aux sides État ou PPA.')
      this.$nuxt.context.redirect(403, '/')
    }

    // const displayedKey = 'tally-displayed-m6kNJP'
    // const formNb = window.localStorage.getItem(displayedKey) || 0
    // if (formNb < 1) {
    //   this.showTally = true
    //   window.Tally.loadEmbeds()
    //   localStorage.setItem(displayedKey, +formNb + 1)
    // }

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
