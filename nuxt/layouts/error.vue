<template>
  <v-app class="align-center justify-center">
    <v-container style="border: 1px solid #E3E3FD;" class="rounded mt-16 text-center">
      <v-row>
        <v-col cols="12" class="mt-12">
          <v-img src="images/errors/404.png" height="120" contain />
        </v-col>
        <v-col cols="12" class="mt-6">
          <h1 v-if="error.statusCode === 404" class="text-h2">
            {{ pageNotFound }}
          </h1>
          <h1 v-else>
            {{ otherError }}
          </h1>
        </v-col>
        <v-col cols="12">
          <div>
            La page que vous cherchez n’existe pas ou a été déplacée.
          </div>
        </v-col>
        <v-col cols="12" class="mb-8">
          <v-btn to="/" nuxt outlined tile color="primary">
            Aller à la page d'accueil
          </v-btn>
        </v-col>
      </v-row>
    </v-container>
  </v-app>
</template>

<script>
export default {
  layout: 'empty',
  props: {
    error: {
      type: Object,
      default: null
    }
  },
  data () {
    return {
      pageNotFound: 'Page non trouvée',
      otherError: 'An error occurred'
    }
  },
  head () {
    const title =
      this.error.statusCode === 404 ? this.pageNotFound : this.otherError
    return {
      title
    }
  }
}
</script>

<style scoped>

</style>
