<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1>Mes Porter à Connaissance</h1>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="auto">
        <v-btn color="primary" depressed @click="creationDialog = true">
          Créer un PAC
        </v-btn>
      </v-col>
      <v-col cols="auto">
        <v-btn
          color="primary"
          depressed
          outlined
          :to="{
            name: 'trames-githubRef',
            params: {githubRef: trameRef}
          }"
        >
          Consulter la trame de PAC {{ trameRef.includes('region') ? 'régionale' : 'départementale' }}
        </v-btn>
      </v-col>
    </v-row>

    <v-row>
      <v-col>
        <v-container fluid class="pac-container">
          <v-row>
            <v-col cols="6">
              <v-text-field v-model="search" outlined hide-details label="Rechercher un PAC" :append-icon="icons.mdiMagnify" />
            </v-col>
          </v-row>

          <v-row>
            <v-col>
              <v-data-table
                class="pac-table"
                hide-default-header
                hide-default-footer
                :loading="loading"
                :headers="headers"
                :items="projects"
                :search="search"
                :custom-filter="customFilter"
                :items-per-page="10"
                :page.sync="page"
                @page-count="pageCount = $event"
              >
                <!-- eslint-disable-next-line vue/valid-v-slot -->
                <template #item.name="{ item }">
                  <div :style="{ fontWeight: 700 }">
                    {{ item.name }}
                  </div>
                </template>
                <!-- eslint-disable-next-line vue/valid-v-slot -->
                <template #item.actions="{ item }">
                  <span>
                    créé le {{ new Date(item.created_at).toLocaleDateString() }}
                  </span>

                  <v-menu offset-y left>
                    <template #activator="{ attrs, on }">
                      <v-btn
                        :loading="loadingPdf.includes(item.id)"
                        :style="{ borderRadius: '4px' }"
                        class="ml-4"
                        color="primary"
                        depressed
                        icon
                        outlined
                        v-bind="attrs"
                        v-on="on"
                      >
                        <v-icon>{{ icons.mdiDotsVertical }}</v-icon>
                      </v-btn>
                    </template>

                    <v-list>
                      <v-list-item @click="openShareDialog(item)">
                        <v-list-item-title>Partager ce PAC</v-list-item-title>
                      </v-list-item>
                      <v-list-item @click="downloadPdf(item)">
                        <v-list-item-title>Télécharger en PDF</v-list-item-title>
                      </v-list-item>
                      <!-- <v-list-item>
                        <v-list-item-title :style="{ color: '#e10600' }">
                          Supprimer le PAC
                        </v-list-item-title>
                      </v-list-item> -->
                    </v-list>
                  </v-menu>

                  <v-btn elevation="0" depressed :to="`/trames/projet-${item.id}`" class="ml-4 edit-button">
                    Consulter
                    <v-icon right>
                      {{ icons.mdiArrowRight }}
                    </v-icon>
                  </v-btn>
                </template>
              </v-data-table>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="6">
              <v-pagination v-model="page" class="pac-pagination" :length="pageCount" />
            </v-col>
          </v-row>
        </v-container>
      </v-col>
    </v-row>
    <DashboardSharePACDialog v-if="shareProject" :key="shareProject.id" v-model="shareDialog" :project="shareProject" />
    <PACTrameGhostSectionsDialog />
    <DashboardDUInsertDialog v-model="creationDialog" @insert="fetchProjects" />
  </v-container>
</template>

<script>
import { mdiMagnify, mdiDotsVertical, mdiArrowRight } from '@mdi/js'
import axios from 'axios'

export default {
  layout: 'ddt',
  data () {
    return {
      headers: [
        { value: 'name' },
        { value: 'actions', align: 'end', filterable: false }
      ],
      projects: [],
      search: this.$route.query.search,
      page: 1,
      pageCount: 0,
      icons: {
        mdiMagnify,
        mdiDotsVertical,
        mdiArrowRight
      },
      intercomunalites: [],
      communes: [],
      creationDialog: false,
      shareDialog: false,
      shareProject: null,
      loading: true,
      loadingPdf: []
    }
  },
  computed: {
    trameRef () {
      const scopes = { ddt: 'dept', dreal: 'region' }
      const poste = this.$user.profile.poste
      const code = poste === 'ddt' ? this.$user.profile.departement : this.$user.profile.region

      return `${scopes[poste]}-${this.$options.filters.deptToRef(code)}`
    }
  },
  async mounted () {
    const departement = this.$route.params.departement

    const { data: communes } = await axios(`/api/geo/communes?departementCode=${departement}`)
    const { data: intercomunalites } = await axios(`/api/geo/intercommunalites?departementCode=${departement}`)

    this.communes = communes
    this.intercomunalites = intercomunalites

    await this.fetchProjects()
    this.loading = false
  },
  methods: {
    findCollectivity (code) {
      return this.intercomunalites.find(i => i.code === code) || this.communes.find(c => c.code === code)
    },
    async fetchProjects () {
      const { data: projects } = await this.$supabase.from('projects').select('id, name, doc_type, towns, collectivite_id, PAC, trame, region, created_at').match({
        owner: this.$user.id,
        archived: false
      })

      projects.forEach((project) => {
        const collectivity = this.findCollectivity(project.collectivite_id)
        project.collectivity = collectivity
      })

      this.projects = projects.filter(project => !!project.collectivity)
    },
    customFilter (value, search, item) {
      if (!search?.length || !value?.length) { return true }

      const normalizedValue = value.toLocaleLowerCase().normalize('NFKD').replace(/\p{Diacritic}/gu, '')
      const normalizedSearch = search.toLocaleLowerCase().normalize('NFKD').replace(/\p{Diacritic}/gu, '')

      return normalizedValue.includes(normalizedSearch)
    },
    openShareDialog (project) {
      this.shareProject = project
      this.shareDialog = true
    },
    async downloadPdf (project) {
      this.loadingPdf.push(project.id)
      await this.$pdf.pdfFromRef(`projet-${project.id}`, project)
      this.loadingPdf = this.loadingPdf.filter(id => id !== project.id)
    }
  }
}
</script>

<style>
.pac-container {
  background-color: #fff;
  padding: 24px;
  border: 1px solid var(--v-grey-base);
}

.pac-table tr:hover {
  background-color: transparent !important;
}

.pac-table tr {
  height: 72px;
}

.pac-pagination .v-pagination__item, .pac-pagination .v-pagination__navigation {
  border-radius: 0;
  box-shadow: none;
}

.pac-pagination .v-pagination {
  justify-content: flex-start;
}

.edit-button {
  color: var(--v-primary-base) !important;
  background-color: var(--v-primary-lighten4) !important;
}
</style>
