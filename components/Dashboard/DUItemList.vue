<template>
  <v-row>
    <v-col cols="12">
      <DashboardDUItem
        v-for="(procedure,i) in procedures"
        :key="'du_' + i"
        :procedure="procedure"
        censored
      />
    </v-col>
  </v-row>
</template>

<script>
import SudocuEvents from '@/mixins/SudocuEvents.js'

export default {
  mixins: [SudocuEvents]
}
</script>
