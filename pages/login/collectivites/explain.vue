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
          Comment me connecter ?
        </div>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <p>
          Vous allez recevoir sous peu un email qui vous permettra de vous connecter.
        </p>
        <p>
          Pour simplifier la gestion de vos accès, nous avons opté pour la connexion sécurisée dite "Lien magique".
          Vous avez reçu un mail qui vous permettra de vous connecter directement, sans mot de passe.
        </p>
        <p>
          <b>Chaque lien est à usage unique et à une durée de vie avant expiration de 1 heure seulement.
            Rendez-vous dès maintenant dans votre boîte email et cliquez sur le lien "Me connecter sur Docurba".</b>
          <br>
          Vous n'avez rien d'autre à faire !
        </p>
        <v-alert type="warning">
          La seule contrepartie est d'utiliser le même poste de travail et navigateur Web que ceux du moment où vous avez demandé votre "lien magique" de connexion.
        </v-alert>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <div class="text-h2">
          Activation de votre compte
        </div>
      </v-col>
      <v-col cols="12">
        <p>
          Veuillez noter qu'une étape de validation manuelle de notre part est nécessaire, afin de nous assurer que vous avez bien la qualité pour agir.
          Vous recevrez un email pour vous informer de votre validation de compte dès que notre équipe aura procédé à la vérification.
        </p>
        <v-alert type="info">
          En cas de problème technique ou de question, n'hésitez pas à contacter l'équipe de Docurba par email: contact@docurba.beta.gouv.fr
        </v-alert>
        <p>
          Vous pourrez alors accéder à votre tableau de bord pour votre collectivité, en cliquant sur le bouton "tableau de bord" depuis la page d'accueil ou directement depuis l'email vous informant de la validation de votre accès.
          En attendant, vous pouvez tout de même soumettre vos actes depuis la partie publique, mais ceux-ci seront traités uniquement après validation de votre profil.
        </p>
      </v-col>
    </v-row>
    <v-row class="mb-12">
      <v-col cols="12" class="d-flex justify-center">
        <v-btn depressed color="primary" tile x-large :to="`/collectivites/${$route.query.collectivite_id}`">
          Voir ma collectivité en mode public
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
