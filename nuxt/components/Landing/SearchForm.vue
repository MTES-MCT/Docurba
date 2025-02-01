<template>
  <v-form ref="form" v-model="valid">
    <v-container fluid :style="{ padding: 0 }">
      <v-row>
        <v-col cols="12" md="10">
          <VCollectivitesAutocomplete
            v-model="selectedCollectivite"
            :cols-dep="4"
            :cols-town="8"
            :input-props="{
              rules: [$rules.required],
              outlined: true,
              style: {
                background: '#fff'
              }
            }"
          />
        </v-col>
        <v-col cols="12" md="2">
          <v-btn
            :style="{ width: '100%', height: '2.5rem' }"
            depressed
            color="primary"
            :loading="searchLoading"
            @click="toPublicDashboard"
          >
            Accéder
          </v-btn>
        </v-col>
      </v-row>
    </v-container>
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
