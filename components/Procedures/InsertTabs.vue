<template>
  <v-container class="border-grey pb-8 px-8 mb-16">
    <v-row>
      <v-col cols="12" class="pt-0 pb-8">
        <v-tabs v-model="tab" class="py-4">
          <v-tab>Procédure principale</v-tab>
          <v-tab>Procédure secondaire</v-tab>
        </v-tabs>
      </v-col>
    </v-row>
    <v-tabs-items v-model="tab">
      <v-tab-item>
        <ProceduresInsertForm :collectivite="collectivite" procedure-category="principale" />
      </v-tab-item>
      <v-tab-item>
        <ProceduresInsertForm :collectivite="collectivite" procedure-category="secondaire" />
      </v-tab-item>
    </v-tabs-items>
  </v-container>
</template>
<script>
export default {
  props: {
    collectivite: {
      type: Object,
      required: true
    }
  },
  data () {
    return {
      tab: null
    }
  },
  mounted () {
    if (this.$route.query.secondary_id) {
      this.tab = 1
    }
  }
}
</script>
