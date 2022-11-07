<template>
  <v-row>
    <v-col cols="12">
      <h1 class="text-h1 text-no-wrap">
        Docurba vous aide dans vos démarches
      </h1>
    </v-col>
    <v-col cols="8">
      <p>
        Docurba, la plateforme mise en place par les services de l’Etat pour les collectivités et leurs bureaux d’étude afin de faciliter l'élaboration des documents d'urbanisme et la prise en compte des informations et enjeux environnementaux
      </p>
      <p>
        Avec Docurba, le socle de Porter-à-connaissance (PAC) est en libre accès avec les ressources suivantes disponibles pour chaque territoire :
      </p>
      <ul class="list">
        <li>
          <v-icon color="focus" class="mr-2">
            {{ icons.mdiCheck }}
          </v-icon><b>Le cadre juridique national</b>
        </li>
        <li>
          <v-icon color="focus" class="mr-2">
            {{ icons.mdiCheck }}
          </v-icon><b>Les éléments régionaux</b> (SRADDET & doctrine régionale)
        </li>
        <li>
          <v-icon color="focus" class="mr-2">
            {{ icons.mdiCheck }}
          </v-icon>Les <b>données territorialisées</b>
        </li>
      </ul>
    </v-col>
    <v-col cols="4">
      <LandingWhatPAC />
    </v-col>
  </v-row>
</template>
<script>
import { mdiCheck } from '@mdi/js'

export default {
  data () {
    return {
      icons: {
        mdiCheck
      }
    }
  }
}
</script>
<style scoped>
.list {
  list-style: none;
}
</style>
