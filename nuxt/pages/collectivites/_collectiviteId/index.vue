<template>
  <v-container>
    <v-row>
      <v-col>
        <h2>Actions rapides</h2>
      </v-col>
    </v-row>
    <v-row>
      <v-col
        v-for="(actionsCard, i) in availableCards"
        :key="i"
        cols="12"
        sm="6"
        :md="12/availableCards.length"
        class="d-flex justify-center"
      >
        <div class="action-card-container">
          <v-card
            outlined
            tile
            color="white"
            class="py-2 fill-height"
            :to="actionsCard.to"
            nuxt
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
      <v-col class="d-flex justify-space-between">
        <h2>Documents d'urbanisme</h2>
        <SignalementProbleme />
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        Documents d’urbanismes disponibles pour la commune recherchée :
      </v-col>
    </v-row>
    <DashboardDUItemsList
      :collectivite="collectivite"
      :procedures="procedures"
      :schemas="schemas"
      is-public
    />
  </v-container>
</template>

<script>
export default {
  name: 'CollectiviteDetails',
  props: {
    isEpci: {
      type: Boolean,
      required: true
    },
    collectivite: {
      type: Object,
      required: true
    },
    procedures: {
      type: Array,
      default () { return [] }
    },
    schemas: {
      type: Array,
      default () { return [] }
    }
  },
  data () {
    return {
      actionsCards: [
        {
          title: 'Socle de Porter à connaissance',
          text: 'Consultez votre socle de Porter à Connaissance.',
          to: {
            name: 'collectivites-collectiviteId-pac',
            params: { collectiviteId: this.collectivite.code },
            query: Object.assign({ document: this.isEpci ? 'PLUi' : 'PLU' }, this.$route.query)
          }
        },
        {
          title: 'Ressources',
          text: 'Consultez des ressources autour de vos documents d’urbanisme.',
          to: { name: 'collectivites-collectiviteId-ressources', params: { collectiviteId: this.collectivite.code }, query: this.$route.query }
        },
        {
          title: 'Données',
          text: 'Consultez les données de votre territoire.',
          to: { name: 'collectivites-collectiviteId-donnees-georisques', params: { collectiviteId: this.collectivite.code }, query: this.$route.query }
        }
      ]
    }
  },
  computed: {
    isAdmin () {
      if (this.$user.profile?.is_admin) { return true }

      if (this.$user.profile?.side === 'etat') {
        return this.$user.profile?.departement === this.collectivite.departementCode
      } else {
        return this.$user.profile?.collectivite_id === this.collectivite.code ||
          this.$user.profile?.collectivite_id === this.collectivite.intercommunaliteCode // Ca ne marche pas sur les CC puisque les CC n'ont pas de CC
      }
    },
    newProcedureCard () {
      const cardData = {
        title: 'Nouvelle Procédure',
        text: 'Démarrez une nouvelle procédure de document d’urbanisme.'
      }

      if (this.isAdmin && this.$user.profile.verified) {
        cardData.to = `/collectivites/${this.collectivite.code}/procedures/add`
      } else if (this.isAdmin && !this.$user.profile.verified) {
        cardData.to = '/validation'
      } else {
        cardData.to = '/login'
      }

      return cardData
    },
    availableCards () {
      return [this.newProcedureCard, ...this.actionsCards]
    }
  }

}
</script>

<style scoped>
.action-card-container {
  position: relative;
  display:inline-block;
  width: 100%;
}

.divider-vertical {
  width: 4px;
  height: 100%;
  background: #6A6AF4;
}
</style>
