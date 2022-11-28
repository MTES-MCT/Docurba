<template>
  <LayoutsCustomApp private extended-app-bar>
    <template #headerExtension>
      <v-tabs v-if="!loadingAccess" show-arrows>
        <v-tab
          :to="{path: '/projets'}"
          nuxt
        >
          Projets
        </v-tab>
        <v-tab
          :to="{path: '/projets/trames/departement'}"
          nuxt
        >
          Trame du {{ deptAccess.dept }}
        </v-tab>
        <v-tab
          v-for="region in regions"
          :key="region.iso"
          :to="{path: `/projets/trames/regions/${region.code}`}"
        >
          Trame {{ region.iso }}
        </v-tab>
      </v-tabs>
      <v-spacer />
      <v-btn
        depressed
        tile
        :to="{name: 'guide'}"
        text
      >
        Guide d'utilisation
      </v-btn>
    </template>
    <v-container v-if="projectListLoaded">
      <v-row>
        <v-col cols="12">
          <!-- <v-toolbar flat> -->
          <v-text-field v-model="search" filled hide-details placeholder="Recherchez un projet" />
          <!-- </v-toolbar> -->
        </v-col>
      </v-row>
      <v-row class="mt-0">
        <v-col>
          <h3 class="text-h3">
            Vos projets
          </h3>
        </v-col>
        <template v-if="projects.length">
          <v-col
            v-for="project in filteredProjects"
            :key="`${project.id}-owned`"
            cols="12"
          >
            <ProjectsDashboardCard :project="project" />
          </v-col>
        </template>
        <v-col v-else cols="12" class="text-center">
          <h3 class="text-h3 text--secondary mb-4">
            Vous n'avez pas encore de projet
          </h3>
          <v-btn color="primary" depressed tile @click="projectDialog = true">
            Créer un projet
          </v-btn>
        </v-col>
        <template v-if="sharedProjects.length">
          <v-col>
            <h3 class="text-h3">
              Projets partagés avec vous
            </h3>
          </v-col>
          <v-col
            v-for="sharing in filteredSharings"
            :key="`${sharing.project.id}-shared`"
            cols="12"
          >
            <ProjectsDashboardCard :project="sharing.project" :sharing="sharing" />
          </v-col>
        </template>
      </v-row>
    </v-container>
    <VGlobalLoader v-else />
    <v-dialog v-model="projectDialog" width="500px">
      <template #activator="{on}">
        <v-btn
          depressed
          fixed
          bottom
          right
          fab
          color="primary"
          v-on="on"
        >
          <v-icon>{{ icons.mdiPlus }}</v-icon>
        </v-btn>
      </template>
      <template #default="dialog">
        <ProjectsProjectCardForm @cancel="dialog.value = false">
          <template #titre>
            Creer un projet
          </template>
        </ProjectsProjectCardForm>
      </template>
    </v-dialog>
  </LayoutsCustomApp>
</template>

<script>
import { mdiPlus, mdiFileDocumentEdit, mdiHelp } from '@mdi/js'
import projectsList from '@/mixins/projectsList.js'

import regions from '@/assets/data/Regions.json'

export default {
  mixins: [projectsList],
  layout: 'app',
  data () {
    return {
      icons: {
        mdiPlus,
        mdiFileDocumentEdit,
        mdiHelp
      },
      projectsSubscription: null,
      projectDialog: false,
      loadingAccess: true
    }
  },
  computed: {
    regions () {
      return this.regionAccess.map((access) => {
        // eslint-disable-next-line eqeqeq
        return regions.find(r => r.code == access.region)
      })
    }
  },
  watch: {
    projectListLoaded () {
      if (this.projectListLoaded) {
        // const projectsIds = this.projects.map(p => p.id)

        this.projectsSubscription = this.$supabase
          .channel('public:projects')
          .on('postgres_changes', { event: 'UPDATE', schema: 'public', table: 'projects', filter: `owner=eq.${this.$user.id}` }, (payload) => {
            const updatedProject = payload.new

            if (updatedProject.archived) {
              const projectIndex = this.projects.findIndex(p => p.id === updatedProject.id)
              this.projects.splice(projectIndex, 1)
            }
          })
          .subscribe()
      }
    }
  },
  async mounted () {
    const [regionAccess, deptAccess] = await Promise.all([
      this.$auth.getRegionAccess(true),
      this.$auth.getDeptAccess()
    ])

    this.regionAccess = regionAccess
    this.deptAccess = deptAccess
    this.loadingAccess = false
  },
  beforeDestroy () {
    if (this.projectsSubscription) {
      this.$supabase.removeChannel(this.projectsSubscription)
    }
  }
}
</script>
