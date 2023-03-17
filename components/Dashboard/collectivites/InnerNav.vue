<template>
  <div class="d-flex justify-end align-center">
    <nuxt-link v-for="(link, i) in links" :key="'inner_' + i" class="ml-4" :to="link.to">
      -> {{ link.name }}
    </nuxt-link>
  </div>
</template>
<script>
export default {
  name: 'InnerNav',
  data () {
    return {
      links: [{
        name: 'Tableau de bord',
        to: { name: 'dashboard-collectivites-collectiviteId-index' }
      }, {
        name: 'Prescription',
        to: { name: 'dashboard-collectivites-collectiviteId-index-prescriptions' }
      }, {
        name: 'Socle de PAC',
        to: '/'
      }, {
        name: 'Données',
        to: { name: 'dashboard-collectivites-collectiviteId-index-donnees' }
      }, {
        name: 'Glossaire',
        to: '/'
      }]
    }
  }
}
</script>
