<template>
  <v-card flat class="event-card">
    <v-menu v-if="!event.from_sudocuh">
      <template #activator="{on}">
        <v-btn absolute top right icon v-on="on">
          <v-icon>{{ icons.mdiDotsHorizontal }}</v-icon>
        </v-btn>
      </template>
      <v-list>
        <v-list-item nuxt :to="{name: 'frise-procedureId-eventId', params: {procedureId: $route.params.procedureId, eventId: event.id}}">
          <v-list-item-action>
            <v-icon color="primary">
              {{ icons.mdiPencil }}
            </v-icon>
          </v-list-item-action>
          <v-list-item-title>
            Modifier
          </v-list-item-title>
        </v-list-item>
        <!-- <v-list-item @click="deleteModal = true">
          <v-list-item-action>
            <v-icon color="error">
              {{ icons.mdiTrashCan }}
            </v-icon>
          </v-list-item-action>
          <v-list-item-title>
            Supprimer
          </v-list-item-title>
        </v-list-item> -->
      </v-list>
    </v-menu>
    <v-card-subtitle class="pb-0">
      <v-chip v-if="event.from_sudocuh" small color="success lighten-3">
        Sudocuh
      </v-chip>
      <v-chip
        v-for="actor in event.actors"
        :key="actor"
        label
        small
        outlined
        class="mr-2"
        :color="getActor(actor).color"
        :style="{'background-color': `${getActor(actor).background} !important`}"
      >
        {{ actor }}
      </v-chip>
    </v-card-subtitle>
    <v-card-title>
      {{ event.type }}
    </v-card-title>
    <div />
    <v-card-text v-if="event.commentaire">
      {{ event.commentaire }}
    </v-card-text>
    <v-card-actions>
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
</template>

<script>
import { mdiDotsHorizontal, mdiPencil, mdiFile, mdiDownload } from '@mdi/js'
import actors from '@/assets/friseActors.json'

export default {
  props: {
    event: {
      type: Object,
      required: true
    },
    censored: {
      type: Boolean,
      default: () => true
    }
  },
  data () {
    return {
      icons: { mdiDotsHorizontal, mdiPencil, mdiFile, mdiDownload }
    }
  },
  computed: {
    attachements () {
      if (this.event.from_sudocuh) {
        if (!this.censored || this.event.type === 'Prescription' || this.event.type === "Délibération d'approbation") {
          return this.event.attachements
        } else {
          return []
        }
      } else {
        return this.event.attachements
      }
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

<style lang="scss" scoped>
.event-card {
  border: 1px solid #000091;
}
</style>
