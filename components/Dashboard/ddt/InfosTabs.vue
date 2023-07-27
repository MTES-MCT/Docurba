<template>
  <v-row>
    <v-col cols="12" class="white pt-0 px-0 pb-0">
      <v-tabs
        background-color="transparent"
      >
        <v-tab :to="{name: 'ddt-departement-collectivites-collectiviteId-procedureId-infos', params: {departement: $route.params.departement ,collectiviteId: $route.params.collectiviteId, procedureId: $route.params.procedureId}}">
          Informations générales
        </v-tab>
        <v-tab :to="{name: 'ddt-departement-collectivites-collectiviteId-procedureId-volet_qualitatif', params: {departement: $route.params.departement ,collectiviteId: $route.params.collectiviteId, procedureId: $route.params.procedureId}}">
          Volet qualitatif
        </v-tab>
        <v-tab :to="{name: 'ddt-departement-collectivites-collectiviteId-procedureId-perimetre', params: {departement: $route.params.departement ,collectiviteId: $route.params.collectiviteId, procedureId: $route.params.procedureId}}">
          Communes concernées
        </v-tab>
      </v-tabs>
    </v-col>
  </v-row>
</template>

<script>
export default {
  name: 'InfosTabs'
}
</script>
