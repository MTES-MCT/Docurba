<template>
  <v-app class="print-container">
    <v-main>
      <nuxt />
    </v-main>
  </v-app>
</template>

<script>
import '@gouvfr/dsfr/dist/css/header.css'
import '@gouvfr/dsfr/dist/css/logo.css'
export default {

}
</script>

<style>
  /* We need both scoped and unscoped style for vuetify internal class */
  .print-container .fr-header .v-toolbar__content {
    margin-top: 1px;
    padding: 0mm !important;
  }

  .print-container img {
    max-width: 100%;
    display: block;
  }
</style>

<style scoped>
@page {
  margin: 17mm 17mm 17mm 17mm;
  -webkit-print-color-adjust: exact !important;   /* Chrome, Safari, Edge */
  color-adjust: exact !important;                 /*Firefox*/
}

/* .fr-header {
  padding: 17mm;
} */

.print-container {
  /* padding: 17mm; */
  -webkit-print-color-adjust: exact !important;   /* Chrome, Safari, Edge */
  color-adjust: exact !important;
}
</style>
