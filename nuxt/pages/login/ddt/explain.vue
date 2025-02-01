<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <div class="text-h1">
          Inscription réussie ! 🎉 Activation en cours
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
        <p>La vérification manuelle de vos informations est nécessaire avant de valider votre accès à Docurba et vous permettre d’agir en tant qu’agent de l’État. </p>
        <p>Cette étape prend au maximum 48h et vous serez informé automatiquement par email dès que votre accès sera validé. Vous pourrez alors accéder à votre tableau de bord et à votre trame de PAC départementale, en cliquant sur le bouton "tableau de bord" depuis la page d'accueil ou directement depuis l'email vous informant de la validation de votre accès.</p>

        <!-- <p>
          Veuillez noter qu'une étape de vérification manuelle est nécessaire, afin de nous assurer que vous êtes bien en droit d’agir en tant qu’agent de l’État..
          Vous recevrez alors un email automatique pour vous confirmer votre accès à Docurba. (supprimer la fin de la phrase car déjà expliqué plus haut).
        </p> -->
        <v-alert type="info">
          En cas de problème technique ou de question, n'hésitez pas à contacter l'équipe de Docurba par email: contact@docurba.beta.gouv.fr
        </v-alert>
        <!-- <p>
          Vous pourrez alors accéder à votre tableau de bord et à votre trame de PAC départementale, en cliquant sur le bouton "tableau de bord" depuis la page d'accueil ou directement depuis l'email vous informant de la validation de votre accès.
        </p> -->
      </v-col>
    </v-row>

    <v-row class="mb-12">
      <v-col cols="12" class="d-flex justify-center">
        <v-btn depressed color="primary" tile x-large :to="{name: 'index'}">
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
