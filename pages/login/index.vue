<template>
  <v-container class="fill-height">
    <v-row class="align-self-start">
      <v-col cols="12">
        <div class="mt-2">
          <nuxt-link :to="{name: 'index'}">
            <v-icon small color="primary" class="my-2">
              {{ icons.mdiArrowLeft }}
            </v-icon>
            Retour
          </nuxt-link>
        </div>

        <div class="text-h1">
          Inscription et connexion
        </div>
      </v-col>
    </v-row>
    <v-row class="d-flex align-self-start">
      <v-col cols="12">
        <div class="text-h2 mb-2">
          Vous êtes...
        </div>
      </v-col>
      <v-col cols="5.5">
        <v-card elevation="2">
          <v-card-title>Une collectivité ou assimilé</v-card-title>
          <v-card-text>
            Je suis un élu, un employé de mairie ou un bureau d'étude. Acceder simplement à toute vos démarche d'ubanisme via Docurba.
            Après une étape de validation de votre statut vous pourrez accéder a votre tableau de bord personalisé.
          </v-card-text>
          <v-card-actions>
            <v-btn color="primary" depressed :to="{name:'login-collectivites-signup'}">
              Créer un compte
            </v-btn>
            <v-btn text color="primary" :to="{name:'login-collectivites-signin'}">
              Me connecter
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
      <v-col cols="1" class="d-flex align-center justify-center">
        <div class="text-h2">
          Ou
        </div>
      </v-col>
      <v-col cols="5.5">
        <v-card
          elevation="2"
        >
          <v-card-title>Un agent de l'Etat</v-card-title>
          <v-card-text>Lorem, ipsum dolor sit amet consectetur adipisicing elit. Suscipit dicta perferendis fugiat harum quos aliquam id voluptatibus, vel aperiam tempore porro expedita qui. Inventore doloremque aliquam iste quia? Maiores, exercitationem?</v-card-text>
          <v-card-actions>
            <v-btn color="primary" depressed :to="{name:'login-ddt-signup'}">
              Creer un compte
            </v-btn>
            <v-btn text color="primary" :to="{name:'login-ddt-signin'}">
              Me connecter
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mdiArrowLeft } from '@mdi/js'

export default {
  name: 'Login',
  data () {
    return {
      icons: {
        mdiArrowLeft
      }
    }
  }
}
</script>
