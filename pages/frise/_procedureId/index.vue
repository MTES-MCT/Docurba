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
        <v-btn v-if="$user?.profile?.side === 'etat'" color="primary" class="mr-2" outlined>
          Ajouter une procédure secondaire
        </v-btn>
        <v-btn depressed nuxt color="primary" :to="{name: 'frise-procedureId-add', params: {procedureId: $route.params.procedureId}, query:{typeDu: procedure.doc_type}}">
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
                <FriseEventCard v-if="$user?.id && recommendedEvents && recommendedEvents[0]" :event="recommendedEvents[0]" suggestion @addSuggestedEvent="addSuggestedEvent" />
                <FriseEventCard
                  v-for="event in enrichedEvents"
                  :id="`event-${event.id}`"
                  :key="event.id"
                  :event="event"
                  :type-du="procedure.doc_type"
                />
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
                          @click="scrollToStructurant(eventStructurant.type)"
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
import { mdiBookmark, mdiPaperclip, mdiChevronLeft, mdiDotsVertical } from '@mdi/js'

import slugify from 'slugify'
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
      events: [],
      dialog: false,
      icons: {
        mdiBookmark,
        mdiPaperclip,
        mdiChevronLeft,
        mdiDotsVertical
      }
    }
  },
  computed: {
    loaded () {
      return this.procedure && this.collectivite && this.eventsStructurants
    },
    documentEvents () {
      console.log('this.procedure.doc_type: ', this.procedure.doc_type)
      const documentsEvents = {
        PLU: PluEvents,
        SCOT: ScotEvents,
        CC: ccEvents,
        POS: PluEvents
      }
      return documentsEvents[this.procedure.doc_type]
    },
    eventsStructurants () {
      return this.enrichedEvents.filter(e => e.structurant)
    },
    enrichedEvents () {
      return this.events.map((event) => {
        const ev = this.documentEvents.find(x => x.name === event.type)
        return { ...event, structurant: !!ev?.structurant }
      })
    },
    attachments () {
      return this.events.map(e => e.attachements).flat()
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
    recommendedEvents () {
      console.log('TEST: ', this.documentEvents, ' this.internalProcedureType: ', this.internalProcedureType)
      const filteredDocumentEvents = this.documentEvents?.filter((e) => {
        return e.scope_sugg.includes(this.internalProcedureType)
      })
      if (!filteredDocumentEvents) { return null }
      if (this.events && this.events.length < 1) {
        console.log('HERE: ', filteredDocumentEvents[0])
        return [filteredDocumentEvents[0]]
      }
      const lastEventType = filteredDocumentEvents.find((event) => {
        return this.events[0].type === event.name
      })
      console.log('lastEventType: ', lastEventType, ' this.events[0].type: ', this.events[0].type, ' test: ', filteredDocumentEvents)
      const lastEventOrder = lastEventType ? lastEventType.order : -1

      const recommendedEvents = [
        this.findRecommendedEventType(lastEventOrder, 2),
        this.findRecommendedEventType(lastEventOrder, 1)
      ]
      console.log('recommendedEvents: ', recommendedEvents)
      return recommendedEvents.filter(e => !!e)
    },
    internalProcedureType () {
      const isIntercommunal = this.procedure.current_perimetre.length > 1
      const secondairesTypes = {
        'Révision à modalité simplifiée ou Révision allégée': 'rms',
        Modification: 'm',
        'Modification simplifiée': 'ms',
        'Mise en comptabilité': 'mc',
        'Mise à jour': 'mj'
      }

      if (secondairesTypes[this.procedure.type]) { return secondairesTypes[this.procedure.type] }
      if (['Elaboration', 'Modification'].includes(this.procedure.type)) {
        if (isIntercommunal && this.procedure.doc_type !== 'CC') { return 'ppi' } else { return 'pp' }
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

      const { data: procedure, error: errorProcedure } = await this.$supabase.from('procedures').select('*').eq('id', this.$route.params.procedureId)
      this.procedure = procedure[0]
      this.collectivite = (await axios({ url: `/api/geo/collectivites/${this.procedure.collectivite_porteuse_id}` })).data
      if (errorProcedure) { throw errorProcedure }
      await this.getEvents()
    } catch (error) {
      // eslint-disable-next-line no-console
      console.log('ERROR: ', error)
    }
  },
  methods: {
    scrollToStructurant (clickedEvent) {
      console.log('Scroll: ', clickedEvent)
      this.$vuetify.goTo(`#${slugify(clickedEvent, { remove: /[*+~.()'"!:@]/g })}`)
    },
    addSuggestedEvent (eventName) {
      this.$router.push(`/frise/${this.procedure.id}/add?eventType=${eventName}&typeDu=${this.procedure.doc_type}`)
    },
    async  archiveProcedure (idProcedure) {
      try {
        console.log('idProcedure to archive: ', idProcedure)
        const { error } = await this.$supabase
          .from('procedures')
          .update({ archived: true })
          .eq('id', idProcedure)

        if (error) { throw error }
        this.$emit('delete', idProcedure)
        this.dialog = false
      } catch (error) {
        console.log(error)
      }
    },
    findRecommendedEventType (order, priority) {
      return this.documentEvents.find((eventType) => {
        return eventType.order > order
      })
    },
    async getEvents () {
      const { data: events, error: errorEvents } = await this.$supabase.from('doc_frise_events')
        .select('*, profiles(*)')
        .eq('procedure_id', this.$route.params.procedureId)
        .order('date_iso', { ascending: false })
      if (errorEvents) { throw errorEvents }
      this.events = events
    }
  }
}
</script>
