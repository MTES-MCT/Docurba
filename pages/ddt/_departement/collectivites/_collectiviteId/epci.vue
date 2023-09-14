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
              <h3>{{ collectivite.communes?.length }} communes dans votre EPCI</h3>
            </v-expansion-panel-header>
            <v-expansion-panel-content>
              <v-container>
                <v-row>
                  <v-col
                    v-for="town in collectivite.communes"
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
    <v-row>
      <v-col cols="12">
        <p class="text-h2">
          Documents d'urbanisme
        </p>
        <p class="text-h6">
          Documents d’urbanisme disponibles pour la commune recherchée :
        </p>
      </v-col>
    </v-row>
    <DashboardDUItemsList
      collectivite-type="epci"
      :collectivite="collectivite"
      :procedures="procedures"
      :projects="projects"
      @inserted="fetchProjects"
    />
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
      linkedEpci: null,
      collectivite: null,
      projects: [],
      sudocuProcedures: null,
      procedures: [],
      icons: {
        mdiArrowLeft
      }
    }
  },
  async mounted () {
    const collectiviteProcedures = await this.$sudocu.getProceduresCollectivite(this.$route.params.collectiviteId)
    this.sudocuProcedures = collectiviteProcedures.procedures
    this.collectivite = collectiviteProcedures.collectivite

    const { procedures, projects } = await this.$urbanisator.getProjectsProcedures(this.collectivite.code)
    this.procedures = [...collectiviteProcedures.procedures, ...procedures]
    this.projects = projects
  },
  methods: {
    async fetchProjects () {
      const { procedures, projects } = await this.$urbanisator.getProjectsProcedures(this.collectivite.code)
      this.procedures = [...this.sudocuProcedures, ...procedures]
      this.projects = projects
    }
  }
}
</script>
