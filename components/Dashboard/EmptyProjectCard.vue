<template>
  <v-card outlined>
    <v-card-text>
      <v-row>
        <v-col cols="12" class="text-subtitle-1 font-weight-bold">
          <span>{{ project.doc_type }}</span>
          <br>
          <span>{{ project.name }}</span>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          Aucune procédure existante pour ce {{ project.doc_type }}.
        </v-col>
      </v-row>
    </v-card-text>
    <v-card-actions>
      <v-btn color="primary" tile disabled>
        Ajouter une procedure
      </v-btn>
      <v-btn color="primary" tile depressed nuxt :to="`/trames/projet-${project.id}`">
        Modifier le PAC
      </v-btn>
      <!-- <v-btn
        color="primary"
        tile
        depressed
        :href="`/api/pdf/${project.id}`"
        @click="downloadPdf"
      >
        PDF
      </v-btn> -->
      <!-- <v-btn
        color="primary"
        tile
        depressed
        :loading="loadingPdf"
        :disabled="loadingPdf"
        @click="downloadPdf"
      >
        PDF
      </v-btn>
      <a ref="pdfLink" :href="pdfUrl" :download="project.name">TEST</a> -->
    </v-card-actions>
  </v-card>
</template>
<script>
import axios from 'axios'

export default {
  props: {
    project: {
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

      if (!this.pdfUrl) {
        const { data } = await axios({
          method: 'get',
          url: `/api/pdf/${this.project.id}`
        })

        const blob = new Blob([data], { type: 'application/pdf' })
        this.pdfUrl = URL.createObjectURL(blob)
      }

      // console.log(this.$refs.pdfLink.click)

      this.$refs.pdfLink.click()
    }
  }
}
</script>
