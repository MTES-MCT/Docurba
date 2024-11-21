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
  mounted () {
    fetch(`https://nuxt3.docurba.incubateur.net/api/geo/search/collectivites?code=${this.$route.params.collectiviteId}`)
      .then(async (res) => {
        const collectivites = await res.json()
        this.collectivite = collectivites[0]
      })

    if (this.$user.profile?.side === 'etat') {
      if (this.$user.profile?.departement !== this.collectivite.departementCode) {
        this.$router.push(`/collectivites/${this.$route.params.collectiviteId}`)
      }
    } else if (this.$user.profile?.collectivite_id !== this.collectivite.code &&
          this.$user.profile?.collectivite_id !== this.collectivite.intercommunaliteCode) {
      this.$router.push(`/collectivites/${this.$route.params.collectiviteId}`)
    }
  }
}
</script>
