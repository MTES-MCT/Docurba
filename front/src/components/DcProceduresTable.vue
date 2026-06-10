<script setup lang="ts">
import { computed } from 'vue'
import DcProcedureStatus from '@/components/DcProcedureStatus.vue'
import FrPagination from '@/components/FrPagination.vue'
import FrTable from '@/components/FrTable.vue'
import FrTableFilter from '@/components/FrTableFilter.vue'
import FrTableLink from '@/components/FrTableLink.vue'
import FrTableRow from '@/components/FrTableRow.vue'
import FrTag from '@/components/FrTag.vue'
import { useCollectivites } from '@/composables/useCollectivites'
import type { Collectivite } from '@/data/Collectivite'
import { LABEL_BY_DOCUMENT_TYPE } from '@/data/Document'
import type { Procedure } from '@/data/Procedure'
import { LABEL_BY_PROCEDURE_STATUS, LABEL_BY_PROCEDURE_TYPE } from '@/data/Procedure'
import { displayDate, displayNumber } from '@/utils/display'

interface Props {
  count?: number
  size?: number
  value: Array<Procedure>
}

const {
  count = 0,
  size = 0,
  value,
} = defineProps<Props>()

const collectivitesId = computed<Array<string>>(() => {
  const collectivitesId: Array<string> = []
  const existingCollectivitesId: Record<string, boolean> = {}

  value.forEach(({ collectiviteId }) => {
    if (existingCollectivitesId[collectiviteId]) return

    collectivitesId.push(collectiviteId)
    existingCollectivitesId[collectiviteId] = true
  })

  return collectivitesId
})
const { collectivites } = useCollectivites({ ids: collectivitesId })

const collectivitesById = computed<Record<string, Collectivite>>(() => {
  const collectivitesById: Record<string, Collectivite> = {}

  collectivites.value.forEach((collectivite) => {
    collectivitesById[collectivite.id] = collectivite
  })

  return collectivitesById
})
const computedProcedures = computed<Array<{
  computed: {
    collectiviteName: string
    joined: boolean
  }
  displayed: Record<keyof Omit<Procedure, 'children' | 'events'>, string>
  value: Procedure
}>>(() => value.flatMap((procedure) => {
  const joinedProcedures = [procedure, ...procedure.children]

  return joinedProcedures.map((procedure, index) => {
    const collectivite = collectivitesById.value[procedure.collectiviteId]

    return {
      computed: {
        collectiviteName: collectivite ? collectivite.name : '',
        joined: index < joinedProcedures.length - 1,
      },
      displayed: {
        approvalDate: displayDate(procedure.approvalDate),
        collectiviteId: procedure.collectiviteId,
        documentType: procedure.documentType
          ? LABEL_BY_DOCUMENT_TYPE[procedure.documentType]
          : '',
        id: procedure.id,
        number: displayNumber(procedure.number),
        parentId: procedure.parentId ?? '',
        prescriptionDate: displayDate(procedure.prescriptionDate),
        status: LABEL_BY_PROCEDURE_STATUS[procedure.status],
        type: LABEL_BY_PROCEDURE_TYPE[procedure.type],
      },
      value: procedure,
    }
  })
}))
const pagesCount = computed<number>(() =>
  Math.floor(count / size) + Math.min(count % size, 1)
)
</script>

<template>
  <FrTable>
    <template #header>
      <th>
        <FrTableFilter>
          <template #default>Statut</template>
          <template #action>Filtrer</template>
        </FrTableFilter>
      </th>
      <th>Procédure</th>
      <th>N°</th>
      <th>Type de DU</th>
      <th>Collectivité en charge</th>
      <th>Prescrit le</th>
      <th>Approuvé le</th>
      <th />
    </template>
    <template #default>
      <FrTableRow v-for="{ computed, displayed, value } in computedProcedures"
                  :key="value.id"
                  class="fr-link-container"
                  :joined="computed.joined">
        <td>
          <DcProcedureStatus :value="value.status" />
        </td>
        <td v-if="value.parentId"
            class="fr-icon--before fr-icon--before-corner-down-right-line fr-icon--inline">{{ displayed.type }}</td>
        <td v-else>
          <strong>{{ displayed.type }}</strong>
        </td>
        <td>{{ displayed.number }}</td>
        <td>
          <FrTag>{{ displayed.documentType }}</FrTag>
        </td>
        <td>{{ computed.collectiviteName }}</td>
        <td>{{ displayed.prescriptionDate }}</td>
        <td>{{ displayed.approvalDate }}</td>
        <td>
          <FrTableLink title="Voir le détail de la procédure"
                        :to="`/procedures/${value.id}`">Voir le détail de la procédure</FrTableLink>
        </td>
      </FrTableRow>
    </template>
  </FrTable>
  <FrPagination v-if="pagesCount > 1"
                :size="pagesCount" />
</template>
