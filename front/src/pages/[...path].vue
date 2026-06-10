<script setup lang="ts">
import { computed } from 'vue'
import FrBreadcrumbs from '@/components/FrBreadcrumbs.vue'
import FrContainer from '@/components/FrContainer.vue'
import { useAuth } from '@/composables/useAuth'
import type { Option } from '@/data/Option'

// Data
const { user } = useAuth()

// View
const breadcrumbs = computed<Array<Option<string>>>(() => user.value ? [{
  label: `Mes collectivités (${user.value.departementId})`,
  value: `/tableau-de-bord/${user.value.departementId}`,
}] : [{
  label: 'Accueil',
  value: '/',
}])
</script>

<template>
  <FrContainer id="content"
               role="main"
               tag="main"
               vertical>
    <FrBreadcrumbs :value="breadcrumbs">Page introuvable</FrBreadcrumbs>
    <h1 class="fr-text fr-text--h1">Page introuvable</h1>
  </FrContainer>
</template>
