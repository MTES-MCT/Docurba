<template>
  <v-card>
    <v-card-title>
      <slot name="title" />
    </v-card-title>
    <v-card-text v-if="userDeptCode">
      <v-row>
        <v-col cols="12">
          <v-text-field v-model="newProject.name" filled hide-details placeholder="Nom du projet" />
        </v-col>
        <v-col cols="12">
          <VDocumentSelect v-model="newProject.doc_type" />
        </v-col>
        <v-col v-if="newProject.doc_type.includes('i') && EPCIs.length" cols="12">
          <VEpciAutocomplete v-model="projectForm.epci" :epci-list="EPCIs" />
        </v-col>
        <v-col v-else cols="12">
          <VTownAutocomplete v-model="projectForm.town" :default-departement-code="userDeptCode" hide-dept />
        </v-col>
        <v-col cols="12">
          <v-switch v-model="projectForm.useTrame" :label="`Utiliser la trame de PAC du ${userDeptCode}`" />
        </v-col>
        <!-- <v-col cols="12" class="tree-view">
          <PACTreeviewSelection v-model="newProject.PAC" :pac-data="PAC" />
        </v-col> -->
        <v-col v-if="error" cols="12">
          <span class="error--text">Echec de sauvegarde, veuillz réessayer ultérieurement.</span>
        </v-col>
      </v-row>
    </v-card-text>
    <v-card-actions>
      <v-btn depressed tile outlined color="secondary" @click="archiveProject">
        Archiver
      </v-btn>
      <v-spacer />
      <v-btn
        v-if="!project.id"
        depressed
        tile
        color="primary"
        :loading="loading"
        @click="upsertProject"
      >
        Créer
      </v-btn>
      <v-btn
        v-else
        depressed
        tile
        color="primary"
        :loading="loading"
        @click="upsertProject"
      >
        Modifier
      </v-btn>
      <v-btn depressed tile color="primary" outlined @click="$emit('cancel')">
        Annuler
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
import axios from 'axios'
import regions from '@/assets/data/Regions.json'
import unifiedPac from '@/mixins/unifiedPac.js'

export default {
  mixins: [unifiedPac],
  props: {
    project: {
      type: Object,
      default () {
        return {
          name: '',
          doc_type: '',
          PAC: [],
          owner: this.$user.id
        }
      }
    }
  },
  data () {
    return {
      PAC: [],
      projectForm: {
        useTrame: this.project.id ? !!this.project.trame : true,
        epci: this.project.epci,
        town: this.project.towns ? this.project.towns[0] : null
      },
      newProject: Object.assign({}, this.project),
      userDeptCode: null,
      EPCIs: [],
      loading: false,
      error: null
    }
  },
  async mounted () {
    await this.initPAC()

    const EPCIs = (await axios({
      method: 'get',
      url: `/api/epci?departement=${this.userDeptCode}`
    })).data

    this.EPCIs = EPCIs
  },
  methods: {
    async initPAC () {
      const PAC = await this.$content('PAC', {
        deep: true,
        text: true
      }).fetch()

      this.PAC = PAC

      const { data: adminAccess } = await this.$supabase.from('admin_users_dept').select('dept').match({
        user_id: this.$user.id,
        user_email: this.$user.email,
        role: 'ddt'
      })

      this.userDeptCode = adminAccess[0].dept

      const { data: deptSections } = await this.$supabase.from('pac_sections_dept').select('*').eq('dept', this.userDeptCode)
      this.PAC = this.unifyPacs([deptSections, this.PAC])
    },
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

      const isEpci = this.newProject.doc_type.includes('i')

      const savedProject = Object.assign({}, this.newProject, {
        epci: isEpci ? this.projectForm.epci : null,
        towns: isEpci ? this.projectForm.epci.towns : [this.projectForm.town],
        region: this.getRegion(isEpci),
        trame: this.projectForm.useTrame ? (this.project.trame || this.userDeptCode) : ''
      })

      const { data, err } = await this.createOrUpdate(savedProject)

      if (!err && data) {
        if (!savedProject.id) {
          this.$router.push(`/ddt/${savedProject.id || data[0].id}`)
        } else {
          this.$emit('cancel')
        }
      } else {
        // eslint-disable-next-line no-console
        console.log('err creating project', data, err)
        this.error = err
      }

      this.loading = false
    },
    async archiveProject () {
      await this.$supabase.from('projects').update({ archived: true }).eq('id', this.project.id)
      await this.$supabase.from('projects_sharing').update({ archived: true }).eq('project_id', this.project.id)
      this.$emit('cancel')
    },
    getRegion (isEpci) {
      if (isEpci) {
        const regionCode = this.projectForm.epci.towns[0].code_region
        // eslint-disable-next-line eqeqeq
        return regions.find(r => r.code == regionCode).iso
      } else {
        return regions.find(r => r.name === this.projectForm.town.nom_region).iso
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
