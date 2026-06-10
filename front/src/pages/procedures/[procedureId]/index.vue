<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import DcProceduresTable from '@/components/DcProceduresTable.vue'
import FrBreadcrumbs from '@/components/FrBreadcrumbs.vue'
import FrButton from '@/components/FrButton.vue'
import FrContainer from '@/components/FrContainer.vue'
import { useCollectivite } from '@/composables/useCollectivite'
import { useProcedure } from '@/composables/useProcedure'
import type { Option } from '@/data/Option'
import { LABEL_BY_PROCEDURE_TYPE } from '@/data/Procedure'

// Route
const route = useRoute()

const procedureId = computed<string>(() => String(route.params.procedureId))

// Data
const collectiviteId = computed<string | null>(() =>
  procedure.value && procedure.value.collectiviteId
)

const { procedure } = useProcedure(procedureId)
const { collectivite } = useCollectivite(collectiviteId)

// View
const breadcrumbs = computed<Array<Option<string>>>(() => collectivite.value ? [{
  label: `Mes collectivités (${collectivite.value.departementId})`,
  value: `/tableau-de-bord/${collectivite.value.departementId}`,
}, {
  label: collectivite.value.name,
  value: `/collectivites/${collectivite.value.id}`
}] : [])
const label = computed<string>(() =>
  procedure.value ? `${
    LABEL_BY_PROCEDURE_TYPE[procedure.value.type]
  } ${
    procedure.value.number ?? ''
  }` : 'Procédure'
)
const rootProcedureId = computed<string>(() =>
  (procedure.value && procedure.value.parentId) ?? procedureId.value
)
</script>

<template>
  <div class="fr-bg--blue">
    <FrContainer vertical>
      <FrBreadcrumbs :value="breadcrumbs">{{ label }}</FrBreadcrumbs>
      <div class="fr-row fr-row--between">
        <div class="fr-col fr-col--center">
          <h1 class="fr-text fr-text--h1">{{ label }}</h1>
        </div>
        <div class="fr-col fr-col--center">
          <FrButton class="fr-icon--before fr-icon--before-add-line"
                    :to="`/procedures/${rootProcedureId}/creation`">Ajouter une procédure secondaire</FrButton>
        </div>
      </div>
    </FrContainer>
  </div>
  <FrContainer id="content"
               role="main"
               tag="main"
               vertical>
    <h2 class="fr-text fr-text--h2">Documents d'urbanisme</h2>
    <DcProceduresTable v-if="procedure"
                       :value="[procedure]" />
  </FrContainer>
</template>
