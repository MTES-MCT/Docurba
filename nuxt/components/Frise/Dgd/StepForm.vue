<template>
  <validation-observer ref="observerStepForm" v-slot="{ handleSubmit, invalid }">
    <form @submit.prevent="handleSubmit(save)">
      <div class="d-flex align-baseline">
        <validation-provider v-slot="{ errors }" name="Nom" rules="required">
          <v-text-field
            v-model="step.name"
            required
            style="min-width: 340px;"
            dense
            filled
            label="Étape prévue pour le versement"
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
            label="Montant"
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
            label="Date"
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
            style="max-width: 100px;"
            label="Categorie"
            class="mr-2"
            :error-messages="errors"
          />
        </validation-provider>
        <validation-provider v-slot="{ errors }" name="État" rules="required">
          <v-select
            v-model="step.isDone"
            style="max-width: 100px;"
            :items="[{text:'oui', value: true},{text:'non', value: false}]"
            dense
            filled
            label="Effectué"
            :error-messages="errors"
          />
        </validation-provider>

        <v-btn
          depressed
          color="primary"
          height="40"
          class="mx-2"
          :disabled="invalid"
          type="submit"
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
        isDone: this.value.is_done || null,
        category: this.value.category || '',
        amount: this.value.amount || '',
        date: this.value.date || ''
      }
    }
  },
  methods: {
    save () {
      this.$emit('save', { id: this.value.id, ...this.step })
    }
  }
}
</script>
