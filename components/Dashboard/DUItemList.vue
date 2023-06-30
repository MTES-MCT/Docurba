<template>
  <v-row v-if="procedures && procedures.length > 0">
    <v-col cols="12">
      <DashboardDUItem
        v-for="(procedure,i) in procedures"
        :key="'du_' + i"
        :procedure="procedure"
        censored
      />
    </v-col>
  </v-row>
  <v-row v-else-if="procedures && procedures.length === 0">
    <v-col cols="12">
      <div class="text--secondary beige pa-6 mb-12 rounded">
        Cette collectivité n'a pas de documents d'urbanisme sous ca compétence.
      </div>
    </v-col>
  </v-row>
  <v-row v-else>
    <v-col cols="12">
      <VGlobalLoader />
    </v-col>
  </v-row>
</template>

<script>
import SudocuEvents from '@/mixins/SudocuEvents.js'

export default {
  mixins: [SudocuEvents]
}
</script>
