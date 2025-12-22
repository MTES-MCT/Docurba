<template>
  <v-container v-if="collectivite">
    <v-row>
      <v-col cols="12">
        <h1 class="text-h1">
          {{ collectivite.intitule }}
        </h1>
      </v-col>
      <v-col cols="12">
        <div class="d-flex">
          <nuxt-link

            :to="{ name: 'ddt-departement-collectivites', params: { departement: $route.params.departement }}"
          >
            <v-icon small color="primary" class="mr-2">
              {{ icons.mdiArrowLeft }}
            </v-icon>
            <span>Revenir à mon tableau de bord</span>
          </nuxt-link>
        </div>
      </v-col>
      <v-col cols="12">
        <v-expansion-panels flat>
          <v-expansion-panel class="border-light">
            <v-expansion-panel-header>
              <h3>{{ collectivite.membres?.length }} membres dans cet EPCI</h3>
            </v-expansion-panel-header>
            <v-expansion-panel-content>
              <v-container>
                <v-row>
                  <v-col
                    v-for="town in collectivite.membres"
                    :key="town.code"
                    cols="4"
                    class="pt-0 pl-0"
                  >
                    <nuxt-link :to="{ name: 'ddt-departement-collectivites-collectiviteId-commune', params: { departement: $route.params.departement, collectiviteId: town.code }}">
                      {{ town.intitule }} ({{ town.code }})
                    </nuxt-link>
                    <v-divider class="mt-3" />
                  </v-col>
                </v-row>
              </v-container>
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-col>
    </v-row>
    <template v-if="loaded">
      <v-row>
        <v-col cols="12">
          <v-alert type="info">
            Le dernier import dans Docurba des événements en provenance de Sudocuh a été réalisé le 16 décembre.
            Si vous n'êtes pas d'accord avec les informations présentes, utilisez le bouton « Signaler un problème ».
          </v-alert>
        </v-col>
        <v-col cols="12" class="d-flex justify-space-between">
          <p class="text-h2">
            Documents d'urbanisme
          </p>
          <SignalementProbleme />
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <p class="text-h6">
            Documents d’urbanisme sous la compétence de {{ collectivite.intitule }} :
          </p>
        </v-col>
      </v-row>
      <DashboardDUItemsList
        collectivite-type="epci"
        :collectivite="collectivite"
        :procedures="plans"
        :projects="projects"
        :schemas="schemas"
        @deleteProcedure="getProcedures"
      />
    </template>
    <v-row v-else>
      <v-col cols="12">
        <VGlobalLoader />
      </v-col>
    </v-row>
  </v-container>
  <v-container v-else>
    <v-row>
      <v-col cols="12">
        <VGlobalLoader />
      </v-col>
    </v-row>
  </v-container>
</template>
<script>
import { mdiArrowLeft } from '@mdi/js'

export default {
  name: 'Collectivite',
  layout: 'ddt',
  data () {
    return {
      loaded: false,
      collectivite: null,
      projects: [],
      plans: [],
      schemas: [],
      icons: {
        mdiArrowLeft
      }
    }
  },
  async mounted () {
    await this.getProcedures()
    this.loaded = true
  },
  methods: {
    async getProcedures () {
      const response = await fetch(`/pour_nuxt/collectivite/${this.$route.params.collectiviteId}/`)
      const json = await response.json()
      this.collectivite = json.collectivite
      this.schemas = json.schemas
      this.plans = json.plans
    }
  }
}
</script>
