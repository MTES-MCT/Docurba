<template>
  <v-container fluid>
    <PACTreeviewContent :pac-data="PAC" />
  </v-container>
</template>

<script>

export default {
  async asyncData ({ $content }) {
    const PAC = await $content('PAC', {
      deep: true
    }).fetch()

    console.log(PAC.length)

    return {
      PAC
    }
  }
}
</script>
