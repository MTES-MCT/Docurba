<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-expansion-panels multiple>
          <v-expansion-panel v-for="endpoint in endpoints" :key="endpoint.path">
            <v-expansion-panel-header>
              <h5 class="text-h5">
                {{ endpoint.apiPath }}
              </h5>
            </v-expansion-panel-header>
            <v-expansion-panel-content>
              <nuxt-content :document="endpoint" />
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  async asyncData ({ $content }) {
    const endpoints = (await $content('Dev/API', {
      deep: true
      // text: true
    }).fetch()).sort((a, b) => a.order - b.order)

    return {
      endpoints
    }
  }
}
</script>
