<template>
  <LayoutsCustomApp drawer private>
    <template #drawer>
      <v-list>
        <!-- <v-list-item>
          <v-list-item-content>
            <v-list-item-title>Projets</v-list-item-title>
          </v-list-item-content>
        </v-list-item> -->
        <v-list-item href="/projets/trames" nuxt>
          <v-list-item-icon>
            <v-icon>{{ icons.mdiFileDocumentEdit }}</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>Trame du PAC</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-list-item href="https://docs.google.com/document/d/1DMVFON6OUSaOomhoUnvHY5uHNkiVMTJlJ_dMpu9auv8/edit" target="_blank">
          <v-list-item-icon>
            <v-icon>{{ icons.mdiHelp }}</v-icon>
          </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>Guide d'utilisation</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </template>
    <v-container fluid>
      <v-row>
        <v-col cols="12">
          <v-toolbar flat>
            <v-text-field v-model="search" filled hide-details placeholder="Recherchez un projet" />
          </v-toolbar>
        </v-col>
      </v-row>
      <v-row class="mt-0">
        <v-col
          v-for="project in filteredProjects"
          :key="project.id"
          cols="12"
        >
          <ProjectsDashboardCard :project="project" />
          <!-- <v-list>
            <v-subheader>Mes projets</v-subheader>
            <ProjectsDdtProjectListItem
              v-for="project in filteredProjects"
              :key="project.id"
              :project="project"
              shareable
            />
          </v-list>
          <v-list>
            <v-subheader>Projets partagés avec moi</v-subheader>
            <ProjectsDdtProjectListItem
              v-for="project in filteredSharedProjects"
              :key="project.id"
              :project="project"
            />
          </v-list> -->
        </v-col>
      </v-row>
    </v-container>
    <v-dialog width="500px">
      <template #activator="{on}">
        <v-btn
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

export default {
  mixins: [projectsList],
  layout: 'app',
  data () {
    return {
      icons: {
        mdiPlus,
        mdiFileDocumentEdit,
        mdiHelp
      }
    }
  }
}
</script>
