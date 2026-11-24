<script>
import { mdiArrowRight, mdiInformation, mdiSubdirectoryArrowRight } from '@mdi/js'

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
        mdiInformation,
        mdiSubdirectoryArrowRight
      }
    }
  },
  computed: {
    selection () {
      return this.$route.query.selection || null
    }
  }
}
</script>

<template>
  <DUTable
    card
    cols="5 7 2 5 7 5 5 fixed"
    top="94px"
  >
    <template #header>
      <DUTableCell>Statut</DUTableCell>
      <DUTableCell>
        Procédure
        <VIcon
          small
          title="Les procédures engagées avant le 26 mai 2026 sont antérieures à la loi Huwart"
        >
          {{ icons.mdiInformation }}
        </VIcon>
      </DUTableCell>
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
          :title="procedure.name"
          :to="`/frise/${procedure.id}`"
        >
          <DUTableCell>
            <ProcedureStatus
              v-if="procedure.status"
              :value="procedure.status"
            />
          </DUTableCell>
          <DUTableCell>
            <strong>
              {{ procedure.type }}
              <template v-if="procedure.nameDetails">
                <br>
                <em>{{ procedure.nameDetails }}</em>
              </template>
            </strong>
          </DUTableCell>
          <DUTableCell>{{ procedure.number }}</DUTableCell>
          <DUTableCell>
            <DUTag
              actionable-child
              sm
            >
              {{ procedure.documentType }}
            </DUTag>
          </DUTableCell>
          <DUTableCell>{{ procedure.territorialAuthorityName }}</DUTableCell>
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
          secondary
          :title="secondaryProcedure.name"
          :to="`/frise/${secondaryProcedure.id}`"
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
            <div>
              {{ secondaryProcedure.type }}
              <template v-if="secondaryProcedure.nameDetails">
                <br>
                <em>{{ secondaryProcedure.nameDetails }}</em>
              </template>
            </div>
          </DUTableCell>
          <DUTableCell>{{ secondaryProcedure.number }}</DUTableCell>
          <DUTableCell />
          <DUTableCell>{{ secondaryProcedure.territorialAuthorityName }}</DUTableCell>
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
