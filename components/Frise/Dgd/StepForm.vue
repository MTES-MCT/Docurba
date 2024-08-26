<template>
  <div class="d-flex">
    <v-text-field
      v-model="step.name"
      style="min-width: 275px;"
      dense
      filled
      placeholder="Étape prévue pour le versement"
      class="mr-2"
    />
    <v-text-field v-model="step.amount" dense filled placeholder="Montant" class="mr-2" />
    <v-text-field v-model="step.date" dense filled placeholder="Date" class="mr-2" />
    <v-select
      v-model="step.category"
      :items="['1', '2', '3']"
      dense
      filled
      style="max-width: 90px;"
      placeholder="Categorie"
      class="mr-2"
    />
    <v-select
      v-model="step.isDone"
      style="max-width: 90px;"
      :items="['oui','non']"
      dense
      filled
      placeholder="Effectué"
    />
    <div class="d-flex ml-2 ">
      <v-btn
        depressed
        color="primary"
        height="40"
        class="mr-2"
        @click="$emit('save', step)"
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
import { mdiCheck, mdiClose } from '@mdi/js'

export default
{
  name: 'StepForm',
  data () {
    return {
      icons: {

        mdiCheck,
        mdiClose
      },
      step: {
        name: '',
        isDone: false,
        category: '1',
        amount: 0,
        date: ''
      }
    }
  }
}
</script>
