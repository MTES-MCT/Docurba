
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
          <v-expansion-panels v-else flat>
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
                          </v-icon> OUI
                        </v-chip>
                      </div>
                    </div>
                    <div class="ml-7">
                      <div class="mention-grey--text mb-4">
                        Année
                      </div>
                      <div>
                        2019
                      </div>
                    </div>
                    <div class="ml-7">
                      <div class="mention-grey--text mb-4">
                        Catégorie
                      </div>
                      <div>
                        2
                      </div>
                    </div>
                    <div class="ml-7">
                      <div class="mention-grey--text mb-4">
                        Montant total
                      </div>
                      <div>
                        1000€
                      </div>
                    </div>
                    <div class="ml-7">
                      <div class="mention-grey--text mb-4">
                        Montant versé
                      </div>
                      <div>
                        1000€
                      </div>
                    </div>
                  </v-col>
                </v-row>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <FriseDgdVersStepPanel />
                <v-btn outlined color="error" @click="deleteVersement(versement)">
                  Supprimer ce versement
                </v-btn>
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
                <div>
                  Commentaire général
                </div>
                <v-btn color="primary" text>
                  Ajouter un commentaire
                </v-btn>
              </div>
            </v-col>
          </v-row>
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
      showVersementForm: false,
      versements: [],
      date: null,
      trip: {
        name: '',
        location: null,
        start: null,
        end: null
      },
      locations: ['Australia', 'Barbados', 'Chile', 'Denmark', 'Ecuador', 'France'],
      headers: [
        {
          text: 'Étape des versements',
          align: 'start',
          sortable: false,
          value: 'name'
        },
        { text: 'Montant', value: 'calories' },
        { text: 'Versement effectué', value: 'fat' },
        { text: 'Date', value: 'carbs' },
        { text: 'Catégorie', value: 'protein' }

      ],
      desserts: [],
      dialog: true,
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
    deleteVersement (versement) {
      console.log('Delete versement')
    },
    addNewVersement (versement) {
      this.versements = [...this.versements, versement]
      console.log('versements: ', this.versements)
    }
  }
}
</script>

<style>
#dgd-dialog .v-expansion-panel-content > .v-expansion-panel-content__wrap{
  padding: 0px!important;
}
</style>
