<template>
  <LayoutsCustomApp drawer private>
    <template #drawer>
      <v-list>
        <v-list-item>
          <v-list-item-content>
            <v-list-item-title>Projets</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-list-item href="/projets/trames">
          <v-list-item-content>
            <v-list-item-title>Trame du PAC</v-list-item-title>
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
        <v-col cols="">
          <v-list>
            <ProjectsProjectListItem
              v-for="project in filteredProjects"
              :key="project.id"
              :project="project"
              shareable
              @share="shareProject(project)"
            />
          </v-list>
          <v-list>
            <ProjectsProjectListItem
              v-for="project in filteredSharedProjects"
              :key="project.id"
              :project="project"
              shareable
              @share="shareProject(project)"
            />
          </v-list>
        </v-col>
      </v-row>
    </v-container>
    <v-dialog v-if="userDeptCode" width="500px">
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
        <v-card>
          <v-card-title>Créer un nouveau projet</v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12">
                <v-text-field v-model="newProject.name" filled hide-details placeholder="Nom du projet" />
              </v-col>
              <v-col cols="12">
                <VDocumentSelect v-model="newProject.docType" />
              </v-col>
              <v-col cols="12">
                <VTownAutocomplete v-model="newProjectTown" :default-departement-code="userDeptCode" hide-dept />
              </v-col>
              <v-col cols="12" class="tree-view">
                <PACTreeviewSelection v-model="newProject.PAC" :pac-data="PAC" />
              </v-col>
            </v-row>
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn color="primary" :loading="loading" @click="createProject">
              Créer
            </v-btn>
            <v-btn color="primary" outlined @click="dialog.value = false">
              Annuler
            </v-btn>
          </v-card-actions>
        </v-card>
      </template>
    </v-dialog>
  </LayoutsCustomApp>
</template>

<script>
import { mdiPlus } from '@mdi/js'
import projectsList from '@/mixins/projectsList.js'

import regions from '@/assets/data/Regions.json'

export default {
  mixins: [projectsList],
  layout: 'app',
  async asyncData ({ $content }) {
    const PAC = await $content('PAC', {
      deep: true,
      text: true
    }).fetch()

    return {
      PAC
    }
  },
  data () {
    return {
      icons: {
        mdiPlus
      },
      newProject: this.getNewProject(),
      newProjectTown: null,
      userDeptCode: null,
      loading: false
    }
  },
  async mounted () {
    // TODO: This part is the same in the page trames.vue and coul be made into a mixin.
    // The only change is that this this page does not need to parse a body to be rendered.
    const { data: adminAccess } = await this.$supabase.from('admin_users_dept').select('dept').match({
      user_id: this.$user.id,
      user_email: this.$user.email,
      role: 'ddt'
    })

    this.userDeptCode = adminAccess[0].dept

    const { data: deptSections } = await this.$supabase.from('pac_sections_dept').select('*').eq('dept', this.departementCode)

    deptSections.forEach((section) => {
      const sectionIndex = this.PAC.findIndex(s => s.path === section.path)

      if (sectionIndex >= 0) {
        // The Object Assign here is to keep the order since it's not saved. As could be other properties.
        // Although it might create inconsistenties for versions that get Archived later on.
        this.PAC[sectionIndex] = Object.assign({}, this.PAC[sectionIndex], section)
      } else {
        this.PAC.push(Object.assign({}, section))
      }
    })
  },
  methods: {
    getNewProject () {
      return {
        name: '',
        docType: '',
        PAC: [],
        owner: this.$user.id
      }
    },
    async createProject () {
      this.loading = true

      this.newProject.PAC = this.newProject.PAC.length ? this.newProject.PAC : this.PAC.map(s => s.path)

      const { data, err } = await this.$supabase.from('projects').insert([Object.assign({
        town: this.newProjectTown,
        region: regions.find(r => r.name === this.newProjectTown.nom_region).iso
      }, this.newProject)])

      if (!err && data) {
        this.$router.push(`/projets/${data[0].id}/content`)
      } else {
        // eslint-disable-next-line no-console
        console.log('err creating project', data, err)
      }
    }
  }
}
</script>

<style scoped>
.tree-view {
  max-height: 400px;
  overflow: scroll;
}
</style>
