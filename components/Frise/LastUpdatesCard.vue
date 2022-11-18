<template>
  <v-card outlined color="alt-beige">
    <v-card-title>Dernières modifications</v-card-title>
    <v-card-text>
      <v-row>
        <v-col v-for="update in lastUpdates" :key="update.eventId" cols="12">
          <v-card flat>
            <v-card-subtitle class="text-right">
              {{ update.date }}
            </v-card-subtitle>
            <v-card-text>
              <v-divider class="pb-4" />
              Evénement <b>{{ update.type }}</b>: <b>{{ update.eventType }}</b>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script>
import { sortBy } from 'lodash'

export default {
  props: {
    events: {
      type: Array,
      required: true
    }
  },
  computed: {
    lastUpdates () {
      const lastUpdates = sortBy(this.events, (event) => {
        console.log(event.updated_at, this.$dayjs(event.updated_at).valueOf())

        return -this.$dayjs(event.updated_at).valueOf()
      }).slice(0, 4)

      console.log(lastUpdates)

      return lastUpdates.map((event) => {
        return {
          type: event.created_at === event.updated_at ? 'créé' : 'modifié',
          eventType: event.type,
          date: this.$dayjs(event.updated_at).format('DD MMMM'),
          eventId: event.id
        }
      })
    }
  }
}
</script>
