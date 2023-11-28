<template>
  <v-card outlined>
    <v-card-text>
      <v-row>
        <v-col cols="" class="text-subtitle-1 font-weight-bold">
          <span>{{ project.doc_type }}</span>
          <br>
          <span>{{ project.name }}</span>
        </v-col>
        <v-spacer />
        <v-col cols="auto" class="text-subtitle-1 font-weight-bold">
          <span>{{ collectivity.intitule }} ({{ collectivity.code }})</span>
        </v-col>
      </v-row>
    </v-card-text>
    <v-card-actions>
      <v-btn color="primary" tile depressed nuxt :to="`/trames/projet-${project.id}`">
        Modifier le PAC
      </v-btn>
      <v-btn
        color="primary"
        tile
        depressed
        :loading="loadingPdf"
        :disabled="loadingPdf"
        @click="downloadPdf"
      >
        PDF
      </v-btn>
    </v-card-actions>
  </v-card>
</template>
<script>

export default {
  props: {
    project: {
      type: Object,
      required: true
    },
    collectivity: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      loadingPdf: false,
      pdfUrl: null
    }
  },
  methods: {
    async downloadPdf () {
      this.loadingPdf = true
      await this.$pdf.pdfFromRef(`projet-${this.project.id}`, this.project)
      this.loadingPdf = false
    }
  }
}
</script>
