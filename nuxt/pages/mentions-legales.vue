<template>
  <div class="g100">
    <v-container id="guide">
      <v-row>
        <v-col cols="12">
          <nuxt-content :document="legal[0]" />
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
export default {
  async asyncData ({ $content }) {
    const legal = await $content('Legal', {
      deep: true
    }).fetch()

    return {
      legal
    }
  }
}
</script>
