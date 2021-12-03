<template>
  <LayoutsCustomApp drawer private>
    <template #drawer>
      <v-list>
        <v-list-item>
          <v-list-item-content>
            <v-list-item-title>Documents</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-list-item>
          <v-list-item-content>
            <v-list-item-title>PAC Templates</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </template>
    <v-container fluid>
      <v-row>
        <v-col cols="auto" class="pa-0" />
        <v-col cols="">
          <v-list>
            <ProjectsProjectListItem
              v-for="project in projects"
              :key="project.id"
              :project="project"
              shareable
              @share="shareProject(project)"
            />
          </v-list>
          <v-list>
            <ProjectsProjectListItem
              v-for="project in sharedProjects"
              :key="project.id"
              :project="project"
              shareable
              @share="shareProject(project)"
            />
          </v-list>
        </v-col>
      </v-row>
    </v-container>
  </LayoutsCustomApp>
</template>

<script>
import projectsList from '@/mixins/projectsList.js'

export default {
  mixins: [projectsList],
  layout: 'app'
}
</script>
