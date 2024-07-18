<template>
  <div class="d-flex">
    <div class="flex-grow-1">
      <div>Montant total</div>
      <v-text-field v-model="amount" dense filled />
    </div>
    <div class="ml-2 flex-grow-1">
      <div>Année</div>
      <v-select v-model="year" :items="yearsItems" dense filled placeholder="Sélectionnez" />
    </div>
    <div class="ml-2 flex-grow-1">
      <div>Catégorie</div>
      <v-select v-model="category" :items="['1', '2', '3']" dense filled placeholder="Sélectionnez" />
    </div>
    <div class="d-flex ml-2 " style="margin-top:23px">
      <v-btn
        depressed
        color="primary"
        height="40"
        class="mr-2"
        @click="save"
      >
        <v-icon>{{ icons.mdiCheck }}</v-icon>
      </v-btn>
      <v-btn
        color="primary"
        outlined
        depressed
        height="40"
        @click="$emit('cancel')"
      >
        <v-icon>{{ icons.mdiClose }}</v-icon>
      </v-btn>
    </div>
  </div>
</template>

<script>
import { mdiCheck, mdiClose, mdiDotsVertical } from '@mdi/js'

export default {
  name: 'VersementForm',
  data () {
    return {
      amount: null,
      year: null,
      category: null,

      icons: {
        mdiCheck,
        mdiClose,
        mdiDotsVertical
      }
    }
  },
  computed: {
    yearsItems () {
      return Array.from({ length: new Date().getFullYear() - 1900 + 1 }, (v, i) => 1900 + i).reverse()
    }
  },
  methods: {
    save () {
      this.$emit('save', { amount: this.amount, year: this.year, category: this.category })
    }
  }
}
</script>
