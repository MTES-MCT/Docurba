<script setup lang="ts">
import { computed } from 'vue'
import FrBadge from '@/components/FrBadge.vue'
import { LABEL_BY_PROCEDURE_STATUS, ProcedureStatus } from '@/data/Procedure'

interface Props {
  value: ProcedureStatus
}

const {
  value,
} = defineProps<Props>()

const elementClass = computed<string>(() => `dc-procedure-status--${(() => {
  switch (value) {
    case ProcedureStatus.ABANDONNEE:
      return 'abandonnee'
    case ProcedureStatus.ABROGEE:
      return 'abrogee'
    case ProcedureStatus.ANNULEE:
      return 'annulee'
    case ProcedureStatus.APPROUVEE:
      return 'approuvee'
    case ProcedureStatus.CADUC:
      return 'caduc'
    case ProcedureStatus.EN_COURS:
      return 'en-cours'
    case ProcedureStatus.EN_PROJET:
      return 'en-projet'
    case ProcedureStatus.OPPOSABLE:
      return 'opposable fr-icon--before fr-icon--before-checkbox-circle-fill'
    case ProcedureStatus.PRECEDENTE:
      return 'precedente'
  }
})()}`)
const label = computed<string>(() => LABEL_BY_PROCEDURE_STATUS[value])
</script>

<template>
  <FrBadge :class="elementClass">{{ label }}</FrBadge>
</template>

<style>
.dc-procedure-status--abandonnee.fr-badge,
.dc-procedure-status--caduc.fr-badge {
  background-color: var(--color-grey-975-75);
  color: var(--color-grey-625-425);
}
.dc-procedure-status--abrogee.fr-badge,
.dc-procedure-status--annulee.fr-badge {
  background-color: var(--color-warning-950-100);
  color: var(--color-warning-425-625);
}
.dc-procedure-status--approuvee.fr-badge,
.dc-procedure-status--opposable.fr-badge {
  background-color: var(--color-green-emeraude-950-sun-425);
  color: var(--color-green-emeraude-sun-425-950);
}
.dc-procedure-status--en-cours.fr-badge {
  background-color: var(--color-blue-ecume-950-sun-247);
  color: var(--color-blue-ecume-sun-247-950);
}
.dc-procedure-status--en-projet.fr-badge {
  background-color: var(--color-yellow-tournesol-950-sun-407);
  color: var(--color-yellow-tournesol-sun-407-950);
}
.dc-procedure-status--precedente.fr-badge {
  background-color: var(--color-grey-950-100);
  color: var(--color-grey-425-625);
}
</style>
