<template>
  <v-container class="my-8">
    <v-row justify="center">
      <v-col cols="12" class="iframe-container">
        <iframe
          src="https://docurba-metabase.osc-fr1.scalingo.io/public/dashboard/64ca74aa-b566-44a5-b381-bda8f8602f05"
          frameborder="0"
          allowtransparency
          class="iframe"
          height="700px"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
.iframe-container {
  position: relative;
  /* overflow: hidden; */
  height: 700px;
}

.iframe {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  right: 0;
  width: 100%;
  height: 100%;
}

.card-loader {
  min-height: 200px;
}

.big-number {
  font-size: 64px;
}
</style>

<style>
.stats-card {
  border: 1px solid #E3E3FD;
  border-color: #E3E3FD !important;
}
</style>
