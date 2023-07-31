<template>
  <v-row v-if="procedures.length > 0 || emptyProjects.length > 0">
    <v-col>
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
        <v-spacer />
        <DashboardDUInsertDialog v-if="!isPublic" :collectivite="collectivite" />
      </v-tabs>

      <v-tabs-items v-model="tab" :class="{beige: !isPublic}">
        <v-tab-item v-if="isEpci">
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
        </v-tab-item>
        <v-tab-item>
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
        </v-tab-item>
      </v-tabs-items>
    </v-col>
  </v-row>
  <v-row v-else-if="!loadingProcedures && procedures.length === 0 && emptyProjects.length === 0">
    <v-col cols="12">
      <div class="text--secondary beige pa-6 mb-12 rounded">
        Cette collectivité n'a pas de documents d'urbanisme sous ca compétence.
      </div>
    </v-col>
    <v-col v-if="!isPublic" cols="auto">
      <DashboardDUInsertDialog v-model="insertDialog" :collectivite="collectivite">
        <v-btn tile color="primary" @click="insertDialog = true">
          Ajouter un document d'urbanisme
        </v-btn>
      </DashboardDUInsertDialog>
    </v-col>
  </v-row>
  <v-row v-else>
    <v-col cols="12">
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
    collectiviteType: {
      type: String,
      default: () => null
    },
    isPublic: {
      type: Boolean,
      default: () => false
    }
  },
  data () {
    return {
      loadingProcedures: true,
      tab: null,
      insertDialog: false,
      procedures: [],
      projects: []
    }
  },
  computed: {
    isEpci () {
      return this.collectiviteType === 'epci'
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
      return this.projects.filter(project => !project.procedures.length)
    },
    emptyProjectsInter () {
      return this.emptyProjects.filter(project => project.collectivite_id.length === 9)
    },
    emptyProjectsCommunaux () {
      return this.emptyProjects.filter(project => project.collectivite_id.length !== 9)
    }
  },
  async mounted () {
    const [sudocuProcedures, { procedures, projects }] = await Promise.all([
      this.$sudocu.getProcedures(this.collectivite.id),
      !this.isPublic ? this.$urbanisator.getProjectsProcedures(this.collectivite.id) : { projects: [], procedures: [] }
    ])

    this.procedures = [...sudocuProcedures, ...procedures]
    this.projects = projects

    this.loadingProcedures = false
  }
}
</script>
