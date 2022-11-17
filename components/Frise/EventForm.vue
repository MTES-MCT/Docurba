<template>
  <v-row>
    <v-col cols="12">
      <v-card outlined>
        <v-card-title>Eléments obligatoires</v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="6">
              <v-row>
                <v-col cols="12">
                  <v-text-field v-model="event.type" hide-details filled label="Type" />
                </v-col>
                <v-col cols="12">
                  <VTextDatePicker v-model="event.date" label="Date" />
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
          </v-row>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>

<script>
import dayjs from 'dayjs'

const defaultEvent = {
  type: '',
  date: dayjs().format('YYYY-MM-DD'),
  description: '',
  actors: []
}

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
    return {
      event: Object.assign({}, defaultEvent)
    }
  },
  // async mounted () {
  //   if(this.eventId) {
  //     // fetch event
  //   }
  // },
  methods: {
    saveEvent () {
      if (this.eventId) {
        this.$supabase.from('doc_frise_events').update(this.event).eq('id', this.eventId)
      } else {
        this.$supabase.from('doc_frise_events').insert([this.event])
      }
    }
  }
}
</script>
