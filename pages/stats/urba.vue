<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-tabs v-model="statTab">
          <v-tab>Cartes</v-tab>
          <v-tab>Communes</v-tab>
          <!-- <v-tab>Population</v-tab> -->
        </v-tabs>
      </v-col>
      <v-col cols="12">
        <v-tabs-items v-model="statTab">
          <v-tab-item>
            <!-- Cartes -->
            <v-row>
              <v-col cols="3">
                <StatsTextCard text="Type de documents par communes." />
              </v-col>
              <v-col cols="9">
                <StatsUrbaCommunesMap />
              </v-col>
            </v-row>
          </v-tab-item>
          <v-tab-item>
            <!-- Communes -->
            <v-row>
              <v-col cols="12">
                <VDeptAutocomplete v-model="selectedDept" clearable />
              </v-col>
            </v-row>
            <StatsUrbaDocTypesDashboard :params="params" />
            <StatsUrbaCompetencesDocTypesDashboard :params="params" />
          </v-tab-item>
        </v-tabs-items>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>

export default {
  data () {
    return {
      // selectedRegion: '',
      selectedDept: null,
      statTab: 0
    }
  },
  computed: {
    params () {
      const parsedDeptCode = this.$options.filters.deptNumberToString(this.selectedDept?.code_departement)

      if (parsedDeptCode) {
        return {
          collectivite_departement_code: parsedDeptCode
        }
      } else {
        return {}
      }
    }
  }
}
</script>
