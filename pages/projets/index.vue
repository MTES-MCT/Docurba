<template>
  <LayoutsCustomApp private>
    <v-container>
      <v-row>
        <v-col cols="12">
          <v-list>
            <ProjectsProjectListItem
              v-for="project in projects"
              :key="project.id"
              :project="project"
              shareable
              @share="shareProject(project)"
            />
          </v-list>
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12">
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
