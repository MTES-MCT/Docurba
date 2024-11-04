<template>
  <v-container>
    <v-row>
      <v-col cols="12" class="pb-0 mt-6">
        <nuxt-link :to="`/ddt/${$route.params.departement}/procedures`" class="text-decoration-none d-flex align-center">
          <v-icon color="primary" small class="mr-2">
            {{ icons.mdiChevronLeft }}
          </v-icon>
          Mes procédures
        </nuxt-link>
        <h1>Mes Procédures</h1>
      </v-col>
    </v-row>

    <v-row>
      <v-col v-if="!collectivites" cols="12">
        <v-skeleton-loader
          type="table"
        />
      </v-col>
      <v-col v-else cols="12">
        <v-data-table
          :headers="headers"
          :items="collectivites"
          :items-per-page="10"
          hide-default-header
          class="elevation-1 pa-8 choose-collectivites-dt"
          :custom-filter="customFilter"
          :search="search"
          :loading="!collectivites"
          loading-text="Chargement des collectivités..."
        >
          <template #top>
            <p>Choisissez la collectivité pour laquelle vous souhaitez créer cette procédure:</p>
            <div class="d-flex align-center justify-space-between ">
              <v-text-field
                v-model="search"
                outlined
                hide-details
                dense
                style="max-width:400px"
                label="Rechercher une collectivité..."
              />
            </div>
          </template>

          <!-- eslint-disable-next-line -->
          <template #item.name="{ item }">
            <div class="my-2">
              <a class="text-decoration-none font-weight-bold">
                {{ item.code }} {{ item.intitule }}
              </a>
            </div>
          </template>

          <!-- eslint-disable-next-line -->
          <template #item.actions="{ item }">
            <div class="my-2">
              <v-btn color="primary" depressed :to="`/ddt/${item.departementCode}/collectivites/${item.code}/procedure/add`">
                Choisir
              </v-btn>
            </div>
          </template>
        </v-data-table>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mdiChevronLeft } from '@mdi/js'
export default {
  name: 'ChooseCollectiviteAddProcedure',
  layout: 'ddt',
  data () {
    return {
      icons: {
        mdiChevronLeft
      },
      search: this.$route.query.search || '',
      collectivites: null
    }
  },
  computed: {
    headers () {
      return [
        { text: 'Nom', align: 'start', value: 'name', filterable: true },
        { text: 'Nom', align: 'end', value: 'actions' }
      ]
    }
  },
  mounted () {
    // TODO: this is using an API route from an other project.
    // It could use a wrapper to avoid having to re writte the base url all the time.
    fetch(`https://nuxt3.docurba.incubateur.net/api/geo/search/collectivites?departementCode=${this.$route.params.departement}`).then(async (res) => {
      this.collectivites = await res.json()
    })
  },
  methods: {
    customFilter (value, search, item) {
      if (!search?.length) { return true }
      const itemValue = item.intitule + item.code
      const normalizedValue = itemValue.toLocaleLowerCase().normalize('NFKD').replace(/\p{Diacritic}/gu, '')
      const normalizedSearch = search.toLocaleLowerCase().normalize('NFKD').replace(/\p{Diacritic}/gu, '')

      return normalizedValue.includes(normalizedSearch)
    }
  }
}
</script>

<style lang="scss">
.choose-collectivites-dt {
  tr th{
    font-size: 14px !important;
    color: #000 !important;
  }
   tbody tr td{
    vertical-align: middle !important;
   }
}

</style>
