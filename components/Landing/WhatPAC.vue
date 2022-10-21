<template>
  <v-card flat color="bf100-g750">
    <v-card-title>
      <v-row no-gutters>
        <v-col cols="12">
          <v-icon color="focus">
            {{ icons.mdiInformationOutline }}
          </v-icon>
        </v-col>
        <v-col>
          Qu'est ce qu'un PAC ?
        </v-col>
      </v-row>
    </v-card-title>
    <v-card-text class="black--text">
      Le PAC contient les informations nécessaires à l’exercice des compétences des collectivités en matière d’urbanisme. Il contient notamment le cadre législatif et réglementaire à respecter ou encore les protections existantes en matière d’environnement et de patrimoine sur le territoire.
    </v-card-text>
  </v-card>
</template>

<script>
import { mdiInformationOutline } from '@mdi/js'
export default {
  data () {
    return {
      icons: {
        mdiInformationOutline
      }
    }
  }
}
</script>
