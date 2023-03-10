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
        name: 'Prescription',
        to: { name: 'prescriptions' }
      }, {
        name: 'Socle de PAC',
        to: '/'
      }, {
        name: 'Données',
        to: '/'
      }, {
        name: 'Glossaire',
        to: '/'
      }]
    }
  }
}
</script>
