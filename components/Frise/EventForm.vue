<template>
  <v-row v-if="!loading">
    <v-col cols="12">
      <v-card outlined>
        <v-card-title class="text-h3 black--text">
          Eléments obligatoires
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="6">
              <v-row>
                <v-col cols="10">
                  <!-- <v-text-field v-model="event.type" hide-details filled label="Type" /> -->
                  <FriseEventSelector v-model="event.type" />
                </v-col>
                <v-col cols="6">
                  <VTextDatePicker v-model="event.date_iso" label="Date" />
                </v-col>
                <v-col cols="12">
                  <v-textarea
                    v-model="event.description"
                    label="Description courte"
                    filled
                    placeholder="Vous pouvez inscrire ici une description qui sera visible par tous"
                  />
                </v-col>
              </v-row>
            </v-col>
            <v-col cols="6">
              <span class="label">Partie prenantes</span>
              <v-checkbox
                v-for="actor in actorsList"
                :key="actor"
                v-model="event.actors"
                :value="actor"
                :label="actor"
                hide-details
              />
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </v-col>
    <v-col cols="12">
      <FriseEventAttachementsCard v-model="attachements" />
    </v-col>
    <v-col cols="12">
      <v-card outlined>
        <v-card-text>
          <v-row>
            <v-spacer />
            <v-col cols="auto">
              <v-btn color="primary" outlined tile @click="$emit('cancel')">
                Annuler
              </v-btn>
            </v-col>
            <v-col v-if="eventId" cols="auto">
              <v-dialog v-model="deleteModal" max-width="320px">
                <template #activator="{on}">
                  <v-btn tile outlined color="error" v-on="on">
                    Supprimer
                  </v-btn>
                </template>
                <v-card>
                  <v-card-title>
                    Confirmer la suppression ?
                  </v-card-title>
                  <v-card-text>
                    Cette action est définitive.
                  </v-card-text>
                  <v-card-actions>
                    <v-spacer />
                    <v-btn color="primary" outlined @click="deleteModal = false">
                      Annuler
                    </v-btn>
                    <v-btn color="error" @click="deleteEvent">
                      <v-icon>{{ icons.mdiTrashCan }}</v-icon> Supprimer
                    </v-btn>
                  </v-card-actions>
                </v-card>
              </v-dialog>
            </v-col>
            <v-col cols="auto">
              <v-btn :loading="saving" color="primary" tile @click="saveEvent">
                {{ eventId ? 'Modifier' : 'Créer' }}
              </v-btn>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
  <VGlobalLoader v-else />
</template>

<script>
import { mdiTrashCan } from '@mdi/js'

export default {
  props: {
    projectId: {
      type: String,
      default () {
        return this.$route.params.projectId
      }
    },
    eventId: {
      type: String,
      default () {
        return this.$route.params.eventId
      }
    }
  },
  data () {
    const defaultEvent = {
      type: this.$route.query.eventType || '',
      date_iso: this.$dayjs().format('YYYY-MM-DD'),
      description: '',
      actors: [],
      attachements: []
    }

    return {
      defaultEvent,
      event: Object.assign({}, defaultEvent, {
        description: this.$isDev ? 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.' : '',
        project_id: this.projectId
      }),
      attachements: [],
      icons: {
        mdiTrashCan
      },
      loading: !!this.eventId,
      saving: false,
      deleteModal: false,
      actorsList: ['Collectivité', 'DDT', 'Bureau d’étude']
    }
  },
  async mounted () {
    if (this.eventId) {
      // fetch event
      const { data: events } = await this.$supabase.from('doc_frise_events').select('*').eq('id', this.eventId)
      this.event = Object.assign({}, events[0])
      this.attachements = this.event.attachements || []
    }

    this.loading = false
  },
  methods: {
    async saveAttachements (eventId) {
      const modifiedAtatchements = this.attachements.filter((attachement) => {
        return attachement.state !== 'old'
      })

      await Promise.all(modifiedAtatchements.map((attachement) => {
        if (attachement.state === 'new') {
          return this.$supabase.storage
            .from('doc-events-attachements')
            .upload(`${this.projectId}/${eventId}/${attachement.id}`, attachement.file)
        } else if (attachement.state === 'removed') {
          // console.log(`${this.projectId}/${eventId}/${attachement.id}`)
          return this.$supabase.storage.from('doc-events-attachements')
            .remove([`${this.projectId}/${eventId}/${attachement.id}`])
        } else { return null }
      }))
    },
    async saveEvent () {
      this.saving = true

      this.event.attachements = this.attachements.filter((attachement) => {
        return attachement.state !== 'removed'
      }).map((attachement) => {
        const { id, name } = attachement
        return { id, name }
      })

      if (this.eventId) {
        await this.$supabase.from('doc_frise_events').update(this.event).eq('id', this.eventId)
        await this.saveAttachements(this.eventId)
      } else {
        const { data: savedEvents } = await this.$supabase.from('doc_frise_events').insert([this.event]).select()
        await this.saveAttachements(savedEvents[0].id)
      }

      this.saving = false
      this.$emit('saved')
    },
    async deleteEvent () {
      await this.$supabase.from('doc_frise_events').delete().eq('id', this.eventId)
      this.$emit('saved')
    }
  }
}
</script>
