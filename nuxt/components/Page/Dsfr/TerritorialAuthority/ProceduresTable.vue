<script>
import { mdiArrowRight, mdiInformation, mdiSubdirectoryArrowRight } from '@mdi/js'
import { displayDate } from '~/plugins/utils';

export default {
  props: {
    value: {
      default: () => [],
      type: Array,
    },
  },
  data() {
    return {
      icons: {
        mdiArrowRight,
        mdiInformation,
        mdiSubdirectoryArrowRight,
      },
    }
  },
  computed: {
    displayedProcedures() {
      return this.value.flatMap((primaryProcedure) => [
        primaryProcedure,
        ...primaryProcedure.procedures,
      ].map((procedure, index) => ({
        approvalDate: displayDate(procedure.approvalDate),
        docType: !procedure.parentId && procedure.docType || '',
        id: procedure.id,
        name: procedure.name ?? '',
        nameDetails: procedure.nameDetails ?? '',
        number: procedure.number ?? '',
        parentId: procedure.parentId ?? '',
        prescriptionDate: displayDate(procedure.prescriptionDate),
        secondary: index > 0,
        status: !procedure.parentId && procedure.status || '',
        territorialAuthorityName: (
          !procedure.parentId
          && procedure.territorialAuthority
          && procedure.territorialAuthority.name
        ) || '',
        type: procedure.type,
      })))
    },
    selection() {
      return this.$route.query.selection || null
    },
  },
}
</script>

<template>
  <FRTable cols="5 7 2 5 7 5 5 fixed">
    <template #header>
      <FRTableCell>
        Statut
      </FRTableCell>
      <FRTableCell>
        Procédure
        <FRIcon title="Les procédures engagées avant le 26 mai 2026 sont antérieures à la loi Huwart"
                :value="icons.mdiInformation" />
      </FRTableCell>
      <FRTableCell>
        N°
      </FRTableCell>
      <FRTableCell>
        Type de DU
      </FRTableCell>
      <FRTableCell>
        {{ selection === 'plu' ? 'Commune' : 'Collectivité porteuse' }}
      </FRTableCell>
      <FRTableCell>
        Prescrit le
      </FRTableCell>
      <FRTableCell>
        Approuvé le
      </FRTableCell>
      <FRTableCell />
    </template>
    <template #default>
      <FRTableRow v-for="procedure in displayedProcedures"
                  :key="procedure.id"
                  :secondary="procedure.secondary"
                  :title="procedure.name"
                  :to="{
                    name: 'dsfr-procedures-id_procedure',
                    params: {
                      id_procedure: procedure.id,
                    },
                  }">
        <FRTableCell>
          <DUProcedureStatus v-if="procedure.status"
                             sm
                             :value="procedure.status" />
        </FRTableCell>
        <FRTableCell>
          <FRIcon v-if="procedure.parentId"
                  :value="icons.mdiSubdirectoryArrowRight" />
          <FRGrid>
            <component :is="procedure.parentId ? 'span' : 'strong'">
              {{ procedure.type }}
            </component>
            <em v-if="procedure.nameDetails">
              {{ procedure.nameDetails }}
            </em>
          </FRGrid>
        </FRTableCell>
        <FRTableCell>
          {{ procedure.number }}
        </FRTableCell>
        <FRTableCell>
          <FRTag v-if="procedure.docType"
                 actionable-child
                 sm>
            {{ procedure.docType }}
          </FRTag>
        </FRTableCell>
        <FRTableCell>
          {{ procedure.territorialAuthorityName }}
        </FRTableCell>
        <FRTableCell>
          {{ procedure.prescriptionDate }}
        </FRTableCell>
        <FRTableCell>
          {{ procedure.approvalDate }}
        </FRTableCell>
        <FRTableCell link>
          <FRIcon :value="icons.mdiArrowRight" />
        </FRTableCell>
      </FRTableRow>
    </template>
  </FRTable>
</template>
