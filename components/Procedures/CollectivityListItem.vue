<template>
  <v-list-item>
    <v-list-item-content>
      <v-list-item-title>{{ collectivity.intitule }} ({{ collectivity.code }})</v-list-item-title>
    </v-list-item-content>
    <v-list-item-content>
      <v-list-item-subtitle v-for="procedure in collectivity.procedures" :key="procedure.id">
        <v-chip small label color="alt-beige" class="font-weight-bold">
          {{ procedure.doc_type }}
        </v-chip>
        <v-chip small label :color="procedure.status === 'opposable' ? 'success-light' : 'bf200'">
          <span
            :class="procedure.status === 'opposable' ? 'success--text' : 'bf200--text'"
            class="text-uppercase font-weight-bold"
          >
            {{ procedure.status }}
          </span>
        </v-chip>
      </v-list-item-subtitle>
    </v-list-item-content>
  </v-list-item>
</template>

<script>
export default {
  props: {
    collectivity: {
      type: Object,
      required: true
    }
  }
}
</script>
