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
            Nouvelle procédure
          </h1>
        </div>
      </v-col>
    </v-row>
    <v-row v-if="loaded">
      <v-col cols="12">
        <v-card outlined class="mb-16 pa-8">
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
                  <v-list two-line max-width="750">
                    <v-list-item-group
                      v-model="existingCollaboratorstoInvite"

                      multiple
                    >
                      <template v-for="(collaborator) in collaborators">
                        <v-list-item :key="collaborator.id" class="px-0" :value="collaborator">
                          <template #default="{ active }">
                            <v-list-item-avatar :color="collaborator.color" class="text-capitalize white--text font-weight-bold">
                              {{ collaborator.avatar }}
                            </v-list-item-avatar>
                            <v-list-item-content>
                              <v-list-item-title class="text-capitalize">
                                {{ collaborator.label }}
                              </v-list-item-title>
                              <v-list-item-subtitle>
                                <span> {{ $utils.posteDetails(collaborator.poste) }}</span>
                                <template v-if="collaborator.detailsPoste">
                                  <span v-for="detail in collaborator.detailsPoste" :key="`colab-${collaborator.email}-${detail}`">{{ ', ' + $utils.posteDetails(detail) }}</span>
                                </template>
                              </v-list-item-subtitle>
                            </v-list-item-content>
                            <v-list-item-action>
                              <v-btn v-if="active" depressed color="primary">
                                Retirer
                              </v-btn>
                              <v-btn v-else outlined color="primary">
                                Inviter
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
                <div class="mb-2">
                  Ou invitez des collaborateurs manuellement par email:
                </div>
                <v-text-field v-model="emailsToShareTxt" filled placeholder="Email, séparés par une virgule" center-affix style="max-width:750px">
                  <template #append>
                    <v-btn color="primary" depressed @click="addToShare">
                      Partager
                    </v-btn>
                  </template>
                </v-text-field>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12">
                <v-btn color="primary" depressed class="mr-2" @click="confirmShare">
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
// import _ from 'lodash'
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
      emailsToShareTxt: null,
      icons: {
        mdiBookmark,
        mdiPaperclip,
        mdiChevronLeft,
        mdiDotsVertical
      }
    }
  },
  computed: {
    emailsToShare () {
      console.log("this.emailsToShareTxt.split(','): ", this.emailsToShareTxt.split(','))
      return this.emailsToShareTxt.split(',')
    },
    isAdmin () {
      if (!this.$user.id) { return false }

      return this.$user.profile?.side === 'etat' || this.$user.profile?.is_admin ||
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
      console.log('Procedure, : ', this.procedure, ' -- ', this.$user, ' this.$route. ', this.$route.params.procedureId)
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

      this.collaborators = collaborators.map(e => this.$utils.formatProfileToCreator(e))
      if (errorCollaborators) { throw errorCollaborators }

      // this.existingCollaboratorstoInvite = this.collaborators.filter((collab) => {
      //   return _.intersection(['suivi_procedures', 'referent_sudocuh'], collab.detailsPoste).length > 0
      // })

      this.loaded = true
    } catch (error) {
      // eslint-disable-next-line no-console
      console.log('ERROR: ', error)
    }
  },
  methods: {
    addToShare () {
      const newCollabs = this.emailsToShare.map(e => ({ avatar: e[0], label: e, color: 'error', email: e }))
      this.collaborators = this.collaborators.concat(newCollabs)
      this.existingCollaboratorstoInvite = this.existingCollaboratorstoInvite.concat(newCollabs)
      this.emailsToShareTxt = null
    },
    async confirmShare () {
      const toInsert = this.existingCollaboratorstoInvite.map(e => ({
        user_email: e.email,
        project_id: this.procedure.project_id,
        shared_by: this.$user.id,
        notified: false,
        role: 'write_frise',
        archived: false,
        dev_test: true
      }))
      console.log('toInsert: ', toInsert)
      const { data: insertedCollabs } = await this.$supabase.from('projects_sharing').insert(toInsert).select()
      console.log('insertedCollabs: ', insertedCollabs)

      insertedCollabs.forEach((ins) => {
        axios.post('/api/projects/notify/shared/frp', {
          sharings: {
            to: ins.user_email,
            sender_email: this.$user.email,
            sender_firstname: this.$user.profile.firstname,
            sender_lastname: this.$user.profile.lastname,
            procedure_name: `${this.procedure.doc_type} de ${this.collectivite.intitule}`,
            procedure_id: this.$route.params.procedureId
          }
        })
      })
      this.$router.push(`/frise/${this.$route.params.procedureId}`)
    }
  }
}
</script>
<style lang="scss" scoped>

.v-list-item--link:before{
background-color: white;
opacity: 0;
}
</style>>
</style>
