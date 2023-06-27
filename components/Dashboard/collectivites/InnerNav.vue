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
        to: { path: `/collectivites/${this.$route.params.collectiviteId}/`, query: this.$route.query }
      }, {
        name: 'Prescription',
        to: { path: `/collectivites/${this.$route.params.collectiviteId}/prescriptions`, query: this.$route.query }
      }, {
        name: 'Socle de PAC',
        to: {
          path: `/collectivites/${this.$route.params.collectiviteId}/pac`,
          query: Object.assign({ document: this.isEpci ? 'PLUi' : 'PLU' }, this.$route.query)
        }
      }, {
        name: 'Données',
        to: { path: `/collectivites/${this.$route.params.collectiviteId}/donnees/georisques`, query: this.$route.query }
      }, {
        name: 'Glossaire',
        to: { path: `/collectivites/${this.$route.params.collectiviteId}/glossaire`, query: this.$route.query }
      }]
    }
  }
}
</script>
