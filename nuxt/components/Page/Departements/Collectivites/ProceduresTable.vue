<script>
import { mdiArrowRight, mdiSubdirectoryArrowRight } from '@mdi/js'

export default {
  props: {
    value: {
      default: () => [],
      type: Array
    }
  },
  data () {
    return {
      icons: {
        mdiArrowRight,
        mdiSubdirectoryArrowRight
      }
    }
  },
  computed: {
    departmentCode () {
      return this.$route.params.code_departement?.padStart(2, '0') || null
    },
    selection () {
      return this.$route.query.selection || null
    },
    territorialAuthorityCode () {
      return this.$route.params.code_collectivite || null
    }
  }
}
</script>

<template>
  <DUTable
    cols="5fr 7fr 2fr 5fr 7fr 5fr 5fr 3rem"
    top="94px"
  >
    <template #header>
      <DUTableCell>Statut</DUTableCell>
      <DUTableCell>Procédure</DUTableCell>
      <DUTableCell>N°</DUTableCell>
      <DUTableCell>Type de DU</DUTableCell>
      <DUTableCell>{{ selection === 'plu' ? 'Commune' : 'Collectivité porteuse' }}</DUTableCell>
      <DUTableCell>Prescrit le</DUTableCell>
      <DUTableCell>Approuvé le</DUTableCell>
      <DUTableCell />
    </template>
    <template #default>
      <template v-for="procedure in value">
        <DUTableRow
          :key="procedure.id"
          primary
          :title="procedure.name"
          :to="{
            name: 'departements-code_departement-collectivites-code_collectivite-procedures-id_procedure',
            params: {
              code_collectivite: territorialAuthorityCode,
              code_departement: departmentCode,
              id_procedure: procedure.id
            }
          }"
        >
          <DUTableCell>
            <ProcedureStatus
              v-if="procedure.status"
              :value="procedure.status"
            />
          </DUTableCell>
          <DUTableCell primary>
            {{ procedure.type }}
          </DUTableCell>
          <DUTableCell>{{ procedure.number }}</DUTableCell>
          <DUTableCell>
            <DUTag sm>
              {{ procedure.documentType }}
            </DUTag>
          </DUTableCell>
          <DUTableCell>{{ selection === 'plu' ? procedure.townName : procedure.territorialAuthorityName }}</DUTableCell>
          <DUTableCell>{{ procedure.prescriptionDate }}</DUTableCell>
          <DUTableCell>{{ procedure.approvalDate }}</DUTableCell>
          <DUTableCell link>
            <VIcon small>
              {{ icons.mdiArrowRight }}
            </VIcon>
          </DUTableCell>
        </DUTableRow>
        <DUTableRow
          v-for="secondaryProcedure in procedure.procedures"
          :key="secondaryProcedure.id"
          :title="secondaryProcedure.name"
          :to="{
            name: 'departements-code_departement-collectivites-code_collectivite-procedures-id_procedure',
            params: {
              code_collectivite: territorialAuthorityCode,
              code_departement: departmentCode,
              id_procedure: secondaryProcedure.id
            }
          }"
        >
          <DUTableCell>
            <ProcedureStatus
              v-if="secondaryProcedure.status"
              :value="secondaryProcedure.status"
            />
          </DUTableCell>
          <DUTableCell>
            <VIcon small>
              {{ icons.mdiSubdirectoryArrowRight }}
            </VIcon>
            {{ secondaryProcedure.type }}
          </DUTableCell>
          <DUTableCell>{{ secondaryProcedure.number }}</DUTableCell>
          <DUTableCell />
          <DUTableCell>{{ selection === 'plu' ? secondaryProcedure.townName : secondaryProcedure.territorialAuthorityName }}</DUTableCell>
          <DUTableCell>{{ secondaryProcedure.prescriptionDate }}</DUTableCell>
          <DUTableCell>{{ secondaryProcedure.approvalDate }}</DUTableCell>
          <DUTableCell link>
            <VIcon small>
              {{ icons.mdiArrowRight }}
            </VIcon>
          </DUTableCell>
        </DUTableRow>
      </template>
    </template>
  </DUTable>
</template>
