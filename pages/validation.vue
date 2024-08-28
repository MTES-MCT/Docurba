<template>
  <v-container class="fill-height">
    <v-row justify="center" align="center">
      <v-col cols="12" class="mb-4">
        <div class="text-center text-h2">
          En attente de validation
        </div>
      </v-col>
      <v-col cols="12">
        <v-img height="200" contain src="/images/errors/maintenance.svg" />
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <p>La vérification manuelle de vos informations est nécessaire avant de valider votre accès à Docurba. </p>
        <p>Cette étape prend au maximum 48h et vous serez informé automatiquement par email dès que votre accès sera validé.</p>

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
  </v-container>
</template>
