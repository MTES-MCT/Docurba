<template>
  <v-container>
    <v-row>
      <v-col>
        <h1 class="text-h1">
          Questions Fréquentes
        </h1>
      </v-col>
    </v-row>
    <v-row>
      <v-col cosl="12">
        <v-expansion-panels flat focusable popout>
          <v-expansion-panel v-for="(q, i) in FAQ" :key="'question-' +i">
            <v-expansion-panel-header>
              <h6 class="text-h6">
                {{ q.question }}
              </h6>
            </v-expansion-panel-header>
            <v-expansion-panel-content>
              <nuxt-content :document="q" />
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
    const FAQ = await $content('FAQ', {
      deep: true
    }).fetch()

    return {
      FAQ: FAQ.filter(q => q.visible)
    }
  }
}
</script>
