<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import DcProcedureStatus from '@/components/DcProcedureStatus.vue'
import DcProceduresTable from '@/components/DcProceduresTable.vue'
import FrBreadcrumbs from '@/components/FrBreadcrumbs.vue'
import FrButton from '@/components/FrButton.vue'
import FrCard from '@/components/FrCard.vue'
import FrContainer from '@/components/FrContainer.vue'
import FrLink from '@/components/FrLink.vue'
import FrSegmented from '@/components/FrSegmented.vue'
import FrSidemenu from '@/components/FrSidemenu.vue'
import FrTextSegmented from '@/components/FrTextSegmented.vue'
import { useCollectivite } from '@/composables/useCollectivite'
import { useProcedures } from '@/composables/useProcedures'
import { useRouteQueryParam } from '@/composables/useRouteQueryParam'
import type { DocumentTypesGroup } from '@/data/Document'
import { DOCUMENT_TYPES_GROUPS, DocumentType } from '@/data/Document'
import type { Option } from '@/data/Option'
import type { Procedure } from '@/data/Procedure'
import { ProcedureStatus } from '@/data/Procedure'

// Route
const route = useRoute()

const displayMode = useRouteQueryParam<string>('affichage', {
  fromQuery: (query) => query === 'liste' ? 'list' : 'table',
  toQuery: (value) => value === 'list' ? 'liste' : undefined,
})
const pageNumber = useRouteQueryParam<number>('page', {
  fromQuery: (query) => {
    const number = Number(query)

    return Number.isNaN(number) ? 1 : number
  },
  toQuery: (value) => value === 1 ? undefined : String(value),
})

const collectiviteId = computed<string>(() => String(route.params.collectiviteId))
const documentTypesGroupId = computed<string>(() =>
  route.params.documentTypesGroupId ? String(route.params.documentTypesGroupId) : ''
)

// Data
const pageSize = ref(25)

const intercommunaliteId = computed<string | null>(() =>
  collectivite.value && collectivite.value.intercommunaliteId
)

const { collectivite } = useCollectivite(collectiviteId)
const { collectivite: intercommunalite } = useCollectivite(intercommunaliteId)
const { procedures, proceduresCount } = useProcedures({ collectiviteId }, pageNumber, pageSize)

// View
const displayOptions = [{
  label: 'Tableau',
  value: 'table',
}, {
  label: 'Liste',
  value: 'list',
}]

const breadcrumbs = computed<Array<Option<string>>>(() => {
  const breadcrumbs: Array<Option<string>> = []

  if (!collectivite.value) {
    return breadcrumbs
  }

  breadcrumbs.push({
    label: `Mes collectivités (${collectivite.value.departementId})`,
    value: `/tableau-de-bord/${collectivite.value.departementId}`,
  })

  if (intercommunalite.value) {
    breadcrumbs.push({
      label: intercommunalite.value.name,
      value: `/collectivites/${intercommunalite.value.id}`,
    })
  }

  return breadcrumbs
})
const displayedCode = computed<string>(() =>
  collectivite.value
    ? collectivite.value.intercommunaliteId
      ? `Code INSEE ${collectivite.value.id}`
      : `SIREN ${collectivite.value.id.match(/.{1,3}/g)?.join(' ')}`
    : ''
)
const documentTypesGroup = computed<DocumentTypesGroup>(() =>
  DOCUMENT_TYPES_GROUPS.find(({ id }) => id === documentTypesGroupId.value)
  ?? DOCUMENT_TYPES_GROUPS[1]!
)
const filteredProcedures = computed<Array<Procedure>>(() =>
  procedures.value.filter(({ documentType }) =>
    documentTypesGroup.value.types.includes(documentType)
  )
)
const menuOptions = computed<Array<Option<string>>>(() => {
  if (!procedures.value || !procedures.value.length) {
    return []
  }
  const existingDocumentTypes: Record<DocumentType, boolean> = Object.fromEntries(
    Object.values(DocumentType).map((type) => [type, false])
  ) as Record<DocumentType, boolean>

  procedures.value.forEach((procedure) => {
    if (existingDocumentTypes[procedure.documentType]) return

    existingDocumentTypes[procedure.documentType] = true
  })

  const menuOptions: Array<Option<string>> = []

  for (const { id, label, types } of DOCUMENT_TYPES_GROUPS) {
    if (types.every((type) => !existingDocumentTypes[type])) continue

    menuOptions.push({
      label,
      value: `/collectivites/${collectiviteId.value}${id ? `/${id}` : ''}`,
    })
  }

  return menuOptions
})
</script>

<template>
  <div v-if="collectivite"
       class="fr-bg--blue">
    <FrContainer vertical>
      <FrBreadcrumbs :value="breadcrumbs">{{ collectivite.name }}</FrBreadcrumbs>
      <h1 class="fr-text fr-text--h1">{{ collectivite.name }}</h1>
      <div class="fr-row fr-row--between">
        <div class="fr-col fr-col--center">
          <FrTextSegmented>
            <span>{{ displayedCode }}</span>
            <span v-if="!intercommunalite">
              <FrLink>Périmètre : {{ collectivite.membersId.length }} commune{{ collectivite.membersId.length === 1 ? '' : 's' }}</FrLink>
            </span>
            <span>
              <FrLink>Plus d'informations</FrLink>
            </span>
          </FrTextSegmented>
        </div>
        <div class="fr-col fr-col--center">
          <FrButton class="fr-icon--before fr-icon--before-add-line"
                    :to="`/collectivites/${collectiviteId}/procedures/creation`">Ajouter une procédure</FrButton>
        </div>
      </div>
    </FrContainer>
  </div>
  <FrContainer id="content"
               role="main"
               tag="main"
               vertical>
    <div class="fr-row">
      <div class="fr-col-12 fr-col-md-3">
        <FrSidemenu :options="menuOptions" />
      </div>
      <div class="fr-col-12 fr-col-md-9">
        <h2 class="fr-text fr-text--h2">{{ documentTypesGroup.description }}</h2>
        <FrSegmented id="display"
                     :options="displayOptions"
                     v-model:value="displayMode">
          <template #label="{ id, option }">
            <label class="fr-icon--before"
                   :class="`fr-icon--before-${option.value === 'table' ? 'table-line' : 'list-unordered'}`"
                   :for="id">{{ option.label }}</label>
          </template>
        </FrSegmented>
        <FrContainer v-if="displayMode === 'list'"
                     class="fr-bg--grey"
                     vertical>
          <FrCard>
            <DcProcedureStatus :value="ProcedureStatus.OPPOSABLE" />
          </FrCard>
        </FrContainer>
        <DcProceduresTable v-else
                           :count="proceduresCount"
                           :size="pageSize"
                           :value="filteredProcedures" />
      </div>
    </div>
  </FrContainer>
</template>
