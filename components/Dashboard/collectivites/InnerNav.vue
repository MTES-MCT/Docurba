<template>
  <div class="d-flex justify-end align-center">
    <nuxt-link v-for="(link, i) in links" :key="'inner_' + i" class="ml-4 d-flex align-center" :to="link.to">
      <v-icon small color="primary" class="mr-2">
        {{ icons.mdiArrowRight }}
      </v-icon>
      {{ link.name }}
    </nuxt-link>
  </div>
</template>
<script>
import { mdiArrowRight } from '@mdi/js'
export default {

  name: 'InnerNav',
  props: {
    isEpci: {
      type: Boolean,
      required: true
    },
    collectivite: {
      type: Object,
      required: true
    },
    communes: {
      type: Array,
      required: true
    },
    region: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      icons: {
        mdiArrowRight
      },
      links: [{
        name: 'Tableau de bord',
        to: { path: `/collectivites/${this.$route.params.collectiviteId}` }
      }, {
        name: 'Prescription',
        to: { path: `/collectivites/${this.$route.params.collectiviteId}/prescriptions` }
      }, {
        name: 'Socle de PAC',
        to: { path: '/pacsec/content', query: { region: this.region.iso, document: 'PLU' } }
      }, {
        name: 'Données',
        to: { path: `/collectivites/${this.$route.params.collectiviteId}/donnees/georisques` }
      }, {
        name: 'Glossaire',
        to: { path: `/collectivites/${this.$route.params.collectiviteId}/glossaire` }
      }]
    }
  }
}
</script>
