<template>
  <validation-observer ref="observerVersementForm" v-slot="{ handleSubmit, invalid }">
    <form @submit.prevent="handleSubmit(save)">
      <div class="d-flex">
        <div class="flex-grow-1">
          <div>Montant total</div>
          <validation-provider v-slot="{ errors }" name="Montant" rules="required|integer">
            <v-text-field v-model="amount" type="number" :error-messages="errors" dense filled />
          </validation-provider>
        </div>
        <div class="ml-2 flex-grow-1">
          <div>Année</div>
          <validation-provider v-slot="{ errors }" name="Année" rules="required">
            <v-select
              v-model="year"
              :items="yearsItems"
              :error-messages="errors"
              dense
              filled
              placeholder="Sélectionnez"
            />
          </validation-provider>
        </div>
        <div class="ml-2 flex-grow-1">
          <div>Catégorie</div>
          <validation-provider v-slot="{ errors }" name="Catégorie" rules="required">
            <v-select
              v-model="category"
              :items="['1', '2', '3']"
              dense
              filled
              placeholder="Sélectionnez"
              :error-messages="errors"
            />
          </validation-provider>
        </div>
        <div class="d-flex ml-2 " style="margin-top:23px">
          <v-btn
            depressed
            color="primary"
            height="40"
            class="mr-2 pa-0"
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
      </div>
    </form>
  </validation-observer>
</template>

<script>
import { mdiCheck, mdiClose, mdiDotsVertical } from '@mdi/js'
import FormInput from '@/mixins/FormInput.js'

export default {
  name: 'VersementForm',
  mixins: [FormInput],
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
