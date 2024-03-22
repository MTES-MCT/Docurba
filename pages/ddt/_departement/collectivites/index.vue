<template>
  <v-container v-if="collectivites">
    <v-row>
      <v-col v-if="!clickedOnDocLink" cols="12">
        <v-alert type="info">
          Zoom sur les dernières améliorations des fonctionnalités de Docurba.
          <a
            class="white--text"
            href="https://pad.incubateur.net/FUz6ITnHSC6wVv1rvIipyg?view"
            target="_blank"
            @click="showClose"
          >Découvrez la documentation</a>
        </v-alert>
      </v-col>
      <v-col cols="12">
        <h1>Mes collectivités - {{ $route.params.departement }}</h1>
      </v-col>
      <v-col cols="12">
        <v-data-table
          :headers="headers"
          :items="collectivites"
          :items-per-page="10"
          class="elevation-1 pa-8"
          :custom-filter="customFilter"
          :search="search"
          :loading="!collectivites"
          loading-text="Chargement des collectivités..."
        >
          <template #top>
            <div class="d-flex  align-center justify-space-between">
              <v-select
                v-model="selectedCollectiviteTypesFilter"
                flat
                background-color="alt-beige"
                hide-details
                solo
                multiple
                dense
                :items="collectiviteTypeFilterItems"
                style="max-width:350px"
              >
                <template #selection="{item, index}">
                  <div v-if="collectiviteTypeFilterItems.length === selectedCollectiviteTypesFilter.length && index === 0">
                    Tous types de collectivité
                  </div>
                  <span v-else-if="collectiviteTypeFilterItems.length !== selectedCollectiviteTypesFilter.length">
                    {{ item.text }}<span v-if="index !== selectedCollectiviteTypesFilter.length - 1">,&nbsp;</span>
                  </span>
                </template>
              </v-select>
              <v-spacer />
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
            <span>{{ item.code }} {{ item.intitule }}</span>
          </template>
          <!-- eslint-disable-next-line -->
            <template #item.procedures="{ item }">
            <div v-for="plan in item.plans" :key="plan.id">
              {{ plan.doc_type }} &nbsp;
              {{ plan.id }}
            </div>
          </template>
          <!-- eslint-disable-next-line -->
          <template #item.scots="{ item }">
            <div v-for="scot in item.scots" :key="scot.id">
              {{ scot.doc_type }} &nbsp;
              {{ scot.id }}
            </div>
          </template>
        </v-data-table>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { groupBy, filter } from 'lodash'
const docVersion = '1.0'
export default {
  name: 'CollectiviteDU',
  layout: 'ddt',
  data () {
    return {
      selectedCollectiviteTypesFilter: ['COM', 'CA', 'CC', 'EPT', 'SM', 'SIVU', 'PETR'],
      collectiviteTypeFilterItems: [
        { text: 'Communes', value: 'COM' },
        { text: 'CA', value: 'CA' },
        { text: 'CC', value: 'CC' },
        { text: 'EPT', value: 'EPT' },
        { text: 'SM', value: 'SM' },
        { text: 'SIVU', value: 'SIVU' },
        { text: 'PETR', value: 'PETR' }
      ],
      search: this.$route.query.search || '',
      referentiel: null,
      clickedOnDocLink: true
    }
  },
  computed: {
    headers () {
      return [
        { text: 'Nom', align: 'start', value: 'name', filterable: true },
        { text: 'Type', align: 'start', value: 'type', filterable: true },
        { text: 'Procédures', value: 'procedures', filterable: false },
        { text: 'SCOTs', value: 'scots', filterable: false }
      ]
    },
    collectivites () {
      return this.referentiel?.filter(e => this.selectedCollectiviteTypesFilter.includes(e.type))
    }
  },
  async mounted () {
    const rawProcedures = this.$urbanisator.getProceduresByCommunes(this.$route.params.departement)
    const rawReferentiel = fetch(`/api/geo/collectivites?departements=${this.$route.params.departement}`)

    const [procedures, referentiel] = await Promise.all([rawProcedures, rawReferentiel])
    const { communes, groupements } = await referentiel.json()
    // TODO: Faire la meme chose sur les SCoTs
    const enrichedGroups = groupements.map((groupement) => {
      const proceduresGroupement = groupement.membres.map(membre => procedures[membre.code]?.plans).flat().filter(e => e)
      const perimetre = groupBy(proceduresGroupement, e => e.procedure_id)
      const proceduresPerimInter = filter(perimetre, e => e.length > 1)
      const proceduresInter = proceduresPerimInter.map(e => e?.[0].procedures_duplicate)
      return { ...groupement, plans: proceduresInter }
    })

    const enrichedCommunes = communes.map(e => ({
      ...e,
      plans: procedures[e.code]?.plans.map(y => y.procedures_duplicate),
      scots: procedures[e.code]?.scots.map(y => y.procedures_duplicate)
    }))
    const flattenReferentiel = [...enrichedGroups, ...enrichedCommunes]
    this.referentiel = flattenReferentiel
  },
  methods: {
    customFilter (value, search, item) {
      if (!search?.length || !value?.length) { return true }

      const normalizedValue = value.toLocaleLowerCase().normalize('NFKD').replace(/\p{Diacritic}/gu, '')
      const normalizedSearch = search.toLocaleLowerCase().normalize('NFKD').replace(/\p{Diacritic}/gu, '')

      return normalizedValue.includes(normalizedSearch)
    },
    showClose () {
      this.clickedOnDocLink = true
      localStorage.setItem('docVersion', docVersion)
    }
  }
}
</script>
<style lang="scss">
.competence-tag-sudocu{
  background: #FEECC2;
  border-radius: 4px;
  text-transform: uppercase;
  color: #716043;
  font-family: 'Marianne';
  font-style: normal;
  font-weight: 700;
  font-size: 14px;
  line-height: 24px;
  padding: 0px 8px;
}

.competence-tag-banatic{
  background: var(--v-primary-base);
  border-radius: 4px;
  text-transform: uppercase;
  color: var(--v-primary-lighten1);
  font-family: 'Marianne';
  font-style: normal;
  font-weight: 700;
  font-size: 14px;
  line-height: 24px;
  padding: 0px 8px;
}

</style>
