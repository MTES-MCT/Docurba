<template>
  <v-menu v-model="menu" :close-on-content-click="false" min-width="auto">
    <template #activator="{on}">
      <v-text-field
        readonly
        filled
        :label="label"
        :value="desplayedDate"
        hide-details
        v-on="on"
      >
        <template #append>
          <v-icon>{{ icons.mdiCalendar }}</v-icon>
        </template>
      </v-text-field>
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

export default {
  model: {
    prop: 'date',
    event: 'input'
  },
  props: {
    date: {
      type: String,
      default () { return this.$dayjs().format('YYYY-MM-DD') }
    },
    label: {
      type: String,
      default: 'Date'
    },
    diplayedFormat: {
      type: String,
      default: 'DD/MM/YYYY'
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
