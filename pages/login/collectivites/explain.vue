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
          Pour simplifier la gestion de vos accès, nous avons opté pour la connexion sécurisé dite "Lien magique".
          Vous avez reçu un mail qui vous permettra de vous connecter directement, sans mot de passe.
        </p>
        <p>
          Chaque lien est à usage unique et à une durée de vie avant expiration de 1 heure.
          Rendez vous dès maintenant dans votre boite email et cliquer sur le lien "Me connecter sur Docurba".
          <br>
          Vous n'avez rien d'autre a faire !
        </p>
        <v-alert type="warning">
          La seule contrepartie est d'utiliser le même poste de travail et navigateur Web que ceux du moment ou vous avez demander votre "lien magique" de connexion.
          Vous pouvez néanmoins vous connecter avec d'autres appareils et/ou
          Vous devez utiliser le même navigateur pour rester connecter.
        </v-alert>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <div class="text-h2">
          Temps d'activation
        </div>
      </v-col>
      <v-col cols="12">
        <p>
          Veuillez noter qu'une étape de validation manuelle pour nous assurer que vous êtes bien en droit d'agir en tant que collectivité.
          Vous recevrez un email pour vous informer de votre validation de compte dès que notre équipe aura procéder à la vérification (sous moins de 48h généralement).
        </p>
        <v-alert type="info">
          En cas de problème technique ou de question, n'hésitez pas à contacter l'équipe de Docurba par email: contact@docurba.com
        </v-alert>
        <p>
          Vous pourrez alors accéder à votre tableau de bord pour votre collectivité, en cliquant sur le bouton "tableau de bord" depuis la page d'accueil ou directement depuis l'email vous informant de votre acceptation d'accès.
          En attendant, vous pouvez tout de même soumettre vos actes depuis la partie public, mais ceux ci seront traités uniquement après validation de votre profil.
        </p>
      </v-col>
    </v-row>
    <v-row class="mb-12">
      <v-col cols="12" class="d-flex justify-center">
        <v-btn depressed color="primary" tile x-large>
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
