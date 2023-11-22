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
          <div class="ml-auto">
            <v-btn color="primary" class="mr-2" outlined>
              Ajouter une procédure secondaire
            </v-btn>
            <v-btn depressed nuxt color="primary" :to="{name: 'frise-procedureId-add', params: {procedureId: $route.params.procedureId}}">
              Ajouter un événement
            </v-btn>
            <v-menu>
              <template #activator="{ on, attrs }">
                <v-btn icon color="primary" v-bind="attrs" v-on="on">
                  <v-icon> {{ icons.mdiDotsVertical }}</v-icon>
                </v-btn>
              </template>

              <v-list>
                <v-list-item>
                  <v-list-item-title @click="deleteProcedure">
                    Supprimer
                  </v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </div>
        </div>
      </v-col>
    </v-row>
    <v-row v-if="loaded">
      <v-col cols="12">
        <v-card outlined class="mb-16">
          <v-container>
            <v-row>
              <v-col cols="9">
                <FriseEventCard :event="recommendedEvents[0]" suggestion />
                <FriseEventCard
                  v-for="event in events"
                  :id="`event-${event.id}`"
                  :key="event.id"
                  :event="event"
                />
              </v-col>
              <v-col cols="3" class="my-6">
                <p class="font-weight-bold">
                  Événements clés
                </p>
                <p>
                  <v-chip label color="grey darken-1">
                    <v-icon color="grey darken-2" class="mr-2">
                      {{ icons.mdiBookmark }}
                    </v-icon>
                    test
                  </v-chip>
                </p>

                <p class="font-weight-bold">
                  Ressources
                </p>
                <p>
                  <v-chip label color="grey darken-1">
                    <v-icon color="grey darken-2" class="mr-2">
                      {{ icons.mdiPaperclip }}
                    </v-icon>
                    test
                  </v-chip>
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
import documentEvents from '@/assets/data/DU_events.json'
export default
{
  name: 'ProcedureTimelineEvents',
  data () {
    return {
      loaded: false,
      collectivite: null,
      procedure: null,
      events: [],
      documentEvents,
      icons: {
        mdiBookmark,
        mdiPaperclip,
        mdiChevronLeft,
        mdiDotsVertical
      }
    }
  },
  computed: {
    backToCollectivite () {
      console.log(this.collectivite, ' this.$user: ', this.$user)
      if (this.$user.id && this.$user.scope && this.$user.scope.dept) {
        return `/ddt/${this.collectivite.departementCode}/collectivites/${this.collectivite.code}`
      } else {
        return `/collectivites/${this.collectivite.code}`
      }
    },
    isVerified () {
      return this.$user?.profile?.side === 'etat' && this.$user?.profile?.verified
    },
    recommendedEvents () {
      if (this.events && this.events.length < 1) {
        return [this.documentEvents[0]]
      }
      const lastEventType = this.documentEvents.find((event) => {
        console.log('event: ', event, ' this.events: ', this.events)
        return this.events[0].type === event.name
      })
      const lastEventOrder = lastEventType ? lastEventType.order : -1

      const recommendedEvents = [
        this.findRecommendedEventType(lastEventOrder, 2),
        this.findRecommendedEventType(lastEventOrder, 1)
      ]

      return recommendedEvents.filter(e => !!e)
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
      this.loaded = true
    } catch (error) {
      // eslint-disable-next-line no-console
      console.log('ERROR: ', error)
    }
  },
  methods: {
    deleteProcedure () {
      console.log('Delete procedure')
    },
    findRecommendedEventType (order, priority) {
      return this.documentEvents.find((eventType) => {
        return eventType.recommended === priority && eventType.order > order
      })
    },
    async getEvents () {
      const { data: events, error: errorEvents } = await this.$supabase.from('doc_frise_events').select('*').eq('procedure_id', this.$route.params.procedureId)
      if (errorEvents) { throw errorEvents }
      this.events = events
    }
  }
}
</script>
