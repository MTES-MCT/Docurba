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
      <v-col cols="12" class="mb-2">
        <v-btn v-if="$user?.profile?.side === 'etat' && !procedure.secondary_procedure_of" color="primary" class="mr-2" outlined @click="addSubProcedure">
          Ajouter une procédure secondaire
        </v-btn>
        <v-btn v-if="$user?.id && isAdmin" depressed nuxt color="primary" :to="{name: 'frise-procedureId-add', params: {procedureId: $route.params.procedureId}, query:{typeDu: procedure.doc_type}}">
          Ajouter un événement
        </v-btn>
        <v-menu v-if="$user?.profile?.side === 'etat'">
          <template #activator="{ on, attrs }">
            <v-btn icon color="primary" v-bind="attrs" v-on="on">
              <v-icon> {{ icons.mdiDotsVertical }}</v-icon>
            </v-btn>
          </template>

          <v-list>
            <v-dialog v-model="dialog" width="500">
              <template #activator="{ on, attrs }">
                <v-list-item link v-bind="attrs" v-on="on">
                  <v-list-item-title>
                    Supprimer
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
import { mdiBookmark, mdiPaperclip, mdiChevronLeft, mdiDotsVertical } from '@mdi/js'

import PluEvents from '@/assets/data/events/PLU_events.json'
import ScotEvents from '@/assets/data/events/SCOT_events.json'
import ccEvents from '@/assets/data/events/CC_events.json'

export default
{
  name: 'ProcedureTimelineEvents',
  data () {
    return {
      collectivite: null,
      procedure: null,
      events: null,
      dialog: false,
      loaded: false,
      icons: {
        mdiBookmark,
        mdiPaperclip,
        mdiChevronLeft,
        mdiDotsVertical
      }
    }
  },
  computed: {
    isEmptyFrise () {
      return this.events.length === 0 || this.events.every(e => !e.type || !e.date_iso)
    },
    isAdmin () {
      if (!this.$user.id) { return false }

      return this.$user.profile?.side === 'etat' ||
        (this.$user.profile?.collectivite_id === this.collectivite.code ||
        this.$user.profile?.collectivite_id === this.collectivite.intercommunaliteCode)
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
        CC: ccEvents
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
        return event.visibility === 'public' || this.isAdmin ||
          (event.from_sudocuh && event.structurant)
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
      console.log('filteredDocumentEvents: ', filteredDocumentEvents)
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

      this.events = await this.getEvents()

      this.loaded = true
    } catch (error) {
      // eslint-disable-next-line no-console
      console.log('ERROR: ', error)
    }
  },
  methods: {
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
    }
  }
}
</script>
