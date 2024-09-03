<template>
  <validation-observer ref="observerStepForm" v-slot="{ handleSubmit, invalid }">
    <form @submit.prevent="handleSubmit(save)">
      <div class="d-flex">
        <validation-provider v-slot="{ errors }" name="Nom" rules="required">
          <v-text-field
            v-model="step.name"
            required
            style="min-width: 275px;"
            dense
            filled
            placeholder="Étape prévue pour le versement"
            class="mr-2"
            :error-messages="errors"
          />
        </validation-provider>
        <validation-provider v-slot="{ errors }" name="Montant" rules="required">
          <v-text-field
            v-model="step.amount"
            :error-messages="errors"
            dense
            filled
            placeholder="Montant"
            class="mr-2"
            type="number"
          />
        </validation-provider>
        <validation-provider v-slot="{ errors }" name="Date" rules="required">
          <v-text-field
            v-model="step.date"
            type="date"
            dense
            filled
            placeholder="Date"
            class="mr-2"
            :error-messages="errors"
          />
        </validation-provider>
        <validation-provider v-slot="{ errors }" name="Catégorie" rules="required">
          <v-select
            v-model="step.category"
            :items="['1', '2', '3']"
            dense
            filled
            style="max-width: 90px;"
            placeholder="Categorie"
            class="mr-2"
            :error-messages="errors"
          />
        </validation-provider>
        <validation-provider v-slot="{ errors }" name="État" rules="required">
          <v-select
            v-model="step.isDone"
            style="max-width: 90px;"
            :items="[{text:'oui', value: true},{text:'non', value: false}]"
            dense
            filled
            placeholder="Effectué"
            :error-messages="errors"
          />
        </validation-provider>

        <div class="d-flex ml-2 ">
          <v-btn
            depressed
            color="primary"
            height="40"
            class="mr-2"
            :disabled="invalid"
            type="submit"
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
    </form>
  </validation-observer>
</template>

<script>
import { mdiCheck, mdiClose } from '@mdi/js'
import FormInput from '@/mixins/FormInput.js'

export default
{
  name: 'StepForm',
  mixins: [FormInput],
  props: {
    value: {
      type: Object,
      default: () => ({})
    }
  },
  data () {
    return {
      icons: {

        mdiCheck,
        mdiClose
      },
      step: {
        name: this.value.name || '',
        isDone: this.value.is_done || false,
        category: this.value.category || '1',
        amount: this.value.amount || '',
        date: this.value.date || ''
      }
    }
  },
  methods: {
    save () {
      this.$emit('save', { ...this.step })
    }
  }
}
</script>
