<template>
  <v-form ref="form" v-model="valid">
    <v-row justify="center" align="center">
      <v-col cols="12" md="10">
        <VCollectivitesAutocomplete
          v-model="selectedCollectivite"
          :cols-dep="4"
          :cols-town="8"
          :input-props="{
            rules: [$rules.required]
          }"
        />
      </v-col>
      <v-col cols="auto" md="2">
        <v-btn
          depressed
          color="primary"
          :loading="searchLoading"
          @click="toPublicDashboard"
        >
          <v-icon class="mr-2" small>
            {{ icons.mdiMagnify }}
          </v-icon>
          Rechercher
        </v-btn>
      </v-col>
    </v-row>
  </v-form>
</template>

<script>
import { mdiMagnify } from '@mdi/js'

export default {
  data () {
    return {
      valid: false,
      selectedCollectivite: null,
      searchLoading: false,
      icons: {
        mdiMagnify
      }
    }
  },
  methods: {
    toPublicDashboard () {
      if (!this.valid) {
        this.$refs.form.validate()
      } else {
        const collectiviteId = this.selectedCollectivite.code

        this.$analytics({
          category: 'public',
          name: 'search',
          value: collectiviteId,
          data: {
            collectivite: this.selectedCollectivite
          }
        })

        this.$matomo([
          'trackEvent', 'Socle de PAC', 'Recherche',
          `${this.selectedCollectivite.departement} - ${this.selectedCollectivite.name}`
        ])

        this.$router.push({
          name: 'collectivites-collectiviteId',
          params: {
            collectiviteId: collectiviteId.toString().padStart(5, '0')
          },
          query: {
            isEpci: this.selectedCollectivite.type === 'epci'
          }
        })
      }
    }
  }
}
</script>
