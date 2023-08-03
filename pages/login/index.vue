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
        <v-card flat class="border-light">
          <v-card-title>Une collectivité ou assimilé</v-card-title>
          <v-card-text>
            Je suis un élu, un employé de mairie ou un bureau d'étude. Acceder simplement à toute vos démarche d'ubanisme via Docurba.
            Après une étape de validation de votre statut vous pourrez accéder a votre tableau de bord personalisé.
          </v-card-text>
          <v-card-actions>
            <v-btn color="primary" depressed tile :to="{name:'login-collectivites-signup'}">
              Créer un compte
            </v-btn>
            <v-btn outlined tile color="primary" :to="{name:'login-collectivites-signin'}">
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
        <v-card flat class="border-light">
          <v-card-title>Un agent de l'Etat</v-card-title>
          <v-card-text>Je suis un agent d'une DDT/DEAL ou d'une DREAL en charge du suivi des procédures d'élaboration et d'évolution des documents d'urbanisme et/ou de la production des documents de l'Etat (PAC, ..) liées à ces procédures. Après une étape de validation de votre compte Etat, vous pourrez paramétrer votre trame de PAC départementale ou régionale et suivre vos procédures.</v-card-text>
          <v-card-actions>
            <v-btn color="primary" tile depressed :to="{name:'login-ddt-signup'}">
              Creer un compte
            </v-btn>
            <v-btn outlined tile color="primary" :to="{name:'login-ddt-signin'}">
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
