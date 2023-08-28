<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <div class="text-h1">
          Inscription réussie ! 🎉
        </div>
      </v-col>
      <v-col cols="12">
        <div class="text-h2">
          Temps d'activation
        </div>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <p> Nous devons valider votre status d'agent de l'Etat.</p>
        <p>Après une étape de validation (au maximum 48h), vous pourrez accéder à votre tableau de bord pour votre departement.</p>

        <p>
          Veuillez noter qu'une étape de validation manuelle pour nous assurer que vous êtes bien en droit d'agir en tant qu'agent de l'Etat est nécessaire.
          Vous recevrez un email pour vous informer de la validation de votre compte dès que notre équipe aura procédé à la vérification (sous moins de 48h généralement).
        </p>
        <v-alert type="info">
          En cas de problème technique ou de question, n'hésitez pas à contacter l'équipe de Docurba par email: contact@docurba.beta.gouv.fr
        </v-alert>
        <p>
          Vous pourrez alors accéder à votre tableau de bord, en cliquant sur le bouton "tableau de bord" depuis la page d'accueil ou directement depuis l'email vous informant de la validation de votre accès.
        </p>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">
        <v-btn :to="{name: 'index'}">
          Retourner au site
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'ExplainCollectivite'
}
</script>
