<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1>Bienvenue DDT {{ $route.params.departement }}</h1>
      </v-col>
      <v-col cols="12">
        <v-btn depressed color="primary" :to="{name:'ddt-departement-collectivites', params:{departement: '47'}}">
          Aller à mon tableau de bord
        </v-btn>
        <v-btn depressed color="primary" class="ml-8">
          Consulter / Modifier ma trame de PAC
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  layout: 'ddt'
}
</script>
