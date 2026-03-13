<template>
  <v-row>
    <v-col cols="12" class="mt-4">
      <p> Périmètre du document d'urbanisme : ({{ perimetre.length }})</p>
      <v-btn
        color="primary"
        class="mr-4"
        outlined
        :disabled="disabled"
        @click="selectAllPerimetre"
      >
        Sélectionner toutes
      </v-btn>
      <v-btn
        color="primary"
        outlined
        :disabled="disabled"
        @click="perimetre = []"
      >
        Déselectionner toutes
      </v-btn>
    </v-col>
    <v-col v-for="(commune) in communes" :key="'commune_'+ commune.code" cols="4">
      <v-checkbox
        v-model="perimetre"
        hide-details
        class="mt-0"
        :disabled="disabled"
        :label="`${commune.intitule} (${commune.code})`"
        :value="commune.code"
      />
    </v-col>
  </v-row>
</template>
<script>

export default {
  props: {
    communes: {
      type: Array,
      default: () => []
    },
    value: {
      type: Array,
      required: true
    },
    disabled: {
      type: Boolean,
      default: false
    }
  },
  data () {
    console.log('perimetre', this.communes)
    return {
      perimetre: this.value
    }
  },
  watch: {
    perimetre (newVal) {
      this.$emit('input', this.perimetre)
    }
  },

  methods: {
    selectAllPerimetre () {
      this.perimetre = this.communes.map(c => c.code)
    }
  }
}
</script>
