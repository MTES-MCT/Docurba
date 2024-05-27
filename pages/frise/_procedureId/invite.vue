<template>
  <v-container>
    <v-row v-if="collectivite">
      <v-col cols="12" class="pb-0 mt-6">
        <nuxt-link :to="backToCollectivite" class="text-decoration-none d-flex align-center">
          <v-icon color="primary" small class="mr-2">
            {{ icons.mdiChevronLeft }}
          </v-icon>
          {{ collectivite.intitule }}
        </nuxt-link>
      </v-col>
    </v-row>
    <v-row v-if="collectivite && procedure">
      <v-col cols="12">
        <div class="d-flex align-center">
          <h1 class="text-h1">
            {{ procedure.doc_type }} de {{ collectivite.intitule }}
          </h1>
        </div>
      </v-col>
    </v-row>
    <v-row v-if="loaded">
      <v-col cols="12">
        <v-card outlined class="mb-16">
          <v-container>
            <v-row>
              <v-col cols="12">
                <h2 class="text-h2">
                  Invitez des collaborateurs
                </h2>
              </v-col>
              <v-col cols="12">
                <p>
                  Choisissez les collaborateurs qui auront accès à cette procédure:
                </p>
                <div>
                  <v-list two-line>
                    <v-list-item-group
                      v-model="existingCollaboratorstoInvite"
                      active-class="primary--text"
                      multiple
                    >
                      <template v-for="(collaborator) in collaborators">
                        <v-list-item :key="collaborator.id">
                          <template #default="{ active }">
                            <v-list-item-avatar color="accent" class="text-capitalize white--text font-weight-bold">
                              <template v-if=" collaborator.firstname">
                                {{ collaborator.firstname[0] }}
                              </template>
                              <span v-else>
                                {{ collaborator.email[0] }}
                              </span>
                            </v-list-item-avatar>
                            <v-list-item-content>
                              <v-list-item-title>
                                <template v-if=" collaborator.firstname && collaborator.lastname">
                                  {{ collaborator.firstname }} {{ collaborator.lastname }}
                                </template>
                                <span v-else>
                                  {{ collaborator.email }}
                                </span>
                              </v-list-item-title>
                              <v-list-item-subtitle>{{ collaborator.poste }}</v-list-item-subtitle>
                            </v-list-item-content>
                            <v-list-item-action>
                              <v-btn v-if="active" depressed color="primary">
                                Inviter
                              </v-btn>
                              <v-btn v-else outlined color="primary">
                                Retirer
                              </v-btn>
                            </v-list-item-action>
                          </template>
                        </v-list-item>
                      </template>
                    </v-list-item-group>
                  </v-list>
                </div>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12">
                <div>Ou invitez des collaborateurs manuellement par email:</div>
              </v-col>
              <v-col cols="12">
                <v-text-field filled placeholder="Email, séparés par une virgule">
                  <template #append>
                    <v-btn color="primary" depressed>
                      Partager
                    </v-btn>
                  </template>
                </v-text-field>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12">
                <v-btn color="primary" depressed>
                  Confirmer
                </v-btn>
                <v-btn exact color="primary" :to="`/frise/${$route.params.procedureId}`" outlined>
                  Passer cette étape
                </v-btn>
              </v-col>
            </v-row>
          </v-container>
        </v-card>
      </v-col>
    </v-row>
    <VGlobalLoader v-else />
  </v-container>
</template>

<script>
import axios from 'axios'
import { mdiBookmark, mdiPaperclip, mdiChevronLeft, mdiDotsVertical } from '@mdi/js'

export default
{
  name: 'ProcedureInviteCollab',
  data () {
    return {
      existingCollaboratorstoInvite: [],
      collectivite: null,
      procedure: null,
      events: null,
      dialog: false,
      loaded: false,
      collaborators: null,
      icons: {
        mdiBookmark,
        mdiPaperclip,
        mdiChevronLeft,
        mdiDotsVertical
      }
    }
  },
  computed: {
    isAdmin () {
      if (!this.$user.id) { return false }

      return this.$user.profile?.side === 'etat' ||
        (this.$user.profile?.collectivite_id === this.collectivite.code ||
        this.$user.profile?.collectivite_id === this.collectivite.intercommunaliteCode)
    },
    backToCollectivite () {
      if (this.$user.id && this.$user.profile && this.$user.profile.side === 'etat') {
        return `/ddt/${this.collectivite.departementCode}/collectivites/${this.collectivite.code}/${this.collectivite.code.length > 5 ? 'epci' : 'commune'}`
      } else {
        return `/collectivites/${this.collectivite.code}`
      }
    },
    isVerified () {
      return this.$user?.profile?.side === 'etat' && this.$user?.profile?.verified
    }
  },
  async mounted () {
    try {
      if (this.$user && this.$user.isReady) {
        this.$user.isReady.then(() => {
          if (this.isVerified) {
            this.$nuxt.setLayout('ddt')
          }
        })
      }

      const {
        data: procedure,
        error: errorProcedure
      } = await this.$supabase.from('procedures').select('*, procedures_perimetres(*)')
        .eq('id', this.$route.params.procedureId)

      if (errorProcedure) { throw errorProcedure }

      this.procedure = procedure[0]

      const perimetre = this.procedure.procedures_perimetres.filter(c => c.type === 'COM')
      const collectiviteId = perimetre.length === 1 ? perimetre[0].code : this.procedure.collectivite_porteuse_id

      const { data: collectivite } = await axios({
        url: `/api/geo/collectivites/${collectiviteId}`
      })

      this.collectivite = collectivite

      console.log('collectivite: ', collectivite)
      const {
        data: collaborators,
        error: errorCollaborators
      } = await this.$supabase.from('profiles').select('*').eq('departement', collectivite.departementCode)
      this.collaborators = collaborators
      if (errorCollaborators) { throw errorCollaborators }
      console.log('collaborators: ', collaborators)
      this.loaded = true
    } catch (error) {
      // eslint-disable-next-line no-console
      console.log('ERROR: ', error)
    }
  }
}
</script>
