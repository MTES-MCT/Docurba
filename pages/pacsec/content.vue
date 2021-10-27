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
    }).where({
      path: {
        $not: {
          $regex: /Politiques-publiques-specifiques-s'appliquant-sur-le-territoire/
        }
      }
    }).fetch()

    // console.log(PAC.length)

    return {
      PAC
    }
  }
}
</script>
