<template>
  <v-card>
    <v-card-title>
      <slot name="title" />
    </v-card-title>
    <v-card-text v-if="userDeptCode">
      <v-row>
        <v-col cols="12">
          <v-select
            v-model="userDeptCode"
            filled
            dense
            :items="refsRoles"
            hint="Trame départementale"
            persistent-hint
            :readonly="!!project.id"
            @change="fetchEPCIs"
          />
        </v-col>
        <v-col cols="12">
          <VDocumentSelect v-model="newProject.doc_type" />
        </v-col>
        <v-col v-if="newProject.doc_type.includes('i') && EPCIs.length" cols="12">
          <VEpciAutocomplete v-model="projectForm.epci" :epci-list="EPCIs" @input="updateDefaultName" />
        </v-col>
        <v-col v-else cols="12">
          <VTownAutocomplete v-model="projectForm.town" :default-departement-code="userDeptCode" hide-dept @input="updateDefaultName" />
        </v-col>
        <v-col cols="12">
          <v-text-field
            v-model="newProject.name"
            filled
            hide-details
            placeholder="Nom du projet"
            dense
          />
        </v-col>
        <v-col cols="12">
          <v-switch v-model="projectForm.useTrame" :label="`Utiliser la trame de PAC du ${userDeptCode}`" />
        </v-col>
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

export default {
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
      // PAC: [],
      refsRoles: [],
      userDeptCode: null,
      projectForm: {
        useTrame: this.project.id ? !!this.project.trame : true,
        epci: this.project.epci,
        town: this.project.towns ? this.project.towns[0] : null
      },
      newProject: Object.assign({}, this.project),
      EPCIs: [],
      loading: false,
      error: null
    }
  },
  async mounted () {
    this.refsRoles = (await this.$auth.getRefsRoles()).filter((role) => {
      return role.ref.includes('dept')
    })

    this.refsRoles.forEach((role) => {
      role.text = this.$options.filters.githubRef(role.ref)
      role.value = role.ref.replace('dept-', '')
    })

    this.userDeptCode = this.project.id ? this.project.trame : this.refsRoles[0].value

    this.fetchEPCIs()
  },
  // wathc: {
  //   'projectForm.epci' () {
  //     this.updateDefaultName()
  //   },
  //   'projectForm.town' () {
  //     this.updateDefaultName()
  //   }
  // },
  methods: {
    async fetchEPCIs () {
      const EPCIs = (await axios({
        method: 'get',
        url: `/api/epci?departement=${this.userDeptCode}`
      })).data

      this.EPCIs = EPCIs
    },
    async createOrUpdate (savedProject) {
      if (savedProject.id) {
        return await this.$supabase.from('projects').upsert(savedProject).select()
      } else {
        const { data, err } = await this.$supabase.from('projects').insert([savedProject]).select()
        const projectId = data[0].id

        await axios({
          method: 'post',
          url: `/api/trames/projects/dept-${this.$options.filters.deptToRef(savedProject.trame)}`,
          data: {
            userId: this.$user.id,
            projectId
          }
        })

        return { data, err }
      }
    },
    updateDefaultName () {
      if (!this.newProject.name) {
        console.log('updateName')

        if (this.newProject.doc_type.includes('i')) {
          this.newProject.name = `${this.projectForm.epci.label} - ${new Date().getFullYear()}`
        } else {
          this.newProject.name = `${this.projectForm.town.nom_commune} - ${new Date().getFullYear()}`
        }
      }
    },
    async upsertProject () {
      this.loading = true

      const isEpci = this.newProject.doc_type.includes('i')

      const savedProject = Object.assign({}, this.newProject, {
        epci: isEpci ? this.projectForm.epci : null,
        towns: isEpci ? this.projectForm.epci.towns : [this.projectForm.town],
        region: this.getRegion(isEpci),
        trame: this.projectForm.useTrame ? (this.project.trame || this.userDeptCode) : ''
      })

      if (!this.newProject.PAC.length) {
        savedProject.PAC = []

        const { data: sections } = await axios({
          method: 'get',
          url: `/api/trames/tree/dept-${this.$options.filters.deptToRef(savedProject.trame)}`
        })

        function addPath (section) {
          savedProject.PAC.push(section.path)
          if (section.children) {
            section.children.forEach(c => addPath(c))
          }
        }

        sections.forEach(s => addPath(s))
      }

      const { data, err } = await this.createOrUpdate(savedProject)

      if (!err && data) {
        if (!savedProject.id) {
          this.$router.push(`/trames/projet-${savedProject.id || data[0].id}`)
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
        const regionCode = this.projectForm.epci.towns[0].regionCode
        console.log(this.projectForm.epci.towns)

        // eslint-disable-next-line eqeqeq
        return regions.find(r => r.code == +regionCode).iso
      } else {
        // eslint-disable-next-line eqeqeq
        return regions.find(r => r.code == this.projectForm.town.regionCode).iso
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
