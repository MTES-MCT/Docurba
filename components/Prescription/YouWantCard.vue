<template>
  <v-row>
    <v-col cols="12">
      <v-container class=" primary lighten-1 pa-8 mb-6">
        <v-row>
          <v-col cols="12">
            <div class="text-h5 font-weight-bold primary--text pb-8 d-flex  align-center">
              <v-icon color="primary" large class="mr-2">
                {{ icons.mdiAccountSearchOutline }}
              </v-icon>

              <div>Vous voulez...</div>
            </div>
            <div>
              <div class="mb-4">
                <v-icon color="primary" class="mr-1">
                  {{ icons.mdiCheck }}
                </v-icon>
                Déposer un acte
              </div>
              <!-- <div>
                  <v-icon color="primary" class="mr-1">
                    {{ icons.mdiCheck }}
                  </v-icon>
                  Pour {{ $route.query.epci_code ? $route.query.epci_label : town.nom_commune_complet }}
                </div> -->
            </div>
          </v-col>
        </v-row>
      </v-container>
    </v-col>
  </v-row>
</template>

<script>
import { mdiCheck, mdiAccountSearchOutline } from '@mdi/js'

export default {
  data () {
    return {
      icons: {
        mdiCheck,
        mdiAccountSearchOutline
      }
    }
  }
}
</script>
