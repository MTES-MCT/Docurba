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

    // .where({
    //   path: {
    //     $not: {
    //       $regex: /Politiques-publiques-specifiques-s'appliquant-sur-le-territoire/
    //     }
    //   }
    // }).fetch()

    // console.log(PAC.length)

    return {
      // PAC: PAC.filter(s => !s.path.includes('olitiques-publiques-specifiques'))
      PAC: PAC.filter(s => !s.path.includes('PP-du-territoire'))
    }
  }
}
</script>
