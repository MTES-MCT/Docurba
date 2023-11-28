<template>
  <v-row v-show="!ignore" class=" align-center justify-center ma-2">
    <v-col cols="auto">
      <v-chip v-if="!suggestion" class="font-weight-bold" color="alt-beige" label>
        {{ formatDate }}
      </v-chip>
    </v-col>
    <v-col cols="">
      <div v-if="suggestion" class="primary--text mb-1">
        Evenement suggéré
      </div>
      <v-card :outlined="!suggestion" flat :color="suggestion ? 'primary lighten-4': ''">
        <v-card-title class="font-weight-bold d-flex flex-nowrap">
          <div class="break-word flex-grow-0 d-flex flex-wrap align-self-start">
            {{ event.type || event.name }}
            <!-- <v-icon color="grey darken-2">
                  {{ icons.mdiBookmark }}
                </v-icon> -->
            <v-chip v-if="!suggestion && !event.is_valid" class="mr-2 font-weight-bold text-uppercase" color="error" label>
              invalide
            </v-chip>
          </div>
          <div v-if="!suggestion" class=" ml-auto flex-shrink-1 d-flex align-self-start">
            <v-chip class="mr-2 font-weight-bold text-uppercase" dark color="grey darken-2" label>
              {{ event.visibility }}
            </v-chip>
            <v-chip class="text-uppercase" :color="creator.background" label>
              {{ event.profiles?.poste || event.profiles?.side || creator.values[0] }}
            </v-chip>
            <v-btn class="ml-2" text icon :to="`/frise/${event.procedure_id}/${event.id}?typeDu=${typeDu}`">
              <v-icon color="grey darken-2">
                {{ icons.mdiPencil }}
              </v-icon>
            </v-btn>
          </div>

          <div v-if="suggestion" class="d-flex ml-auto">
            <v-btn outlined color="primary" depressed class="mx-2" @click="ignore = true">
              Ignorer
            </v-btn>
            <v-btn color="primary" depressed>
              Ajouter
            </v-btn>
          </div>
        </v-card-title>
        <v-card-text v-if="event.commentaire || event.description">
          {{ event.commentaire || event.description }}
        </v-card-text>
        <v-card-actions v-if="event.attachements?.length">
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
            {{ attachement.name }}
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
      console.log('event ttt: ', this.event, this.event.profiles)
      let actor = this.event.profiles?.side || 'docurba'
      if (this.event.from_sudocuh) { actor = 'sudocu' }
      console.log('actor: ', actor)
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
      console.log('CHOSEN: ', path)
      const { data } = await this.$supabase.storage.from('doc-events-attachements').download(path)

      const link = this.$refs[`file-${attachement.id}`][0]
      link.href = URL.createObjectURL(data)
      link.click()
    }
  }
}
</script>
