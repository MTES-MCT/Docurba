<template>
  <v-dialog v-model="dialog" min-width="600px" max-width="600px">
    <template #activator="{ on }">
      <slot>
        <v-btn text v-on="on">
          Besoins d'aide ?
        </v-btn>
      </slot>
    </template>
    <v-card min-width="600px" max-width="600px">
      <v-card-title>
        Demandez de l'aide à l'équipe Docurba
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12">
            <v-text-field v-model="help.email" hide-details filled label="Votre email" />
          </v-col>
          <v-col cols="12">
            <v-text-field v-model="help.title" hide-details filled label="Comment pouvons-nous vous aider ?" />
          </v-col>
          <v-col cols="12">
            <v-textarea v-model="help.message" hide-details filled label="Laissez nous un message." />
          </v-col>
        </v-row>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn text color="primary" @click="dialog = false">
          Annuler
        </v-btn>
        <v-btn color="primary" @click="sendRequest">
          Envoyer
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import axios from 'axios'

export default {
  props: {
    value: {
      type: Boolean,
      required: true
    }
  },
  data () {
    return {
      help: {
        email: this.$user ? this.$user.email : '',
        title: '',
        message: ''
      }
    }
  },
  computed: {
    dialog: {
      get () {
        return this.value
      },
      set (val) {
        this.$emit('input', val)
      }
    }
  },
  methods: {
    sendRequest () {
      axios({
        url: '/api/admin/help',
        method: 'post',
        data: this.help
      })

      this.help = {
        email: this.$user ? this.$user.email : '',
        title: '',
        message: ''
      }

      this.$emit('helpSent')
    }
  }
}
</script>
