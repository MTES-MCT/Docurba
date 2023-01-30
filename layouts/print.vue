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
  size: A4;

  /* @bottom-right {
    content: counter(page)
  } */
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

<style>
.print-container h1, .print-container h2,
.print-container h3, .print-container h4,
.print-container h5, .print-container h6,
.print-container ul {
  margin-bottom: 16px !important;
}

.print-container h1 {
  font-size: 40px;
}
.print-container h2 {
  font-size: 32px;
}
.print-container h3 {
  font-size: 28px;
}
.print-container h4 {
  font-size: 24px;
}
.print-container h5 {
  font-size: 22px;
}
.print-container h6 {
  font-size: 20px;
}
</style>
