<template>
  <v-container>
    <v-btn
      v-show="$user?.profile?.is_admin"
      fab
      fixed
      bottom
      left
      color="primary"
      :loading="syncLoading"
      @click="syncProcedure"
    >
      <v-icon>{{ icons.mdiSync }}</v-icon>
    </v-btn>
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
            <!-- {{ procedure.doc_type }} de {{ collectivite.intitule }} -->
            {{ procedure.fullName }}
          </h1>
        </div>
      </v-col>
      <v-col cols="12" class="mb-2">
        <v-btn v-if="$user?.profile?.side === 'etat' && isAdmin && !procedure.secondary_procedure_of" color="primary" class="mr-2" outlined @click="addSubProcedure">
          Ajouter une procédure secondaire
        </v-btn>
        <v-btn v-if="($user?.id && isAdmin)" depressed nuxt color="primary" :to="{name: 'frise-procedureId-add', params: {procedureId: $route.params.procedureId}, query:{typeDu: procedure.doc_type}}">
          Ajouter un événement
        </v-btn>
        <FriseShareDialog
          v-if="isAdmin"
          :document-name="`${procedure.doc_type} de ${collectivite.intitule }`"
          :collaborators="collaborators"
          :departement="collectivite.departementCode"
          @share_to="addToCollabs"
          @remove_shared="removeCollabShared"
        />
        <v-menu v-if="$user?.profile?.side === 'etat' && isAdmin">
          <template #activator="{ on, attrs }">
            <v-btn icon color="primary" v-bind="attrs" v-on="on">
              <v-icon> {{ icons.mdiDotsVertical }}</v-icon>
            </v-btn>
          </template>

          <v-list>
            <FriseInfosDialog />
            <FriseVoletQualiDialog />

            <FriseDgdDialog />
            <!-- <v-list-item link>
              <v-list-item-title>
                Éditer la procédure
              </v-list-item-title>
            </v-list-item> -->

            <v-dialog v-model="dialog" width="500">
              <template #activator="{ on, attrs }">
                <v-list-item link v-bind="attrs" v-on="on">
                  <v-list-item-title class="text--error">
                    Supprimer la procédure
                  </v-list-item-title>
                </v-list-item>
              </template>

              <v-card>
                <v-card-title class="text-h5 error white--text">
                  Cette action est irréversible.
                </v-card-title>

                <v-card-text class="pt-4">
                  Êtes-vous sur de vouloir supprimer cette procédure ? Il ne sera pas possible de revenir en arrière.
                </v-card-text>

                <v-divider />

                <v-card-actions>
                  <v-spacer />
                  <v-btn color="primary" text @click="dialog = false">
                    Annuler
                  </v-btn>
                  <v-btn color="error" depressed @click="archiveProcedure(procedure.id)">
                    Supprimer
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
          </v-list>
        </v-menu>
      </v-col>
    </v-row>
    <v-row v-if="loaded">
      <v-col cols="12">
        <v-card outlined class="mb-16">
          <v-container>
            <v-row>
              <v-col cols="9">
                <FriseEventCard v-if="$user?.id && recommendedEvent && isAdmin" :event="recommendedEvent" suggestion @addSuggestedEvent="addSuggestedEvent" />
                <div v-if="isEmptyFrise" class="d-flex align-center justify-center flex-column py-16">
                  <p class="text-h6 font-weight-bold">
                    Aucun événement
                  </p>
                  <p>Cette procédure n’a pas encore reçu d’événement.</p>
                  <v-btn v-if="$user?.id && isAdmin" depressed nuxt color="primary" :to="{name: 'frise-procedureId-add', params: {procedureId: $route.params.procedureId}, query:{typeDu: procedure.doc_type}}">
                    Ajouter un événement
                  </v-btn>
                </div>
                <div v-else>
                  <template v-for="event in enrichedEvents">
                    <FriseEventCard
                      :id="`event-${event.id}`"
                      :key="event.id"
                      :event="event"
                      :type-du="procedure.doc_type"
                    />
                  </template>
                </div>
              </v-col>
              <v-col cols="3" class="my-6">
                <div class="font-weight-bold">
                  Collaborateurs
                </div>
                <div class="mb-4">
                  <v-list two-line dense class="py-0">
                    <template v-for="(collaborator, icollab) in collaborators">
                      <v-list-item v-if="icollab < 3 || showAllCollabs" :key="collaborator.id" class="pl-0">
                        <v-list-item-avatar :color="collaborator.color" class="text-capitalize white--text font-weight-bold">
                          {{ collaborator.avatar }}
                        </v-list-item-avatar>
                        <v-list-item-content>
                          <v-list-item-title>
                            {{ collaborator.label }}
                          </v-list-item-title>
                          <v-list-item-subtitle>
                            <span> {{ $utils.posteDetails(collaborator.poste) }}</span>

                            <template v-if="collaborator.detailsPoste">
                              <span v-for="detail in collaborator.detailsPoste" :key="`colab-${collaborator.email}-${detail}`">{{ ', ' + $utils.posteDetails(detail) }}</span>
                            </template>
                          </v-list-item-subtitle>
                        </v-list-item-content>
                      </v-list-item>
                    </template>
                  </v-list>
                  <v-btn v-if="collaborators?.length > 3" class="mt-2" depressed @click="showAllCollabs = !showAllCollabs">
                    <span v-if="showAllCollabs">Cacher</span>
                    <span v-else>Voir plus</span>
                  </v-btn>
                </div>
                <p class="font-weight-bold">
                  Événements clés
                </p>
                <div class="mb-4">
                  <div v-for="(eventStructurant, i) in eventsStructurants" :key="i" class="mb-2">
                    <v-tooltip bottom>
                      <template #activator="{ on, attrs }">
                        <v-chip
                          label
                          class="mb-2"
                          color="grey darken-1"
                          v-bind="attrs"
                          v-on="on"
                          @click="scrollToStructurant(eventStructurant.id)"
                        >
                          <v-icon color="grey darken-2" class="mr-2">
                            {{ icons.mdiBookmark }}
                          </v-icon>
                          <span class="text-truncate">
                            {{ eventStructurant.type }}
                          </span>
                        </v-chip>
                      </template>
                      {{ eventStructurant.type }}
                    </v-tooltip>
                  </div>
                </div>
                <p class="font-weight-bold">
                  Ressources
                </p>
                <p>
                  <!-- @click="downloadFile(attachement)" -->
                  <v-tooltip v-for="attachment in attachments" :key="attachment.id" bottom>
                    <template #activator="{ on, attrs }">
                      <v-chip
                        label

                        class="mb-2"
                        color="grey darken-1"
                        v-bind="attrs"
                        v-on="on"
                      >
                        <v-icon color="grey darken-2" class="mr-2">
                          {{ icons.mdiPaperclip }}
                        </v-icon>
                        <span class="text-truncate">
                          {{ attachment.name }}
                        </span>
                      </v-chip>
                    </template>
                    {{ attachment.name }}
                  </v-tooltip>
                </p>
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
import _ from 'lodash'
import { mdiBookmark, mdiPaperclip, mdiChevronLeft, mdiDotsVertical, mdiSync } from '@mdi/js'

import PluEvents from '@/assets/data/events/PLU_events.json'
import ScotEvents from '@/assets/data/events/SCOT_events.json'
import ccEvents from '@/assets/data/events/CC_events.json'

export default
{
  name: 'ProcedureTimelineEvents',
  data () {
    return {
      canShare: false,
      collectivite: null,
      procedure: null,
      events: null,
      dialog: false,
      loaded: false,
      syncLoading: false,
      showAllCollabs: false,
      collaborators: [],
      icons: {
        mdiBookmark,
        mdiPaperclip,
        mdiChevronLeft,
        mdiDotsVertical,
        mdiSync
      }
    }
  },
  computed: {
    isEmptyFrise () {
      return this.events.length === 0 || this.events.every(e => !e.type || !e.date_iso)
    },
    isAdmin () {
      if (this.procedure.shareable) {
        return this.collaborators.some(e => e.email === this.$user.email)
      } else {
        if (!this.$user.id || !this.$user.profile?.verified) { return false }

        const adminDept = _.uniq(this.procedure.procedures_perimetres.map(p => p.departement))

        if (this.$user.profile?.is_admin) { return true }

        if (this.$user.profile?.side === 'etat') {
          return adminDept.includes(this.$user.profile.departement)
        } else {
          return this.canShare || this.$user.profile?.collectivite_id === this.collectivite.code ||
            this.$user.profile?.collectivite_id === this.collectivite.intercommunaliteCode
        }
      }
    },
    internalDocType () {
      let currDocType = this.procedure.doc_type
      if (currDocType.match(/i|H|M/)) {
        currDocType = 'PLU'
      }
      return currDocType
    },
    documentEvents () {
      const documentsEvents = {
        PLU: PluEvents,
        PLUi: PluEvents,
        POS: PluEvents,
        SCOT: ScotEvents,
        CC: ccEvents,
        SD: ScotEvents
      }
      return documentsEvents[this.internalDocType]
    },
    eventsStructurants () {
      return this.enrichedEvents.filter(e => e.structurant)
    },
    enrichedEvents () {
      return this.events.map((event) => {
        const ev = this.documentEvents.find(x => x.name === event.type)
        return { ...event, structurant: !!ev?.structurant }
      }).filter((event) => {
        return event.visibility === 'public' || this.isAdmin || (event.from_sudocuh && event.structurant)
      })
    },
    attachments () {
      return this.enrichedEvents.map(e => e.attachements).flat().filter(e => e)
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
    },
    recommendedEvent () {
      const filteredDocumentEvents = this.documentEvents?.filter(e => e.scope_sugg.includes(this.internalProcedureType))
      if (!filteredDocumentEvents) { return null }

      if (this.events && this.events.length < 1) { return filteredDocumentEvents[0] }
      const lastEventType = this.events[0]

      const lastEventOrder = this.documentEvents.find(e => e.name === lastEventType.type)

      if (!lastEventOrder) { return filteredDocumentEvents[0] }
      return filteredDocumentEvents.find(e => _.gt(e.order, lastEventOrder.order))
    },
    internalProcedureType () {
      const isIntercommunal = this.procedure.current_perimetre.length > 1
      const secondairesTypes = {
        'Révision à modalité simplifiée ou Révision allégée': 'rms',
        Modification: 'm',
        'Modification simplifiée': 'ms',
        'Mise en compatibilité': 'mc',
        'Mise à jour': 'mj'
      }
      if (secondairesTypes[this.procedure.type]) { return secondairesTypes[this.procedure.type] }
      if (['Elaboration', 'Révision'].includes(this.procedure.type)) {
        if (isIntercommunal && this.internalDocType !== 'CC') { return 'ppi' } else { return 'pp' }
      }
      return 'aucun'
    }
  },
  async mounted () {
    try {
      if (this.$user && this.$user.isReady) {
        this.$user.isReady.then(() => {
          this.$tally('woy4KO', {
            max: 3,
            signupDelay: 30
          })

          if (this.isVerified) {
            this.$nuxt.setLayout('ddt')
          }
        })
      }

      const {
        data: procedure,
        error: errorProcedure
      } = await this.$supabase.from('procedures').select('*, secondary_procedure_of(id, project_id), procedures_perimetres(*)')
        .eq('id', this.$route.params.procedureId)

      if (errorProcedure) { throw errorProcedure }

      this.procedure = procedure[0]

      const perimetre = this.procedure.procedures_perimetres.filter(c => c.collectivite_type === 'COM')
      const collectiviteId = perimetre.length === 1 ? perimetre[0].collectivite_code : this.procedure.collectivite_porteuse_id

      const { data: collectivite } = await axios({
        url: `/api/geo/collectivites/${collectiviteId}`
      })

      this.collectivite = collectivite
      this.procedure.fullName = `${this.procedure.type} ${this.procedure.numero ? this.procedure.numero : ''} ${this.procedure.doc_type} ${this.collectivite?.intitule}`

      this.events = await this.getEvents()
      this.collaborators = await this.getCollaborators(this.procedure)
      // console.log('this.collaborators :; ', this.collaborators)
      console.log(' this.procedure: ', this.procedure)
      const canShare = await this.$supabase.from('projects_sharing').select('id').eq('project_id', this.procedure.project_id ?? this.procedure.secondary_procedure_of.project_id).eq('user_email', this.$user.profile.email).eq('role', 'write_frise')
      console.log('canShare: ', canShare)
      // console.log('this.collectivite.: ', this.collectivite.code)

      this.canShare = canShare.data.length > 0
      this.loaded = true
    } catch (error) {
      // eslint-disable-next-line no-console
      console.log('ERROR: ', error)
    }
  },
  methods: {
    async  addToCollabs (collabs) {
      // TODO: Add to
      console.log('collabs: ', collabs)
      const toInsert = collabs.map(e => ({
        user_email: e.email,
        project_id: this.procedure.project_id,
        shared_by: this.$user.id,
        notified: false,
        role: 'write_frise',
        archived: false,
        dev_test: true
      }))
      console.log('toInsert: ', toInsert)
      const { data: insertedCollabs, error: errorInsertedCollabs } = await this.$supabase.from('projects_sharing').insert(toInsert).select()
      if (errorInsertedCollabs) { console.log('errorInsertedCollabs: ', errorInsertedCollabs) }
      await axios({
        url: '/api/slack/notify/frp_shared',
        method: 'post',
        data: {
          from: {
            email: this.$user.email,
            firstname: this.$user.profile.firstname,
            lastname: this.$user.profile.lastname,
            poste: this.$user.profile.poste + ' ' + this.$user.profile.other_poste
          },
          to: {
            emailsFormatted: toInsert.map(e => e.user_email).reduce((acc, curr) => acc + ', ' + curr, '').slice(2),
            emails: toInsert.map(e => e.user_email)
          },
          type: 'frp',
          procedure: { url: window.location.href, name: this.procedure.fullName }
        }
      })
      console.log('insertedCollabs: ', insertedCollabs)

      this.collaborators = await this.getCollaborators(this.procedure)
    },
    async removeCollabShared (toRemoveCollaborator) {
      console.log('toRemoveCollaborator; ', toRemoveCollaborator)
      // TODO: Delete
      const { data: removedCollab, error: errorDeleteCollab } = await this.$supabase.from('projects_sharing').delete().eq('user_email', toRemoveCollaborator.email).eq('role', 'write_frise').eq('project_id', this.procedure.project_id).select()
      if (errorDeleteCollab) { console.log('errorDeleteCollab: ', errorDeleteCollab) }
      console.log('Removed: ', removedCollab)
      this.collaborators = await this.getCollaborators(this.procedure)
    },
    async getCollaborators (procedure) {
      let legacyCollabs = []
      if (!this.procedure.shareable) {
        const adminDept = _.uniq(this.procedure.procedures_perimetres.map(p => p.departement))
        console.log('adminDeptadminDeptadminDeptadminDept: ', adminDept)
        const { data: stateProfiles, error: errorStateProfiles } = await this.$supabase.from('profiles').select('*')
          .in('departement', adminDept)
          .eq('side', 'etat')

        if (errorStateProfiles) { console.log('errorStateProfiles: ', errorStateProfiles) }

        const { data: collectiviteProfiles, error: errorCollectiviteProfiles } = await this.$supabase.from('profiles').select('*')
          .eq('side', 'collectivite')
          .or(`collectivite_id.eq.${this.collectivite.code}, collectivite_id.eq.${this.collectivite.intercommunaliteCode}`)
        if (errorCollectiviteProfiles) { console.log('errorCollectiviteProfiles: ', errorCollectiviteProfiles) }

        console.log('stateProfiles: ', stateProfiles, 'collectiviteProfiles: ', collectiviteProfiles)
        legacyCollabs = [...stateProfiles ?? [], ...collectiviteProfiles ?? []]
      }

      const { data: collabsData, error: errorCollabs } = await this.$supabase.from('projects_sharing')
        .select('*')
        .eq('project_id', procedure.project_id)
        .eq('role', 'write_frise')

      if (errorCollabs) { console.log('errorCollabs: ', errorCollabs) }

      const emails = _.uniqBy(collabsData, e => e.user_email).map(e => e.user_email)

      const { data: profilesData, error: errorProfiles } = await this.$supabase.from('profiles').select('*').in('email', emails)

      if (errorCollabs) { console.log('errorProfiles: ', errorProfiles) }
      const allCollaborators = [...legacyCollabs ?? [], ...profilesData ?? []]
      const formattedProfiles = allCollaborators.map(e => this.$utils.formatProfileToCreator(e))

      const noProfilesCollabs = emails.filter(e => !profilesData.find(prof => prof.email === e)).map(e => (this.$utils.formatProfileToCreator({ email: e })))

      return formattedProfiles.concat(noProfilesCollabs)
    },
    async downloadFile (attachement) {
      // TODO: Handle link type
      const path = this.event.from_sudocuh ? attachement.id : `${this.event.project_id}/${this.event.id}/${attachement.id}`
      const { data } = await this.$supabase.storage.from('doc-events-attachements').download(path)

      const link = this.$refs[`file-${attachement.id}`][0]
      link.href = URL.createObjectURL(data)
      link.click()
    },
    addSubProcedure () {
      this.$router.push(`/ddt/${this.collectivite.departementCode}/collectivites/${this.collectivite.code}/procedure/add?secondary_id=${this.$route.params.procedureId}`)
    },
    scrollToStructurant (eventId) {
      if (eventId) {
        // The event- is here to prevent errors since ids should start with a letter: https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/id
        this.$vuetify.goTo(`#event-${eventId}`)
      }
    },
    addSuggestedEvent (eventName) {
      this.$router.push(`/frise/${this.procedure.id}/add?eventType=${eventName}&typeDu=${this.procedure.doc_type}`)
    },
    async archiveProcedure (idProcedure) {
      try {
        const { error } = await this.$supabase.from('procedures').delete().eq('id', idProcedure)
        if (error) { throw error }
        this.$emit('delete', idProcedure)
        this.dialog = false
        this.$router.push(-1)
      } catch (error) {
        // eslint-disable-next-line no-console
        console.log(error)
      }
    },
    async getEvents () {
      const { data: events, error: errorEvents } = await this.$supabase.from('doc_frise_events')
        .select('*, profiles(*)')
        .eq('procedure_id', this.$route.params.procedureId)
        .order('date_iso', { ascending: false })
        .order('created_at', { ascending: false })

      if (errorEvents) { throw errorEvents }
      return events
    },
    async syncProcedure () {
      this.syncLoading = true
      await axios(`https://nuxt3.docurba.incubateur.net/api/urba/procedures/${this.$route.params.procedureId}/update`)
      this.syncLoading = false
    }
  }
}
</script>
