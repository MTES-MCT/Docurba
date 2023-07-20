<template>
  <v-row v-if="procedures && procedures.length > 0 && collectiviteType === 'epci'">
    <v-col>
      <v-tabs
        v-model="tab"
        background-color="primary"
        dark
      >
        <v-tab>
          DU intercommunaux
        </v-tab>
        <v-tab>
          DU communaux
        </v-tab>
      </v-tabs>

      <v-tabs-items v-model="tab" :class="{beige: !isPublic}">
        <v-tab-item>
          <DashboardDUItem
            v-for="(procedure,i) in DUInter"
            :key="'du_' + i"
            :procedure="procedure"
            :censored="isPublic"
          />
        </v-tab-item>
        <v-tab-item>
          <DashboardDUItem
            v-for="(procedure,i) in DUCommunaux"
            :key="'du_' + i"
            :procedure="procedure"
            :censored="isPublic"
          />
        </v-tab-item>
      </v-tabs-items>
    </v-col>
  </v-row>
  <v-row v-else-if="procedures && procedures.length > 0 && collectiviteType === 'commune'">
    <v-col cols="12">
      <DashboardDUItem
        v-for="(procedure,i) in procedures"
        :key="'du_' + i"
        :procedure="procedure"
        :censored="isPublic"
      />
    </v-col>
  </v-row>
  <v-row v-else-if="procedures && procedures.length === 0 ">
    <v-col cols="12">
      <div class="text--secondary beige pa-6 mb-12 rounded">
        Cette collectivité n'a pas de documents d'urbanisme sous sa compétence.
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
export default {
  name: 'DUItemsList',
  props: {
    procedures: {
      type: Array,
      default: () => null
    },
    collectiviteType: {
      type: String,
      default: () => null
    },
    isPublic: {
      type: Boolean,
      default: () => false
    }
  },
  data () {
    return {
      tab: null
    }
  },
  computed: {
    DUCommunaux () {
      return this.procedures?.filter(e => e.perimetre.length === 1)
    },
    DUInter () {
      return this.procedures?.filter(e => e.perimetre.length > 1)
    }
  }
}
</script>
