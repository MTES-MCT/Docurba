<template>
  <v-card flat class="event-card">
    <v-menu>
      <template #activator="{on}">
        <v-btn absolute top right icon v-on="on">
          <v-icon>{{ icons.mdiDotsHorizontal }}</v-icon>
        </v-btn>
      </template>
      <v-list>
        <v-list-item nuxt :to="`/projets/${event.project_id}/frise/${event.id}`">
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
    <v-card-title>{{ event.type }}</v-card-title>
    <v-card-text>{{ event.description }}</v-card-text>
  </v-card>
</template>

<script>
import { mdiDotsHorizontal, mdiPencil } from '@mdi/js'
import actors from '@/assets/friseActors.json'

export default {
  props: {
    event: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      icons: { mdiDotsHorizontal, mdiPencil }
    }
  },
  methods: {
    getActor (val) {
      return actors.find((actor) => {
        return actor.values.includes(val)
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.event-card {
  border: 1px solid #000091
}
</style>
