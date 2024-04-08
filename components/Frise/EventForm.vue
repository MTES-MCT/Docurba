<template>
  <v-row v-if="!loading" class="mb-8">
    <v-col cols="12">
      <v-card outlined class="pa-4">
        <validation-observer ref="observerEventForm" v-slot="{ handleSubmit }">
          <form @submit.prevent="handleSubmit(saveEvent)">
            <v-container>
              <v-row>
                <v-col cols="12">
                  <FriseEventSelector v-model="event.type" :procedure="procedure" />
                </v-col>
                <v-col cols="12">
                  <VTextDatePicker v-model="event.date_iso" label="Date de l'évènement" />
                </v-col>
                <v-col cols="12">
                  <v-textarea
                    v-model="event.description"
                    label="Description"
                    filled
                    hide-details=""
                    placeholder="Vous pouvez inscrire ici une description qui sera visible par tous"
                  />
                </v-col>
                <v-col cols="12">
                  <v-select
                    v-model="event.visibility"
                    persistent-hint
                    hint="Les événements privés sont visibles uniquement par la DDT et la collectivité en charge de la procédure, ainsi que par le bureau d’études le cas échéant."
                    label="Visibilité de l'évènement"
                    filled
                    :items="[{value: 'public', text: 'Publique'}, {value: 'private', text: 'Privé'}]"
                  />
                </v-col>
                <v-col cols="12">
                  <FriseEventAttachementsCard v-model="attachements" />
                </v-col>
              </v-row>

              <v-col cols="12">
                <v-row>
                  <v-spacer />
                  <v-col cols="auto">
                    <v-btn color="primary" outlined tile :to="`/frise/${procedure.id}`">
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
                    <v-btn type="submit" :loading="saving" color="primary" tile>
                      {{ eventId ? 'Modifier' : 'Créer' }}
                    </v-btn>
                  </v-col>
                </v-row>
              </v-col>
            </v-container>
          </form>
        </validation-observer>
      </v-card>
    </v-col>
  </v-row>
  <VGlobalLoader v-else />
</template>

<script>
import axios from 'axios'
import { mdiTrashCan } from '@mdi/js'
import FormInput from '@/mixins/FormInput.js'
export default {
  mixins: [FormInput],
  props: {
    typeDu: {
      type: String,
      required: true
    },
    procedure: {
      type: Object,
      required: true
    },
    value: {
      type: Object,
      default () {
        return {}
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
      attachements: [],
      visibility: 'private'
    }

    return {
      defaultEvent,
      event: Object.assign({}, defaultEvent, {
        description: this.$isDev ? 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.' : '',
        project_id: this.procedure.project_id,
        procedure_id: this.procedure.id,
        test: !!this.$isDev
      }, this.value),
      attachements: this.value?.attachements ? this.value?.attachements : [],
      icons: { mdiTrashCan },
      loading: !!this.eventId,
      saving: false,
      deleteModal: false
    }
  },
  mounted () {
    this.loading = false
  },
  methods: {
    async saveAttachements (eventId) {
      const modifiedAttachements = this.attachements.filter((attachement) => {
        return attachement.state !== 'old'
      })

      await Promise.all(modifiedAttachements.map((attachement) => {
        if (attachement.state === 'new') {
          return this.$supabase.storage.from('doc-events-attachements').upload(`${this.procedure.project_id}/${eventId}/${attachement.id}`, attachement.file)
        } else if (attachement.state === 'removed') {
          return this.$supabase.storage.from('doc-events-attachements').remove([`${this.procedure.project_id}/${eventId}/${attachement.id}`])
        } else { return null }
      }))
    },
    async saveEvent () {
      try {
        this.saving = true

        this.event.attachements = this.attachements.filter(attachement => attachement.state !== 'removed')
          .map(attachement => ({ id: attachement.id, name: attachement.name }))

        const upsertEvent = { ...this.event, profile_id: this.$user.id }
        if (this.eventId) {
          await this.$supabase.from('doc_frise_events').update(upsertEvent).eq('id', this.eventId)
          await this.saveAttachements(this.eventId)
        } else {
          const { data: savedEvents } = await this.$supabase.from('doc_frise_events').insert(upsertEvent).select()
          await this.saveAttachements(savedEvents[0].id)
        }

        this.$analytics({
          category: 'frp',
          name: this.eventId ? 'update_event' : 'create_event',
          value: this.event.type
        })

        axios({
          url: '/api/slack/notify/frp',
          method: 'post',
          data: {
            userData: this.$user.profile,
            eventData: upsertEvent,
            procedureData: this.procedure
          }
        })

        this.saving = false
        this.$router.push(`/frise/${this.procedure.id}`)
      } catch (error) {
        console.log(error)
      }
    },
    async deleteEvent () {
      this.saveAttachements(this.eventId)
      await this.$supabase.from('doc_frise_events').delete().eq('id', this.eventId)
      this.$router.push({ name: 'frise-procedureId', params: { procedureId: this.procedure.id }, query: this.$route.query })
    }
  }
}
</script>
