<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <div class="text-h1">
          Vous allez recevoir un email qui vous permettra de vous connecter automatiquement.
        </div>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <p>Vous devez utiliser le même navigateur pour rester connecter blabla.</p>
        <p>Après une étape de validation (au maximum 48h), vous pourrez accéder à votre tableau de bord pour votre collectivité.</p>
        <p>En attendant, vous pouvez tout de même soumettre vos actes</p>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">
        <v-btn>Voir ma collectivité</v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'ExplainCollectivite'
}
</script>
