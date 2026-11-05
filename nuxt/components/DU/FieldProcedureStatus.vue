<script>
import { ProcedureStatus } from '~/store/procedure'

export default {
  props: {
    id: {
      default: undefined,
      type: String,
    },
    value: {
      default: () => [],
      type: Array,
    },
  },
  computed: {
    options() {
      return [{
        label: 'En projet',
        value: ProcedureStatus.InPlanning,
      }, {
        label: 'En cours',
        value: ProcedureStatus.InProgress,
      }, {
        label: 'Approuvé',
        value: ProcedureStatus.Approved,
      }, {
        label: 'Opposable',
        value: ProcedureStatus.Opposable,
      }, {
        label: 'Précédent',
        value: ProcedureStatus.Previous,
      }, {
        label: 'Abandonné',
        value: ProcedureStatus.Abandoned,
      }, {
        label: 'Annulé',
        value: ProcedureStatus.Canceled,
      }, {
        label: 'Abrogé',
        value: ProcedureStatus.Repealed,
      }, {
        label: 'Caduc',
        value: ProcedureStatus.Obsolete,
      }]
    },
  },
}
</script>

<template>
  <FRFieldMultiselect :id="id"
                      :options="options"
                      placeholder="Tout statut"
                      :value="value"
                      @input="$emit('input', $event)">
    <template #default>
      <slot />
    </template>
    <template #option="{ value }">
      <DUProcedureStatus sm
                         :value="value" />
    </template>
  </FRFieldMultiselect>
</template>
