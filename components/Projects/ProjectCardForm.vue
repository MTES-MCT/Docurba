<template>
  <v-card>
    <v-card-title><slot name="titre" /></v-card-title>
    <v-card-text v-if="userDeptCode">
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
      <v-btn v-if="!project.id" color="primary" :loading="loading" @click="upsertProject">
        Créer
      </v-btn>
      <v-btn v-else color="primary" :loading="loading" @click="upsertProject">
        Modifier
      </v-btn>
      <v-btn color="primary" outlined @click="$emit('cancel')">
        Annuler
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
import regions from '@/assets/data/Regions.json'

export default {
  props: {
    project: {
      type: Object,
      default () {
        return {
          name: '',
          docType: '',
          PAC: [],
          owner: this.$user.id
        }
      }
    }
  },
  data () {
    return {
      PAC: [],
      newProjectTown: this.project.town,
      newProject: Object.assign({}, this.project),
      userDeptCode: null,
      loading: false
    }
  },
  async mounted () {
    const PAC = await this.$content('PAC', {
      deep: true,
      text: true
    }).fetch()

    this.PAC = PAC

    // TODO: This part is the same in the page trames.vue and coul be made into a mixin.
    // The only change is that this this page does not need to parse a body to be rendered.
    const { data: adminAccess } = await this.$supabase.from('admin_users_dept').select('dept').match({
      user_id: this.$user.id,
      user_email: this.$user.email,
      role: 'ddt'
    })

    this.userDeptCode = adminAccess[0].dept

    const { data: deptSections } = await this.$supabase.from('pac_sections_dept').select('*').eq('dept', this.userDeptCode)

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
    createOrUpdate (savedProject) {
      if (savedProject.id) {
        return this.$supabase.from('projects').upsert(savedProject)
      } else {
        return this.$supabase.from('projects').insert([savedProject])
      }
    },
    async upsertProject () {
      this.loading = true

      this.newProject.PAC = this.newProject.PAC.length ? this.newProject.PAC : this.PAC.map(s => s.path)

      const savedProject = Object.assign({
        town: this.newProjectTown,
        region: regions.find(r => r.name === this.newProjectTown.nom_region).iso
      }, this.newProject)

      const { data, err } = await this.createOrUpdate(savedProject)

      if (!err && data) {
        if (!savedProject.id) {
          this.$router.push(`/projets/${savedProject.id || data[0].id}/content`)
        } else {
          this.$emit('cancel')
        }
      } else {
        // eslint-disable-next-line no-console
        console.log('err creating project', data, err)
      }

      this.loading = false
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
