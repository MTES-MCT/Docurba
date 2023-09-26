<template>
  <v-row>
    <v-col cols="12">
      <h1 class="text-h1 ">
        Docurba vous aide dans vos démarches
      </h1>
    </v-col>
    <v-col cols="12" md="8">
      <p>
        Docurba, la plateforme mise en place par les services de l’Etat pour les collectivités et leurs bureaux d’étude afin de faciliter l'élaboration des documents d'urbanisme et la prise en compte des informations et enjeux environnementaux
      </p>
      <p>
        Avec Docurba, vous pouvez consulter en libre accès des données territorialisées, diverses ressources ainsi que le socle de PAC qui comprend :
      </p>
      <ul class="list">
        <li class="mb-2">
          <v-icon color="focus" class="mr-2">
            {{ icons.mdiCheck }}
          </v-icon><b>Le cadre juridique national ;</b>
        </li>
        <li>
          <v-icon color="focus" class="mr-2">
            {{ icons.mdiCheck }}
          </v-icon><b>Les éléments régionaux</b> (SRADDET & doctrine régionale).
        </li>
      </ul>
      <p class="mt-4">
        Vous pouvez également suivre les procédures avec :
      </p>
      <ul class="list">
        <li class="mb-2">
          <v-icon color="focus" class="mr-2">
            {{ icons.mdiCheck }}
          </v-icon>les <b>actes</b> correspondant aux étapes clés ;
        </li>
        <li>
          <v-icon color="focus" class="mr-2">
            {{ icons.mdiCheck }}
          </v-icon>
          le <b>tableau de bord</b> et la <b>feuille de route</b> avec l'état d'avancement.
        </li>
      </ul>
    </v-col>
    <v-col cols="12" md="4">
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
