<template>
  <v-card color="info" flat dark>
    <v-card-title>
      <span>Vous souhaitez modifier cette section ?</span>
      <v-spacer />
      <v-btn icon @click="expended = !expended">
        <v-icon>{{ expended ? icons.mdiChevronUp : icons.mdiChevronDown }}</v-icon>
      </v-btn>
    </v-card-title>
    <v-card-text v-show="expended">
      <p>
        Si vous souhaitez ajouter du contenu nous vous conseillons de créer une sous section.
      </p>
      <p>
        Vous pouvez aussi suggérer une modification que nous examinerons.
      </p>
    </v-card-text>
    <v-card-actions v-show="expended">
      <v-spacer />
      <v-dialog v-model="dialog" min-width="600px" max-width="600px">
        <template #activator="{on}">
          <v-snackbar v-model="snackbar">
            Votre demande de changement à été transmise.
          </v-snackbar>
          <v-btn color="white" outlined v-on="on">
            Proposer un changement
          </v-btn>
        </template>
        <v-card min-width="600px" max-width="600px">
          <v-card-title>
            Proposer un changement
          </v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12">
                <v-text-field v-model="change.title" hide-details filled label="Quel est l'objet de votre changement ?" />
              </v-col>
              <v-col cols="12">
                <v-textarea v-model="change.message" hide-details filled label="Expliquez nous le détail du changement." />
              </v-col>
            </v-row>
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn depressed tile text color="primary" @click="dialog = false">
              Annuler
            </v-btn>
            <v-btn depressed tile color="primary" @click="sendChangeRequest">
              Envoyer
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-card-actions>
  </v-card>
</template>

<script>
import axios from 'axios'
import { mdiChevronDown, mdiChevronUp } from '@mdi/js'

export default {
  props: {
    section: {
      type: Object,
      required: true
    },
    gitRef: {
      type: String,
      required: true
    }
  },
  data () {
    return {
      icons: {
        mdiChevronDown, mdiChevronUp
      },
      dialog: false,
      change: {
        email: this.$user.email,
        title: '',
        message: ''
      },
      expended: false,
      snackbar: false
    }
  },
  methods: {
    sendChangeRequest () {
      axios({
        url: '/api/admin/help/pac',
        method: 'post',
        data: Object.assign({
          path: this.section.path,
          ref: this.gitRef
        }, this.change)
      })

      this.change = {
        email: this.$user.email,
        title: '',
        message: ''
      }

      this.dialog = false
      this.snackbar = true
    }
  }
}
</script>
