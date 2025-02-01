<template>
  <v-dialog v-model="show" width="792" persistent>
    <v-card>
      <v-card-title>
        <h4>Mettez votre trame de PAC à jour</h4>
      </v-card-title>
      <v-card-text>
        <p :style="{ fontSize: '16px' }">
          De nouvelles mises à jours provenant la trame de PAC {{ upperTrameRef === 'main' ? 'nationale' : 'régionale' }} sont disponibles.
          Rendez-vous sur votre trame de PAC {{ trameRef.startsWith('dept') ? 'départementale' : 'régionale' }} pour la mettre à jour.
        </p>
        <img src="/images/pac-ghost-section.png" height="186px">
      </v-card-text>
      <v-card-actions>
        <v-btn
          color="primary"
          elevation="0"
          :to="{
            name: 'trames-githubRef',
            params: {githubRef: trameRef}
          }"
        >
          Voir ma trame de PAC
        </v-btn>
        <v-btn color="primary" outlined @click="ignoreNewGhostSections">
          Ignorer
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import axios from 'axios'
import departements from '@/assets/data/departements-france.json'

const IGNORED_SHA_LOCAL_STORAGE_KEY = 'ignoredUpperTrameCommitSha'

export default {
  data () {
    return {
      show: false,
      upperTrameLastCommitSha: null
    }
  },
  computed: {
    trameRef () {
      const scopes = { ddt: 'dept', dreal: 'region' }
      const poste = this.$user.profile.poste
      const code = poste === 'ddt' ? this.$user.profile.departement : this.$user.profile.region

      return `${scopes[poste]}-${this.$options.filters.deptToRef(code)}`
    },
    upperTrameRef () {
      let headRef = 'main'

      if (this.trameRef.includes('dept-')) {
        const dept = this.trameRef.replace('dept-', '')
        // eslint-disable-next-line eqeqeq
        const region = departements.find(d => d.code_departement == dept).code_region
        headRef = `region-${region}`
      }

      return headRef
    }
  },
  mounted () {
    this.checkIfTrameHasGhostSections()
  },
  methods: {
    async checkIfTrameHasGhostSections () {
      const { data: upperTrameHead } = await axios({
        method: 'get',
        url: `/api/trames/${this.upperTrameRef}/head`
      })

      this.upperTrameLastCommitSha = upperTrameHead.sha
      const ignoredUpperTrameCommitSha = localStorage.getItem(IGNORED_SHA_LOCAL_STORAGE_KEY)

      if (this.upperTrameLastCommitSha && this.upperTrameLastCommitSha === ignoredUpperTrameCommitSha) {
        return
      }

      const { data: trameSections } = await axios({
        method: 'get',
        url: `/api/trames/tree/${this.trameRef}`,
        params: {
          ghostRef: this.upperTrameRef
        }
      })

      function hasGhost (sections) {
        for (const s of sections) {
          if (s.ghost) {
            return true
          }
          if (s.children && s.children.length > 0) {
            if (hasGhost(s.children)) {
              return true
            }
          }
        }
        return false
      }

      if (hasGhost(trameSections)) {
        this.show = true
      }
    },
    ignoreNewGhostSections () {
      localStorage.setItem(IGNORED_SHA_LOCAL_STORAGE_KEY, this.upperTrameLastCommitSha)
      this.show = false
    }
  }
}
</script>
