<template>
  <v-row v-show="!ignore" class=" align-center justify-center ma-2">
    <v-col cols="auto">
      <v-chip v-if="!suggestion" class="font-weight-bold" color="alt-beige" label>
        {{ formatDate }}
      </v-chip>
    </v-col>
    <v-col cols="10">
      <div v-if="suggestion" class="primary--text mb-1">
        Evénement suggéré
      </div>
      <!-- The event- is here to prevent errors since ids should start with a letter: https://developer.mozilla.org/en-US/docs/Web/HTML/Global_attributes/id -->
      <v-card :id="`event-${event.id}`" :outlined="!suggestion" flat :color="suggestion ? 'primary lighten-4': ''">
        <v-card-title class="font-weight-bold d-flex flex-nowrap">
          <div class="break-word flex-grow-0 d-flex flex-wrap align-self-start mr-4">
            <div>
              {{ event.type || event.name }}
              <v-icon v-if="event.structurant" color="grey darken-2">
                {{ icons.mdiBookmark }}
              </v-icon>
            </div>

            <v-chip v-if="!suggestion && !event.is_valid" class="ml-2 font-weight-bold text-uppercase" color="error" label>
              invalide
            </v-chip>
          </div>
          <div v-if="!suggestion" class=" ml-auto flex-shrink-1 d-flex align-self-start">
            <v-tooltip v-if="event.visibility === 'private'" bottom>
              <template #activator="{ on, attrs }">
                <v-chip
                  class="mr-2 font-weight-bold text-uppercase"
                  dark
                  color="grey darken-2"
                  label
                  v-bind="attrs"
                  v-on="on"
                >
                  {{ event.visibility === 'private' ? 'privé' : '' }}
                </v-chip>
              </template>
              Cet événement n’est visible que pour la collectivité et les services de l’État.
            </v-tooltip>
            <v-tooltip bottom>
              <template #activator="{ on, attrs }">
                <v-chip
                  class="text-uppercase"
                  :color="creator.background"
                  label
                  v-bind="attrs"
                  v-on="on"
                >
                  {{ event.profiles?.poste || event.profiles?.side || creator.values[0] }}
                </v-chip>
              </template>
              Cet événement a été ajouté par  {{ event.profiles?.poste || event.profiles?.side || creator.values[0] }}.
            </v-tooltip>
            <v-btn v-if="creator.values[0] != 'sudocu' && ($user.profile?.side === 'etat' || event.profile_id=== $user.id )" class="ml-2" text icon :to="`/frise/${event.procedure_id}/${event.id}?typeDu=${typeDu}`">
              <v-icon color="grey darken-2">
                {{ icons.mdiPencil }}
              </v-icon>
            </v-btn>
          </div>

          <div v-if="suggestion" class="d-flex ml-auto">
            <v-btn outlined color="primary" depressed class="mx-2" @click="ignore = true">
              Ignorer
            </v-btn>
            <v-btn color="primary" depressed @click="$emit('addSuggestedEvent', event.name)">
              Ajouter
            </v-btn>
          </div>
        </v-card-title>
        <v-card-text v-if="$user.id && (event.commentaire || event.description)">
          {{ event.commentaire || event.description }}
        </v-card-text>
        <v-card-actions v-if="event.attachements?.length" class="d-flex">
          <v-chip
            v-for="attachement in event.attachements"
            :key="attachement.id"
            label
            class="mr-2"

            @click="downloadFile(attachement)"
          >
            <v-icon class="pr-2" color="grey darken-2">
              {{ icons.mdiPaperclip }}
            </v-icon>
            <span class="text-truncate">{{ attachement.name }}</span>
          </v-chip>
          <a
            v-for="attachement in event.attachements"
            :key="`file-link-${attachement.id}`"
            :ref="`file-${attachement.id}`"
            class="d-none"
            :download="attachement.name"
          />
        </v-card-actions>
      </v-card>
    </v-col>
  </v-row>
</template>

<script>
import { mdiPencil, mdiPaperclip, mdiBookmark } from '@mdi/js'
import actors from '@/assets/friseActors.json'

export default {
  props: {
    typeDu: {
      type: String,
      default: () => null
    },
    censored: {
      type: Boolean,
      default: () => true
    },
    suggestion: {
      type: Boolean,
      default: () => false
    },
    event: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      ignore: false,
      icons: { mdiPencil, mdiPaperclip, mdiBookmark }
    }
  },
  computed: {
    creator () {
      let actor = this.event.profiles?.side || 'docurba'
      if (this.event.from_sudocuh) { actor = 'sudocu' }
      return actors.find((e) => {
        return e.values.includes(actor)
      })
    },
    formatDate () {
      return this.$dayjs(this.event.date_iso).format('DD/MM/YY')
    }
  },
  methods: {
    async downloadFile (attachement) {
      // TODO: Handle link type
      const path = this.event.from_sudocuh ? attachement.id : `${this.event.project_id}/${this.event.id}/${attachement.id}`
      const { data } = await this.$supabase.storage.from('doc-events-attachements').download(path)

      const link = this.$refs[`file-${attachement.id}`][0]
      link.href = URL.createObjectURL(data)
      link.click()
    }
  }
}
</script>
