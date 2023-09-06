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
          Vous représentez...
        </div>
      </v-col>
      <v-col cols="5.5">
        <v-card flat class="border-light fill-height d-flex flex-column">
          <v-card-title>Les territoires</v-card-title>
          <v-card-text>
            <p>
              Vous êtes un élu, un technicien ou employé d'une collectivité, bureau d'étude ou agence d'urbanisme. Accédez simplement aux informations relatives à l'élaboration ou l'évolution de vos documents d'urbanisme
            </p>
            <div>
              Après vérification de votre accès, vous pourrez naviguer dans votre espace personnalisé.
            </div>
          </v-card-text>
          <v-card-actions class="mt-auto">
            <v-spacer />
            <v-btn color="primary" depressed tile :to="{name:'login-collectivites-signup'}" class="no-text-transform">
              Créer un compte territoires
            </v-btn>
            <v-btn outlined tile color="primary" :to="{name:'login-collectivites-signin'}" class="no-text-transform">
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
          <v-card-title>Les services de l’État</v-card-title>
          <v-card-text>
            <p>
              Vous êtes un agent d'une DDT(M)/DEAL ou d'une DREAL en charge du suivi des procédures d’élaboration et d’évolution des documents d’urbanisme et/ou de la production des documents de l’État liés à ces procédures (PAC, etc.).
            </p>
            <div>
              Après vérification de votre accès, vous pourrez paramétrer votre trame de PAC départementale ou régionale, et suivre vos procédures.
            </div>
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn color="primary" tile depressed :to="{name:'login-ddt-signup'}" class="no-text-transform">
              Créer un compte agent de l’État
            </v-btn>
            <v-btn outlined tile color="primary" :to="{name:'login-ddt-signin'}" class="no-text-transform">
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
