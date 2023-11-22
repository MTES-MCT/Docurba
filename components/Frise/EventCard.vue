<template>
  <div class="d-flex align-center justify-center ma-6">
    <v-chip v-if="!suggestion" class="mr-2 font-weight-bold" style="width:83px" color="alt-beige" label>
      {{ formatDate }}
    </v-chip>
    <div v-else class="mr-6" style="width:84px" />
    <div class="flex-grow-1">
      <div v-if="suggestion" class="primary--text mb-1">
        Evenement suggéré
      </div>
      <v-card :outlined="!suggestion" flat :color="suggestion ? 'primary lighten-4': ''">
        <v-card-title class="font-weight-bold">
          <div class="d-flex break-word">
            <div class="d-flex">
              <div>
                {{ event.type || event.name }}
              <!-- <v-chip class="mr-2 font-weight-bold" color="error" label>
          {{ event.status }}
        </v-chip> -->
              </div>
              <div>
                <!-- <v-chip class="text-uppercase" label>
                  test
                </v-chip> -->
              </div>
            </div>

            <div v-if="suggestion" class="d-flex ml-auto">
              <v-btn outlined color="primary" depressed class="mx-2">
                Ignorer
              </v-btn>
              <v-btn color="primary" depressed>
                Ajouter
              </v-btn>
            </div>
          </div>
        </v-card-title>
        <v-card-text v-if="event.commentaire || event.description">
          {{ event.commentaire || event.description }}
        </v-card-text>
        <v-card-actions v-if="attachements">
          <v-chip
            v-for="attachement in attachements"
            :key="attachement.id"
            outlined
            color="primary"
            class="mr-2"
            @click="downloadFile(attachement)"
          >
            <v-icon class="pr-2">
              {{ icons.mdiFile }}
            </v-icon>
            {{ attachement.name }}
            <v-icon color="primary" class="pl-2">
              {{ icons.mdiDownload }}
            </v-icon>
          </v-chip>
          <a
            v-for="attachement in attachements"
            :key="`file-link-${attachement.id}`"
            :ref="`file-${attachement.id}`"
            class="d-none"
            :download="attachement.name"
          />
        </v-card-actions>
      </v-card>
    </div>
  </div>
</template>

<script>
import { mdiDotsHorizontal, mdiPencil, mdiFile, mdiDownload } from '@mdi/js'
import actors from '@/assets/friseActors.json'

export default {
  props: {
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
      icons: { mdiDotsHorizontal, mdiPencil, mdiFile, mdiDownload }
    }
  },
  computed: {
    formatDate () {
      return this.$dayjs(this.event.date_iso).format('DD/MM/YY')
    }
  },
  methods: {
    getActor (val) {
      return actors.find((actor) => {
        return actor.values.includes(val)
      })
    },
    async downloadFile (attachement) {
      // TODO: Handle link type
      console.log('this.event.from_sudocuh: ', this.event.from_sudocuh)
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
