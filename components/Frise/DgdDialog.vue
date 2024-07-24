
<template>
  <v-dialog id="dgd-dialog" v-model="dialog" width="1000">
    <template #activator="{ on, attrs }">
      <v-list-item link v-bind="attrs" v-on="on">
        <v-list-item-title>
          DGD
        </v-list-item-title>
      </v-list-item>
    </template>

    <v-card>
      <div class="text-right pr-2 pt-2">
        <v-btn color="primary" text @click="dialog = false">
          Fermer x
        </v-btn>
      </div>

      <v-card-title class="text-h5 d-flex flex-column font-weight-bold ">
        DGD
      </v-card-title>

      <v-card-text class="pt-4">
        <v-container fluid class="px-0">
          <v-row v-if="(!versements || versements.length === 0) && !showVersementForm">
            <v-col cols="12" class="text-center py-8 typo--text">
              <div class="font-weight-bold text-h5">
                Aucun versement
              </div>
              <div class="mb-4">
                Aucun versement n’a été entré pour cette procédure.
              </div>
              <v-btn depressed color="primary" @click="showVersementForm = true">
                Ajouter un versement
              </v-btn>
            </v-col>
          </v-row>
          <div v-else>
            <v-expansion-panels>
              <v-expansion-panel v-for="(versement, i) in versements" :key="`versement-${i}`">
                <v-expansion-panel-header class="">
                  <v-row>
                    <v-col cols="12" class="d-flex py-6">
                      <div>
                        <div class="mention-grey--text mb-2">
                          Versement terminé
                        </div>
                        <div>
                          <v-chip small label color="success">
                            <v-icon small color="grey">
                              {{ icons.mdiMinusCircle }}
                            </v-icon> NON
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
                          - €
                        </div>
                      </div>
                    </v-col>
                  </v-row>
                </v-expansion-panel-header>
                <v-expansion-panel-content>
                  <FriseDgdVersStepPanel />
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
                          Vous êtes sur le point de supprimer une étape de versement. Cette action est irréversible.
                        </v-card-text>

                        <v-divider />

                        <v-card-actions>
                          <v-btn
                            color="error"
                            depressed
                            @click="deleteVersement(versementIdx)"
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
            </v-expansion-panels>
            <div v-if="showVersementForm">
              <div class="font-weight-bold typo--text mb-1">
                Ajouter un versement
              </div>
              <FriseDgdVersementForm @add="addNewVersement" @save="addNewVersement(arguments[0])" @cancel="showVersementForm = false" />
            </div>
            <v-row>
              <v-col cols="12">
                <div>
                  <div v-if="!showVersementForm" class="mt-6">
                    <v-btn depressed color="primary" @click="showVersementForm = true">
                      Ajouter un versement
                    </v-btn>
                  </div>
                  <div>
                    Commentaire général
                  </div>
                  <v-btn v-if="!showCommentForm" color="primary" text @click="showCommentForm =true">
                    Ajouter un commentaire
                  </v-btn>
                  <div v-else>
                    <InputsEditableText label="Commentaire:" compact />
                  </div>
                </div>
              </v-col>
            </v-row>
          </div>
        </v-container>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>
<script>
import { mdiCheck, mdiClose, mdiDotsVertical, mdiMinusCircle, mdiCheckCircle } from '@mdi/js'

export default
{
  name: 'DgdDialog',
  props: {},
  data () {
    return {
      dialogDeleteVersement: false,
      showCommentForm: false,
      showVersementForm: false,
      versements: [],
      date: null,
      trip: {
        name: '',
        location: null,
        start: null,
        end: null
      },
      dialog: false,
      voletQualitatifRaw: null,
      icons: {
        mdiCheck,
        mdiClose,
        mdiDotsVertical,
        mdiMinusCircle,
        mdiCheckCircle
      }
    }
  },
  computed: {

  },
  async mounted () {

  },
  methods: {
    deleteVersement (versementIdx) {
      console.log('Delete versement')
      this.versements.splice(versementIdx, 1)
      this.dialogDeleteVersement = false
    },
    addNewVersement (versement) {
      this.versements = [...this.versements, versement]
      console.log('versements: ', this.versements)
      this.showVersementForm = false
    }
  }
}
</script>

<style>
#dgd-dialog .v-expansion-panel-content > .v-expansion-panel-content__wrap{
  padding: 0px!important;
}
</style>
