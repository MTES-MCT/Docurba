<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import FrButton from '@/components/FrButton.vue'
import FrContainer from '@/components/FrContainer.vue'
import FrField from '@/components/FrField.vue'
import { useAuth } from '@/composables/useAuth'
import { useProcedures } from '@/composables/useProcedures'
import { useRouteQueryParam } from '@/composables/useRouteQueryParam'
import { useDepartements } from '@/composables/useDepartements'
import type { Options } from '@/data/Option'
import DcProceduresTable from '@/components/DcProceduresTable.vue'

// Definitions
definePage({
  meta: {
    signedInOnly: true,
  },
})

// Route
const route = useRoute()
const router = useRouter()

const pageNumber = useRouteQueryParam<number>('page', {
  fromQuery: (query) => {
    const number = Number(query)

    return Number.isNaN(number) ? 1 : number
  },
  toQuery: (value) => value === 1 ? undefined : String(value),
})
const query = useRouteQueryParam<string>('query', {
  fromQuery: (query) => query ?? '',
  toQuery: (value) => value || undefined,
})

// Data
const pageSize = ref(25)

const departementId = computed<string>({
  get() {
    return route.params.departementId
      ? String(route.params.departementId)
      : (user.value && user.value.departementId) ?? ''
  },
  set(newDepartementId: string) {
    router.push({
      params: {
        ...route.params,
        departementId: newDepartementId,
      },
    })
  },
})

const { user } = useAuth()
const { departements } = useDepartements()
const { procedures, proceduresCount } = useProcedures({ departementId }, pageNumber, pageSize)

// View
const departementOptions = computed<Options<string>>(() =>
  departements.value.map(({ id, name }) => ({ label: `${name} - ${id}`, value: id }))
)

// Watchers
watch(departementId, (newDepartementId) => {
  if (newDepartementId === route.params.departementId) return

  router.replace({
    params: {
      departementId: newDepartementId,
    },
  })
}, { immediate: true })
</script>

<template>
  <div class="fr-bg--blue">
    <FrContainer vertical>
      <div class="fr-row fr-row--between">
        <div class="fr-col">
          <h1 class="fr-text fr-text--h1">Mes procédures</h1>
        </div>
        <div class="fr-col fr-col--center">
          <FrButton class="fr-icon--before fr-icon--before-add-line"
                    to="/procedures/creation">Créer une procédure</FrButton>
        </div>
      </div>
    </FrContainer>
  </div>
  <FrContainer id="content"
               role="main"
               tag="main"
               vertical>
    <div class="fr-row fr-row--between">
      <div class="fr-col-12 fr-col-md-4">
        <FrField id="search-departement"
                 :options="departementOptions"
                 type="autocomplete"
                 v-model:value="departementId" />
      </div>
      <div class="fr-col-12 fr-col-md-4">
        <FrField field-class="fr-icon--after fr-icon--after-search-line"
                 id="search-procedure-name"
                 placeholder="Rechercher une procédure"
                 v-model:value="query" />
      </div>
    </div>
    <DcProceduresTable :count="proceduresCount"
                       :size="pageSize"
                       :value="procedures" />
  </FrContainer>
</template>
