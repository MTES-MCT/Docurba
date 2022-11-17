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
      />
    </template>
    <v-date-picker
      v-model="pickerDate"
      :first-day-of-week="1"
      locale="fr-fr"
    />
  </v-menu>
</template>

<script>
import dayjs from 'dayjs'

export default {
  model: {
    prop: 'date',
    event: 'input'
  },
  props: {
    date: {
      type: String,
      default () { return dayjs().format('YYYY-MM-DD') }
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
      menu: false
    }
  },
  computed: {
    desplayedDate () {
      return dayjs(this.date, 'YYYY-MM-DD').format(this.diplayedFormat)
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
