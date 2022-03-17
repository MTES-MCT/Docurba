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

    // remove unwanted intros
    PAC.splice(PAC.findIndex(s => s.path === '/PAC/Introduction/introcution-PAC-valide'), 1)

    return {
      // PAC: PAC.filter(s => !s.path.includes('olitiques-publiques-specifiques'))
      PAC: PAC.filter(s => !s.path.includes('PP-du-territoire'))
    }
  }
}
</script>
