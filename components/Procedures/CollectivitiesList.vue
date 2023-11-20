<template>
  <v-list>
    <v-list-item-group v-model="selectedCollectivities" multiple>
      <template v-for="(collectivity, i) in collectivities">
        <v-divider v-if="i > 0" :key="i" />
        <ProceduresCollectivityListItem :key="collectivity.code" :collectivity="collectivity" />
      </template>
    </v-list-item-group>
  </v-list>
</template>

<script>
export default {
  props: {
    collectivities: {
      type: Array,
      required: true
    }
  },
  data () {
    return {
      selectedCollectivities: []
    }
  }
}
</script>
