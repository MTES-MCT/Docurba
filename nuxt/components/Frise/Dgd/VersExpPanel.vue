<template>
  <v-expansion-panel :key="`versement-${versement.id}`" :disabled="!!versement.from_sudocu">
    <v-expansion-panel-header>
      <v-row>
        <v-col cols="12" class="d-flex py-6">
          <div>
            <div class="mention-grey--text mb-2">
              Versement terminé
            </div>
            <div>
              <span v-if="versement.from_sudocu">
                -
              </span>
              <v-chip v-else-if="allVersementsDone" small label color="success-light">
                <v-icon small color="success" class="mr-2">
                  {{ icons.mdiCheckCircle }}
                </v-icon>
                <span class="success--text font-weight-bold">OUI</span>
              </v-chip>
              <v-chip v-else small label color="grey">
                <v-icon small color="g800" class="mr-2">
                  {{ icons.mdiMinusCircle }}
                </v-icon>
                <span class="g800--text font-weight-bold">NON</span>
              </v-chip>
            </div>
          </div>
          <div class="ml-7">
            <div class="mention-grey--text mb-4">
              Année
            </div>
            <div>
              {{ versement.year }}
            </div>
          </div>
          <div class="ml-7">
            <div class="mention-grey--text mb-4">
              Catégorie
            </div>
            <div>
              {{ versement.category }}
            </div>
          </div>
          <div class="ml-7">
            <div class="mention-grey--text mb-4">
              Montant total
            </div>
            <div>
              {{ versement.amount }} €
            </div>
          </div>
          <div class="ml-7">
            <div class="mention-grey--text mb-4">
              Montant versé
            </div>
            <div>
              <span v-if="!versement.from_sudocu">
                {{ amoutTransfered }}
              </span>
              <span v-else> - </span>
              €
            </div>
          </div>
        </v-col>
      </v-row>
    </v-expansion-panel-header>
    <v-expansion-panel-content>
      <FriseDgdVersStepPanel
        :versement="versement"
        @save="$emit('save-step')"
        @delete="$emit('delete-step')"
      />
      <div class="mt-10">
        <v-dialog
          v-model="dialogDeleteVersement"
          width="500"
        >
          <template #activator="{ on, attrs }">
            <v-btn
              outlined
              color="error"
              v-bind="attrs"
              v-on="on"
            >
              Supprimer le versement
            </v-btn>
          </template>

          <v-card>
            <v-card-title class="text-h5">
              Confirmer la suppression
            </v-card-title>

            <v-card-text>
              Vous êtes sur le point de supprimer un versement. Cette action est irréversible.
            </v-card-text>

            <v-divider />

            <v-card-actions>
              <v-btn
                color="error"
                depressed
                @click="$emit('delete', versement)"
              >
                Supprimer le versement
              </v-btn>
              <v-btn
                color="primary"
                outlined
                @click="dialogDeleteVersement = false"
              >
                Annuler
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </div>
    </v-expansion-panel-content>
  </v-expansion-panel>
</template>
<script>
import { mdiMinusCircle, mdiCheckCircle } from '@mdi/js'

export default
{
  name: 'VersExpPanel',
  props: {
    versement: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      icons: {
        mdiMinusCircle,
        mdiCheckCircle
      },
      dialogDeleteVersement: false
    }
  },
  computed: {
    amoutTransfered () {
      if (!this.versement.etapes_versement) {
        return '-'
      }

      return this.versement.etapes_versement.reduce((acc, curr) => {
        if (curr.is_done) {
          return acc + curr.amount
        } else {
          return acc
        }
      }, 0)
    },
    allVersementsDone () {
      return this.amoutTransfered >= this.versement.amount
    }
  },
  methods: {
  }
}

</script>
