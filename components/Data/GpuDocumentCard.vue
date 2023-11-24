<template>
  <v-card flat outlined height="100%" max-height="400" class="d-flex flex-column">
    <v-card-title>{{ title }}</v-card-title>
    <v-card-text>
      <div>
        <v-chip
          outlined
          class="text-capitalize"
          color="bf500"
        >
          {{ document.grid.title }}
        </v-chip>
        <v-chip
          outlined
          class="text-capitalize"
          color="bf300"
        >
          {{ label }}
        </v-chip>
      </div>
      <div class="mt-4">
        <div>
          <div>Nom</div>
          <div><strong>{{ document.name }}</strong></div>
        </div>
        <div class="mt-2">
          <div>Dernière mise à jour</div>
          <div><strong>{{ new Date(document.updateDate).toLocaleDateString() }}</strong></div>
        </div>
      </div>
    </v-card-text>
    <v-spacer />
    <v-card-actions>
      <v-btn
        :href="mapUrl"
        target="_blank"
        tile
        depressed
        color="
        primary"
      >
        Voir la carte
      </v-btn>
      <v-btn
        :href="filesUrl"
        target="_blank"
        tile
        text
        color="primary"
      >
        Pièces écrites
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
export default {
  props: {
    document: {
      type: Object,
      required: true
    }
  },
  computed: {
    title () {
      switch (this.document.type) {
        case 'SUP':
          return this.document.supCategory.libelleCourt
        case 'PLU':
          return "Plan Local d'Urbanisme"
        case 'CC':
          return 'Carte Communale'
        case 'SCoT':
          return 'Schéma de Cohérence Territorial'
        case 'PSMV':
          return 'Plan de Sauvegarde et de Mise en Valeur'
      }

      return this.document.type
    },
    label () {
      if (this.document.type === 'PLU' || this.document.type === 'CC') {
        return "Document d'urbanisme"
      }

      return this.document.type
    },
    mapUrl () {
      return `https://www.geoportail-urbanisme.gouv.fr/map/?document=${this.document.id}#tile=1&lat=${this.document.center.lat}&lon=${this.document.center.lon}&zoom=13`
    },
    filesUrl () {
      return `https://www.geoportail-urbanisme.gouv.fr/document/by-id/${this.document.id}?tab=2`
    }
  }
}
</script>
