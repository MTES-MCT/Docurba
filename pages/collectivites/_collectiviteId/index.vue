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
            :to="actionsCard.disabled ? null: actionsCard.to"
          >
            <v-card-title class="text-body-1 font-weight-bold break-word d-flex align-end justify-space-between" style="line-height:24px">
              <div>
                {{ actionsCard.title }}
              </div>

              <v-chip v-if="actionsCard.tag" class="mt-2 font-weight-regular primary--text text--lighten-2" x-small color="primary lighten-3 ">
                {{ actionsCard.tag }}
              </v-chip>
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
      <v-col cols="12">
        <DashboardDUItem
          v-for="(procedure,i) in procedures"
          :key="'du_' + i"
          :procedure="procedure"
          censored
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import SudocuEvents from '@/mixins/SudocuEvents.js'

export default {
  mixins: [SudocuEvents],
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
    const collectiviteId = this.isEpci ? this.collectivite.EPCI : this.collectivite.code_commune_INSEE

    return {
      actionsCards: [
        {
          title: 'Déposer un acte',
          text: 'Déposez une délibération de prescription ou un arrêté.',
          to: { name: 'collectivites-collectiviteId-prescriptions', params: { collectiviteId }, query: this.$route.query }
        },
        {
          title: 'Socle de Porter à connaissance',
          text: 'Consultez ou modifiez votre socle de Porter à Connaissance.',
          to: {
            name: 'collectivites-collectiviteId-pac',
            params: { collectiviteId },
            query: Object.assign({ document: this.isEpci ? 'PLUi' : 'PLU' }, this.$route.query)
          }
        },
        {
          title: 'Ressources',
          text: 'Consultez des guides ou sites internet utiles.',
          to: { name: 'collectivites-collectiviteId-ressources', params: { collectiviteId }, query: this.$route.query }
        },
        {
          title: 'Données',
          text: 'Consultez les données de votre territoire.',
          to: { name: 'collectivites-collectiviteId-donnees-georisques', params: { collectiviteId }, query: this.$route.query }
        }
      ]
    }
  },
  mounted () {
    console.log('OK TEST: ', this.collectivite)
  }
}
</script>
