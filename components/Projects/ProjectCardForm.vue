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
          <VDocumentSelect v-model="newProject.docType" />
        </v-col>
        <v-col v-if="newProject.docType.includes('i') && EPCIs.length" cols="12">
          <VEpciAutocomplete v-model="newProjectEpci" :epci-list="EPCIs" />
        </v-col>
        <v-col v-else cols="12">
          <VTownAutocomplete v-model="newProjectTown" :default-departement-code="userDeptCode" hide-dept />
        </v-col>
        <v-col cols="12">
          <v-switch />
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
      newProjectEpci: this.project.epci,
      newProjectTown: this.project.towns ? this.project.towns[0] : null,
      newProject: Object.assign({}, this.project),
      userDeptCode: null,
      EPCIs: [],
      loading: false,
      error: null
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

    this.PAC = this.unifyPacs([deptSections, this.PAC])

    const EPCIs = (await axios({
      method: 'get',
      url: `/api/epci?departement=${this.userDeptCode}`
    })).data

    this.EPCIs = EPCIs
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

      const isEpci = this.newProject.docType.includes('i')

      const savedProject = Object.assign({}, this.newProject, {
        epci: isEpci ? this.newProjectEpci : null,
        towns: isEpci ? this.newProjectEpci.towns : [this.newProjectTown],
        region: this.getRegion(isEpci)
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
    getRegion (isEpci) {
      if (isEpci) {
        const regionCode = this.newProjectEpci.towns[0].code_region
        // eslint-disable-next-line eqeqeq
        return regions.find(r => r.code == regionCode).iso
      } else {
        return regions.find(r => r.name === this.newProjectTown.nom_region).iso
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
