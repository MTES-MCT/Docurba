
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
      <v-card-title class="text-h5 d-flex flex-column">
        DGD
      </v-card-title>

      <v-card-text class="pt-4">
        <v-container fluid class="px-0">
          <v-expansion-panels flat>
            <v-expansion-panel>
              <v-expansion-panel-header class="red">
                <v-row>
                  <v-col cols="12" class="d-flex">
                    <div>
                      <div class="mention-grey--text mb-2">
                        Versement terminé
                      </div>
                      <div>
                        <v-chip small label color="success">
                          OUI
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
                <v-divider />
                <v-data-table

                  :headers="headers"
                  :items="desserts"
                  hide-default-footer
                  :items-per-page="-1"
                  class="elevation-0"
                >
                  <template #item="{item}">
                    <tr v-if="item.edit">
                      <td><v-text-field dense filled label="Étape prévue pour le versement" /></td>
                      <td>lul</td>
                    </tr>
                    <tr v-else>
                      <td>selected</td>
                      <td>selected</td>
                    </tr>
                  </template>
                </v-data-table>

                <v-btn outlined color="primary" @click="addNewVersement">
                  + Ajouter une étape de versement
                </v-btn>
                <InputsEditableText label="Commentaire:" compact />
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>

          <div>
            Commentaire
            <v-btn color="primary">
              Ajouter un versement
            </v-btn>
          </div>
          <div>
            <div>Ajouter un versmeent</div>
            <div class="d-flex">
              <div>
                <div>Versement terminé</div>
                <v-text-field dense filled />
              </div>
              <div class="ml-2">
                <div>Année</div>
                <v-text-field dense filled />
              </div>
              <div class="ml-2">
                <div>Catégorie</div>
                <v-text-field dense filled />
              </div>
              <div class="ml-2">
                <div>Montnat total</div>
                <v-text-field dense filled />
              </div>
              <div class="ml-2">
                <div>Montant </div>
                <v-text-field dense filled />
              </div>
              <div class="d-flex ml-2 mt-8">
                <v-btn
                  depressed
                  color="primary"
                  height="40"
                  class="mr-2"
                  @click="editMode = false"
                >
                  <v-icon>{{ icons.mdiCheck }}</v-icon>
                </v-btn>
                <v-btn
                  color="primary"
                  outlined
                  depressed
                  height="40"
                  @click="editMode = false"
                >
                  <v-icon>{{ icons.mdiClose }}</v-icon>
                </v-btn>
              </div>
            </div>
          </div>
        </v-container>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>
<script>
import { mdiCheck, mdiClose, mdiDotsVertical } from '@mdi/js'

export default
{
  name: 'DgdDialog',
  props: {},
  data () {
    return {
      versements: null,
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
      desserts: [
        {
          name: 'Frozen Yogurt',
          calories: 159,
          fat: 6.0,
          carbs: 24,
          protein: 4.0,
          iron: 1
        },
        {
          name: 'Ice cream sandwich',
          calories: 237,
          fat: 9.0,
          carbs: 37,
          protein: 4.3,
          iron: 1,
          edit: true
        },
        {
          name: 'Eclair',
          calories: 262,
          fat: 16.0,
          carbs: 23,
          protein: 6.0,
          iron: 7
        },
        {
          name: 'Cupcake',
          calories: 305,
          fat: 3.7,
          carbs: 67,
          protein: 4.3,
          iron: 8
        },
        {
          name: 'Gingerbread',
          calories: 356,
          fat: 16.0,
          carbs: 49,
          protein: 3.9,
          iron: 16
        }],
      dialog: true,
      voletQualitatifRaw: null,
      icons: {
        mdiCheck,
        mdiClose,
        mdiDotsVertical
      }
    }
  },
  computed: {

  },
  async mounted () {

  },
  methods: {
    addNewVersement () {
      this.desserts = [...this.desserts, {
        name: 'Ice cream sandwich',
        calories: 237,
        fat: 9.0,
        carbs: 37,
        protein: 4.3,
        iron: 1,
        edit: true
      }]
    }
  }
}
</script>

<style>
#dgd-dialog .v-expansion-panel-content > .v-expansion-panel-content__wrap{
  padding: 0px!important;
}
</style>
