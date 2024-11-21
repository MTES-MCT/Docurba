<template>
  <div v-if="collectivite">
    <v-container class="px-0 mt-8">
      <v-row align="end" class="mb-1">
        <v-col cols="auto">
          <nuxt-link
            class="text-decoration-none d-flex align-center"
            :to="`/ddt/${$route.params.departement}/collectivites/${$route.params.collectiviteId}/${$route.params.collectiviteId.length > 5 ? 'epci' : 'commune'}`"
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
</template>
<script>
import { mdiChevronLeft } from '@mdi/js'
export default {
  name: 'ProcedureAdd',
  layout: 'ddt',
  data () {
    return {
      collectivite: null,
      icons: { mdiChevronLeft }
    }
  },
  mounted () {
    fetch(`https://nuxt3.docurba.incubateur.net/api/geo/search/collectivites?code=${this.$route.params.collectiviteId}&populate=true`)
      .then(async (res) => {
        const collectivites = await res.json()
        this.collectivite = collectivites[0]
      })

    // this.collectivite = (await axios({
    //   url: `/api/geo/${this.$route.params.collectiviteId.length > 5 ? 'intercommunalites' : 'communes'}/${this.$route.params.collectiviteId}`,
    //   method: 'get'
    // })).data
  }
}
</script>
