<script setup lang="ts">
import { computed, watch } from 'vue'
import FrAutocomplete from '@/components/FrAutocomplete.vue'
import FrButton from '@/components/FrButton.vue'
import FrCard from '@/components/FrCard.vue'
import FrContainer from '@/components/FrContainer.vue'
import { useCollectivites } from '@/composables/useCollectivites'
import { useDepartements } from '@/composables/useDepartements'
import { useRouteQueryParam } from '@/composables/useRouteQueryParam'
import type { CollectiviteLabel } from '@/data/Collectivite'
import { EPCI_TYPES } from '@/data/Collectivite'
import type { Option, OptionGroup, Options } from '@/data/Option'

// Route
const collectiviteId = useRouteQueryParam<string | null>('collectivite')
const departementId = useRouteQueryParam<string | null>('departement')

// Data
const { collectivites } = useCollectivites({ departementId })
const { departements } = useDepartements()

// View
const collectiviteOptions = computed<Options<string>>(() => {
  if (!departementId.value) {
    return [{
      disabled: true,
      label: 'Sélectionnez un département',
      value: '',
    }]
  }

  const optionsByLabel: Record<CollectiviteLabel, Array<Option<string>>> = {
    Communes: [],
    EPCIs: [],
    Groupements: [],
  }

  for (const collectivite of collectivites.value) {
    const label = collectivite.type === 'COM'
      ? 'Communes'
      : EPCI_TYPES.includes(collectivite.type)
        ? 'EPCIs'
        : 'Groupements'

    optionsByLabel[label].push({
      label: collectivite.name,
      value: collectivite.id,
    })
  }

  const labels: Array<CollectiviteLabel> = ['Groupements', 'EPCIs', 'Communes']
  const optionsGroups: Array<OptionGroup<string>> = []

  for (const label of labels) {
    if (!optionsByLabel[label].length) continue

    optionsGroups.push({
      label,
      options: optionsByLabel[label],
    })
  }

  return optionsGroups
})
const departementOptions = computed<Options<string>>(() =>
  departements.value.map(({ id, name }) => ({ label: `${name} - ${id}`, value: id }))
)

// Watchers
watch(departementId, () => {
  collectiviteId.value = null
})
</script>

<template>
  <FrContainer id="content"
               role="main"
               tag="main"
               vertical>
    <h1 class="fr-text fr-text--center fr-text--h1">Docurba vous accompagne dans l'élaboration de vos PLUs</h1>
    <FrCard>
      <p class="fr-text">Pour commencer, accédez aux ressources de votre territoire :</p>
      <div class="fr-row">
        <div class="fr-col-3">
          <FrAutocomplete :options="departementOptions"
                          placeholder="Département"
                          v-model:value="departementId" />
        </div>
        <div class="fr-col-7">
          <FrAutocomplete :options="collectiviteOptions"
                          placeholder="Commune ou EPCI"
                          v-model:value="collectiviteId" />
        </div>
        <div class="fr-col-2">
          <FrButton :disabled="!collectiviteId"
                    :to="
                      collectiviteId
                        ? `/collectivites/${collectiviteId}`
                        : undefined
                    ">Accéder</FrButton>
        </div>
      </div>
    </FrCard>
  </FrContainer>
</template>
