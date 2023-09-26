<template>
  <v-row>
    <!-- TODO: Remettre la modal -->
    <!-- @insert="fetchProjects" -->
    <DashboardDUInsertDialog
      v-model="insertDialog"
      :collectivite="collectivite"
      @insert="$emit('inserted')"
    />
    <v-col v-if="procedures.length > 0 || emptyProjects.length > 0 || schemas.length > 0">
      <v-tabs
        v-model="tab"
        background-color="primary"
        dark
      >
        <v-tab v-if="isEpci">
          DU intercommunaux
        </v-tab>
        <v-tab>
          DU communaux
        </v-tab>
        <v-tab>
          SCoTs
        </v-tab>
        <v-spacer />
        <v-btn v-if="!isPublic" text class="align-self-center" @click="insertDialog = true">
          Ajouter un DU
        </v-btn>
      </v-tabs>

      <v-tabs-items v-model="tab" :class="{beige: !isPublic}">
        <v-tab-item v-if="isEpci">
          <template v-if="emptyProjectsInter.length > 0 || DUInter.length > 0">
            <DashboardEmptyProjectCard
              v-for="emptyProject in emptyProjectsInter"
              :key="emptyProject.id"
              :project="emptyProject"
              class="mb-4"
            />
            <DashboardDUItem
              v-for="(procedure,i) in DUInter"
              :key="'du_' + i"
              :procedure="procedure"
              :censored="isPublic"
            />
          </template>
          <div v-else class="d-flex align-center justify-center pa-8 text--disabled flex-column g200  rounded">
            <p class="text-h1 mb-7">
              :'(
            </p>
            <p class="font-weight-bold">
              Pas de documents d'urbanisme Intercommunaux
            </p>
            <span class="font-italic">Astuce: Si vous ne voyez pas le document d'urbanisme recherché, vérifiez sur la commune ou l'EPCI qui à la compétence.</span>
          </div>
        </v-tab-item>
        <v-tab-item>
          <template v-if="emptyProjectsInter.length > 0 || DUInter.length > 0">
            <DashboardEmptyProjectCard
              v-for="emptyProject in emptyProjectsCommunaux"
              :key="emptyProject.id"
              :project="emptyProject"
              class="mb-4"
            />
            <DashboardDUItem
              v-for="(procedure,i) in DUCommunaux"
              :key="'du_' + i"
              :procedure="procedure"
              :censored="isPublic"
            />
          </template>
          <div v-else class="d-flex align-center justify-center pa-8 text--disabled flex-column g200  rounded">
            <p class="text-h1 mb-7">
              :'(
            </p>
            <p class="font-weight-bold">
              Pas de documents en compétence communal
            </p>
            <span class="font-italic">Astuce: Si vous ne voyez pas le document d'urbanisme recherché, vérifiez sur la commune ou l'EPCI qui à la compétence.</span>
          </div>
        </v-tab-item>
        <v-tab-item>
          <DashboardEmptyProjectCard
            v-for="emptyProject in emptyProjectsCommunaux"
            :key="emptyProject.id"
            :project="emptyProject"
            class="mb-4"
          />
          <DashboardDUItem
            v-for="(procedure,i) in schemas"
            :key="'du_' + i"
            :procedure="procedure"
            :censored="isPublic"
          />
        </v-tab-item>
      </v-tabs-items>
    </v-col>
    <v-col v-else-if="isLoaded && procedures.length === 0 && emptyProjects.length === 0" cols="12">
      <div class="text--secondary beige pa-6 mb-12 rounded">
        Cette collectivité n'a pas de documents d'urbanisme sous sa compétence.
      </div>

      <v-btn v-if="!isPublic" tile color="primary" @click="insertDialog = true">
        Ajouter un document d'urbanisme
      </v-btn>
    </v-col>
    <v-col v-else cols="12">
      <VGlobalLoader />
    </v-col>
  </v-row>
</template>

<script>
export default {
  name: 'DUItemsList',
  props: {
    collectivite: {
      type: Object,
      required: true
    },
    procedures: {
      type: Array,
      default () { return [] }
    },
    projects: {
      type: Array,
      default () { return [] }
    },
    schemas: {
      type: Array,
      default: () => null
    },
    isPublic: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      loadingProcedures: true,
      tab: null,
      insertDialog: false
    }
  },
  computed: {
    isLoaded () {
      return !!this.procedures && !!this.projects && !!this.collectivite
    },
    isEpci () {
      return this.collectivite.type !== 'Commune'
    },
    DUCommunaux () {
      if (this.isEpci) {
        return this.procedures?.filter(e => e.perimetre.length === 1)
      } else { return this.procedures }
    },
    DUInter () {
      return this.procedures?.filter(e => e.perimetre.length > 1)
    },
    emptyProjects () {
      if (!this.projects) { return [] }

      return this.projects.filter(project => !project.procedures.length)
    },
    emptyProjectsInter () {
      return this.emptyProjects?.filter(project => project.collectivite_id.length === 9)
    },
    emptyProjectsCommunaux () {
      return this.emptyProjects?.filter(project => project.collectivite_id.length !== 9)
    }
  }
}
</script>
