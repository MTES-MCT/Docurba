<template>
  <v-container v-if="loaded && !procedure">
    <h1 class="text-h1">
      Nous n'avons pas pu trouver cette procédure
    </h1>
  </v-container>
  <v-container v-else>
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
            {{ $utils.formatProcedureName(procedure, collectivite) }}
          </h1>
        </div>
      </v-col>
      <v-col v-if="!procedure.project_id">
        <v-alert type="warning">
          Cette procédure n'a pas de projet associé.
        </v-alert>
      </v-col>
      <v-col v-if="procedure.archived" cols="12">
        <v-alert type="warning">
          Cette procédure est archivée.
          <span v-if="procedure.doublon_cache_de_id">
            <nuxt-link :to="{name: 'frise-procedureId', params: {procedureId: procedure.doublon_cache_de_id}}">
              Visiter la procédure canonique.
            </nuxt-link>
          </span>
        </v-alert>
      </v-col>
      <v-col v-if="!isProcedureReadOnly()" cols="12" class="mb-2">
        <v-btn
          v-if="canCreateSecondaryProcedure"
          color="primary"
          class="mr-2"
          outlined
          :to="{
            name:'collectivites-collectiviteId-procedures-add',
            params:{collectiviteId: collectivite.code},
            query:{secondary_id: $route.params.procedureId}
          }"
        >
          Ajouter une procédure secondaire
        </v-btn>
        <v-btn v-if="($user?.id && isAdmin)" depressed nuxt color="primary" :to="{name: 'frise-procedureId-add', params: {procedureId: $route.params.procedureId}, query:{typeDu: procedure.doc_type}}">
          Ajouter un événement
        </v-btn>
        <FriseShareDialog
          v-if="isAdmin"
          :document-name="$utils.formatProcedureName(procedure, collectivite)"
          :collaborators="toDisplayCollabs"
          :departement="collectivite.departementCode"
          :collectivite="collectivite"
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
            <!-- <FriseInfosDialog />
            <FriseVoletQualiDialog /> -->

            <FriseDgdDialog />
            <!-- <v-list-item link>
              <v-list-item-title>
                Éditer la procédure
              </v-list-item-title>
            </v-list-item> -->

            <v-dialog v-if="$user.canDeleteProcedure()" v-model="dialog" width="500">
              <template #activator="{ on, attrs }">
                <v-list-item link v-bind="attrs" v-on="on">
                  <v-list-item-title class="error--text">
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
                <FriseEventCard
                  v-if="!isProcedureReadOnly() && $user?.id && recommendedEvent && isAdmin"
                  :event="recommendedEvent"
                  suggestion
                  @addSuggestedEvent="addSuggestedEvent"
                />
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
                <SignalementProbleme class="mb-4" />

                <v-alert v-if="procedure.from_sudocuh" type="info" dense text>
                  Procédure débutée sur Sudocuh
                </v-alert>

                <template v-if="$user && $user.email && isAdmin">
                  <div class="font-weight-bold">
                    Collaborateurs
                  </div>
                  <div class="mb-4">
                    <ul class="pl-0">
                      <template v-for="(collaborator, icollab) in toDisplayCollabs">
                        <li v-if="icollab < 3 || showAllCollabs" :key="collaborator.id" class="d-flex py-2 text-body-2 font-weight-medium" style="font-size: .8125rem !important; gap: 0.5rem;">
                          <v-avatar size="40" :color="collaborator.color" class="text-capitalize text-body-1 font-weight-bold white--text">
                            {{ collaborator.avatar }}
                          </v-avatar>
                          <div>
                            {{ collaborator.label }}
                            <div class="mention-grey--text">
                              {{ $utils.formatPostesAndSide(collaborator) }}
                            </div>
                          </div>
                        </li>
                      </template>
                    </ul>
                    <v-btn v-if="collaborators?.length > 3" class="mt-2" depressed @click="showAllCollabs = !showAllCollabs">
                      <span v-if="showAllCollabs">Cacher</span>
                      <span v-else>Voir plus</span>
                    </v-btn>
                  </div>
                </template>
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
import { mdiBookmark, mdiChevronLeft, mdiDotsVertical, mdiPaperclip, mdiSync } from '@mdi/js'
import axios from 'axios'
import _ from 'lodash'

import ccEvents from '@/assets/data/events/CC_events.json'
import PluEvents from '@/assets/data/events/PLU_events.json'
import ScotEvents from '@/assets/data/events/SCOT_events.json'

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
    toDisplayCollabs () {
      return this.$sharing.excludeStaff(this.collaborators)
    },
    isEmptyFrise () {
      return this.events.length === 0 || this.events.every(e => !e.type || !e.date_iso)
    },
    isAdmin () {
      console.log('this.$user.profile: ', this.$user)
      if (this.$user.profile?.is_admin) { return true }
      if (this.procedure.shareable) {
        return this.collaborators.some(e => e.email === this.$user.email) || this.$user.profile.is_admin
      } else {
        if (!this.$user.id || !this.$user.profile?.verified) { return false }

        const adminDept = _.uniq(this.procedure.procedures_perimetres.map(p => p.departement))

        if (this.$user.profile?.side === 'etat') {
          return adminDept.includes(this.$user.profile.departement) || this.canShare
        } else {
          return this.canShare || this.$user.profile?.collectivite_id === this.collectivite.code ||
            this.$user.profile?.collectivite_id === this.collectivite.intercommunaliteCode
        }
      }
    },
    canCreateSecondaryProcedure () {
      if (this.$user.profile.side === 'ppa') {
        return false
      }
      return this.isAdmin && !this.procedure.secondary_procedure_of
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
      console.log('this.isAdmin: ', this.isAdmin)
      return this.events.map((event) => {
        const ev = this.documentEvents.find(x =>
          // Matche le type d'événement en regardant le libellé Docurba ET le libellé Sudocuh
          [x.name, x["lib EV (sur l'outil Sudocuh)"]].includes(event.type)
        )
        return { ...event, structurant: !!ev?.structurant }
      }).filter((event) => {
        return event.visibility === 'public' || this.isAdmin || (event.from_sudocuh && event.structurant)
      })
    },
    attachments () {
      return this.enrichedEvents.map(e => e.attachements).flat().filter(e => e)
    },
    backToCollectivite () {
      if (this.$user.id && this.$user.profile && this.$user.canViewDDTLayout()) {
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
        await this.$user.isReady

        this.$tally('woy4KO', {
          max: 3,
          signupDelay: 30
        })

        if (this.isVerified) {
          this.$nuxt.setLayout('ddt')
        }
      }

      const {
        data: procedure,
        error: errorProcedure
      } = await this.$supabase.from('procedures').select('*, secondary_procedure_of(id, project_id), procedures_perimetres(*)')
        .eq('id', this.$route.params.procedureId).maybeSingle()

      if (errorProcedure) { throw errorProcedure }

      if (!procedure) {
        this.loaded = true
        console.log('⚠️ 404')
        return
      }
      this.procedure = procedure
      console.log(' this.procedure: ', this.procedure)
      this.procedure.project_id = this.procedure.project_id ?? this.procedure.secondary_procedure_of?.project_id

      const perimetre = this.procedure.procedures_perimetres.filter(c => c.collectivite_type === 'COM')
      const collectiviteId = perimetre.length === 1 ? perimetre[0].collectivite_code : this.procedure.collectivite_porteuse_id
      const { data: collectivite } = await axios({
        url: `/api/geo/collectivites/${collectiviteId}`
      })
      this.collectivite = collectivite

      this.events = await this.getEvents()

      this.collaborators = await this.$sharing.getCollaborators(this.procedure, this.collectivite)
      if (this.procedure.project_id) {
        const canShare = await this.$supabase.from('projects_sharing').select('id').eq('project_id', this.procedure.project_id).eq('user_email', this.$user.profile.email).eq('role', 'write_frise')
        this.canShare = canShare.data.length > 0
      }

      this.loaded = true
    } catch (error) {
      // eslint-disable-next-line no-console
      console.log('ERROR: ', error)
    }
  },
  methods: {
    async addToCollabs (collabs) {
      console.log('collabs to invite: ', collabs)
      await this.$sharing.addToCollabs(this.procedure, collabs, this.collectivite)
      this.collaborators = await this.$sharing.getCollaborators(this.procedure, this.collectivite)
    },
    async removeCollabShared (toRemoveCollaborator) {
      const { error: errorDeleteCollab } = await this.$supabase.from('projects_sharing')
        .delete().eq('user_email', toRemoveCollaborator.email)
        .eq('role', 'write_frise').eq('project_id', this.procedure.project_id).select()

      this.$analytics({
        category: 'partage',
        name: 'suppression collaborateur',
        value: 'write_frise'
      })

      if (errorDeleteCollab) { console.log('errorDeleteCollab: ', errorDeleteCollab) }
      this.collaborators = await this.$sharing.getCollaborators(this.procedure, this.collectivite)
    },
    async downloadFile (attachement) {
      // TODO: Handle link type
      const path = this.event.from_sudocuh ? attachement.id : `${this.event.project_id}/${this.event.id}/${attachement.id}`
      const { data } = await this.$supabase.storage.from('doc-events-attachements').download(path)

      const link = this.$refs[`file-${attachement.id}`][0]
      link.href = URL.createObjectURL(data)
      link.click()
    },
    isProcedureReadOnly () {
      return this.procedure.archived || !this.procedure.project_id
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
        const { error } = await this.$supabase
          .from('procedures')
          .update({ soft_delete: true })
          .eq('id', idProcedure)

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
      await axios(`${process.env.NUXT3_API_URL}/api/urba/procedures/${this.$route.params.procedureId}/update`)
      this.syncLoading = false
    }
  }
}
</script>
