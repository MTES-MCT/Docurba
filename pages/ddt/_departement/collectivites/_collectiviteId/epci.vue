<template>
  <v-container v-if="collectivite">
    <v-row>
      <v-col cols="12">
        <h1 class="text-h1">
          {{ collectivite.name }}
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
              <h3>{{ collectivite.towns?.length }} communes dans votre EPCI</h3>
            </v-expansion-panel-header>
            <v-expansion-panel-content>
              <v-container>
                <v-row>
                  <v-col
                    v-for="town in collectivite.towns"
                    :key="town.code_commune_INSEE"
                    cols="4"
                    class="pt-0 pl-0"
                  >
                    <nuxt-link :to="{ name: 'ddt-departement-collectivites-collectiviteId-commune', params: { departement: $route.params.departement, collectiviteId: town.code_commune_INSEE }}">
                      {{ town.nom_commune }} ({{ town.code_commune_INSEE }})
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
    <v-row v-if="procedures && procedures.length > 0">
      <v-col>
        <v-tabs
          v-model="tab"
          background-color="primary"
          dark
        >
          <v-tab>
            DU intercommunaux
          </v-tab>
          <v-tab>
            DU communaux
          </v-tab>
        </v-tabs>

        <v-tabs-items v-model="tab" class="beige">
          <v-tab-item>
            <DashboardDUItem
              v-for="(procedure,i) in DUInter"
              :key="'du_' + i"
              :procedure="procedure"
            />
          </v-tab-item>
          <v-tab-item>
            <DashboardDUItem
              v-for="(procedure,i) in DUCommunaux"
              :key="'du_' + i"
              :procedure="procedure"
            />
          </v-tab-item>
        </v-tabs-items>
      </v-col>
    </v-row>
    <v-row v-else-if="procedures && procedures.length === 0">
      <v-col cols="12">
        <div class="text--secondary beige pa-6 mb-12 rounded">
          Cette collectivité n'a pas de documents d'urbanisme sous ca compétence.
        </div>
      </v-col>
    </v-row>
    <v-row v-else>
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
      tab: null,
      collectivite: null,
      procedures: null,
      icons: {
        mdiArrowLeft
      }
    }
  },
  computed: {
    DUCommunaux () {
      return this.procedures?.filter(e => e.perimetre.length === 1)
    },
    DUInter () {
      return this.procedures?.filter(e => e.perimetre.length > 1)
    }
  },

  async mounted () {
    this.collectivite = await this.$sudocu.getCurrentCollectivite(this.$route.params.collectiviteId, 'epci')
    this.procedures = await this.$sudocu.getProcedures(this.collectivite, 'epci')
  }
}
</script>

<style lang="scss">
.border-light{
  border: solid 1px var(--v-primary-lighten1) !important;
}
</style>
