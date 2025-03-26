<template>
  <v-menu v-model="menu" :close-on-content-click="false" min-width="auto">
    <template #activator="{on}">
      <validation-provider v-slot="{ errors }" :rules="rules" name="Date">
        <v-text-field
          readonly
          filled
          :label="label"
          :value="desplayedDate"
          hide-details
          :error-messages="errors"
          v-on="on"
        >
          <template #append>
            <v-icon>{{ icons.mdiCalendar }}</v-icon>
          </template>
        </v-text-field>
      </validation-provider>
    </template>
    <v-date-picker
      v-model="pickerDate"
      :first-day-of-week="1"
      locale="fr-fr"
    />
  </v-menu>
</template>

<script>
import { mdiCalendar } from '@mdi/js'
import FormInput from '@/mixins/FormInput'

export default {
  mixins: [FormInput],
  model: {
    prop: 'date',
    event: 'input'
  },
  props: {
    date: {
      type: String,
      default: null
    },
    label: {
      type: String,
      default: 'Date'
    },
    diplayedFormat: {
      type: String,
      default: 'DD/MM/YYYY'
    },
    rules: {
      type: [String, Object, Array],
      default: 'required'
    }
  },
  data () {
    return {
      menu: false,
      icons: { mdiCalendar }
    }
  },
  computed: {
    desplayedDate () {
      if (!this.date) {
        return ''
      }
      return this.$dayjs(this.date, 'YYYY-MM-DD').format(this.diplayedFormat)
    },
    pickerDate: {
      get () {
        return this.date
      },
      set (newDate) {
        this.$emit('input', newDate)
        this.menu = false
      }
    }
  }
}
</script>
