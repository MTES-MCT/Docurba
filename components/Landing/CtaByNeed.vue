<template>
  <v-container>
    <v-row class="mt-10" justify="center">
      <v-col cols="12" lg="6">
        <div class="fill-height d-flex flex-column">
          <h2 class="text-h3 mb-5">
            Vous voulez immédiatement avoir accès aux données et aux éléments régionaux concernant votre territoire ?
          </h2>
          <v-img contain :src="require('@/assets/images/landing/data_screen.png')" max-height="200px" class="my-5" />
          <p>
            Vous pouvez consulter les modèles et guides sur l’élaboration d’un document d’urbanisme, et surtout accéder au cadre juridique national, aux éléments régionaux (SRADDET & doctrine régionale) et aux données territorialisées.
          </p>
          <v-btn to="/pacsec/data" nuxt outlined class="mt-auto" color="primary">
            Accéder aux ressources disponibles et données territorialisées
          </v-btn>
        </div>
      </v-col>
      <v-col cols="12" lg="6">
        <div class="fill-height d-flex flex-column">
          <h2 class="text-h3 mb-5">
            Vous avez prescrit un document d’urbanisme et souhaitez être accompagné dans l’élaboration du projet ?
          </h2>
          <v-img contain :src="require('@/assets/images/landing/doc_screen.png')" max-height="200px" class="my-5" />
          <p>
            Vous pouvez accéder à votre porter à connaissance (PAC) en ligne, à votre note d'enjeux le cas échéant, et à l'espace partagé avec une feuille de route et des documents liés aux étapes de votre projet.
          </p>
          <v-btn outlined class="mt-auto" color="primary" @click="openDialog">
            Créer mon compte pour obtenir le PAC de mon territoire
          </v-btn>
          <client-only>
            <LoginDialog v-model="openLogin" />
            <DocumentsDialog v-if="$user.id" v-model="openDocs" />
          </client-only>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  data () {
    return {
      openLogin: false,
      openDocs: false
    }
  },
  methods: {
    openDialog () {
      if (this.$user && this.$user.id) {
        this.openDocs = true
      } else {
        this.openLogin = true
      }
    }
  }
}
</script>
