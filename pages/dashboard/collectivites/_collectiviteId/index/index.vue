<template>
  <v-container>
    <v-row>
      <v-col>
        <h2>Actions rapides</h2>
      </v-col>
    </v-row>
    <v-row>
      <v-col
        v-for="(actionsCard, i) in actionsCards"
        :key="i"
        cols="12"
        sm="6"
        md="3"
        class="d-flex justify-center"
      >
        <div style="position: relative; display:inline-block;">
          <v-card
            outlined
            tile
            color="white"
            class="py-2 fill-height"
            :to="actionsCard.to"
          >
            <v-card-title class="text-body-1 font-weight-bold break-word" style="line-height:24px">
              {{ actionsCard.title }}
            </v-card-title>
            <v-card-text>
              {{ actionsCard.text }}
            </v-card-text>
          </v-card>
          <div class="primary bottom-border" />
        </div>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <h2>Documents d'urbanisme</h2>
      </v-col>
      <v-col cols="12">
        <p>
          Documents d’urbanismes disponibles pour la commune recherchée :
        </p>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  props: {
    isEpci: {
      type: Boolean,
      required: true
    },
    collectivite: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      actionsCards: [
        {
          title: 'Prescription',
          text: 'Déposez ou consultez votre prescription',
          to: { name: 'dashboard-collectivites-collectiviteId-index-prescriptions', params: { collectiviteId: this.collectivite.code_commune_INSEE } }
        },
        {
          title: 'Socle de PAC',
          text: 'Consultez ou modifiez votre socle de Porter à Connaissance',
          // http://localhost:3000/pacsec/content?insee=2001&region=FR-HDF&document=PLU
          to: { name: 'pacsec-content', query: { insee: '2001', region: 'FR-HDF', document: 'PLU' } }
        },
        {
          title: 'Ressources',
          text: 'Lorem ipsum dolor sit amet consectetur. Ut nullam vitae.',
          to: { name: 'dashboard-collectivites-collectiviteId-index-ressources', params: { collectiviteId: this.collectivite.code_commune_INSEE } }
        },
        {
          title: 'Données',
          text: 'Lorem ipsum dolor sit amet consectetur. Ut nullam vitae.',
          to: { name: 'dashboard-collectivites-collectiviteId-index-donnees', params: { collectiviteId: this.collectivite.code_commune_INSEE } }
        }
      ]
    }
  }
}
</script>
