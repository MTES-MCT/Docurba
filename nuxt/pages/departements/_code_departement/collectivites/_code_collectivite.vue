<script>
import { mdiArrowRight, mdiMessageAlertOutline, mdiPlus, mdiSubdirectoryArrowRight } from '@mdi/js'
import { orderBy } from 'lodash'
import { displayProcedure } from '~/plugins/procedure'
import { displaySirenCode } from '~/plugins/territorial-authority'

export default {
  data () {
    return {
      icons: {
        mdiArrowRight,
        mdiMessageAlertOutline,
        mdiPlus,
        mdiSubdirectoryArrowRight
      },
      intermunicipality: null,
      pageSize: 6,
      procedures: [],
      territorialAuthority: null
    }
  },
  computed: {
    breadcrumb () {
      const breadcrumb = [{
        label: `Mes collectivités${this.departmentCode ? ` (${this.departmentCode})` : ''}`,
        value: `/departements/${this.departmentCode}/collectivites`
      }]

      if (this.intermunicipality) {
        breadcrumb.push({
          label: this.intermunicipality.name,
          value: `/departements/${this.departmentCode}/collectivites/${this.intermunicipalityCode}`
        })
      }

      return breadcrumb
    },
    departmentCode () {
      return this.$route.params.code_departement || null
    },
    displayedCode () {
      return this.territorialAuthority
        ? this.territorialAuthority.inseeCode
          ? `Code INSEE ${this.territorialAuthority.inseeCode}`
          : `SIREN ${displaySirenCode(this.territorialAuthority.sirenCode)}`
        : ''
    },
    displayedProcedures () {
      if (!(this.documentType in this.proceduresByDocumentType)) {
        return []
      }

      const displayedProcedures = this.proceduresByDocumentType[this.documentType]
        .map(displayProcedure)

      return (
        this.intermunicipalityCode || this.documentType !== 'PLU'
          ? displayedProcedures
          : orderBy(displayedProcedures, ['territorialAuthorityName', 'townName'], ['asc', 'asc'])
      )
    },
    documentType () {
      switch (this.$route.query.type_document) {
        case 'plui':
          return 'PLUi'
        case 'scot':
          return 'SCoT'
        default:
          return 'PLU'
      }
    },
    intermunicipalityCode () {
      return this.territorialAuthority?.intermunicipalityCode || null
    },
    label () {
      return this.territorialAuthority?.name || ''
    },
    page () {
      const pageNumber = Number(this.$route.query.page)

      return !Number.isNaN(pageNumber) && pageNumber ? pageNumber : 1
    },
    pages () {
      return Math.ceil(this.displayedProcedures.length / this.pageSize)
    },
    proceduresByDocumentType () {
      const proceduresByDocumentType = {}

      this.procedures.forEach((procedure) => {
        if (procedure.documentType in proceduresByDocumentType) {
          proceduresByDocumentType[procedure.documentType].push(procedure)
        } else {
          proceduresByDocumentType[procedure.documentType] = [procedure]
        }
      })

      return proceduresByDocumentType
    },
    proceduresLabel () {
      switch (this.documentType) {
        case 'PLUi':
          return 'Plans locaux d’urbanisme intercommunaux'
        case 'SCoT':
          return 'Schémas de cohérence territoriale'
        default:
          return 'Documents d\'urbanisme communaux'
      }
    },
    proceduresPage () {
      return this.displayedProcedures
        .slice((this.page - 1) * this.pageSize, this.page * this.pageSize)
    },
    territorialAuthorityCode () {
      return this.$route.params.code_collectivite || null
    }
  },
  watch: {
    intermunicipalityCode: {
      async handler (value) {
        if (!process.client) {
          return
        }

        this.intermunicipality = value
          ? await this.$territorialAuthorityApi.get(value)
          : null
      },
      immediate: true
    },
    territorialAuthorityCode: {
      async handler (value) {
        if (!process.client) {
          return
        }

        this.territorialAuthority = value
          ? await this.$territorialAuthorityApi.get(value, { includeMembers: true })
          : null

        if (this.territorialAuthority) {
          const codes = []
          const existingCodes = {}

          for (const { code, type } of [
            this.territorialAuthority,
            ...this.territorialAuthority.members
          ]) {
            if (type === 'COM' && !existingCodes[code]) {
              existingCodes[code] = true
              codes.push(code)
            }
          }

          this.procedures = await this.$procedureApi.listForTerritorialAuthorities(codes)
        } else {
          this.procedures = []
        }
      },
      immediate: true
    }
  }
}
</script>

<template>
  <LayoutMain v-if="territorialAuthority">
    <LayoutHeader :breadcrumb="breadcrumb" :label="label">
      <template #infos>
        <div>{{ displayedCode }}</div>
        <div v-if="territorialAuthority.members.length">
          <NuxtLink to="#">
            Périmètre : {{ territorialAuthority.members.length }} membre{{ territorialAuthority.members.length === 1 ? '' : 's' }}
          </NuxtLink>
        </div>
        <div>
          <NuxtLink to="#">
            Plus d'informations
          </NuxtLink>
        </div>
      </template>
      <template #actions>
        <DUButton to="#">
          <VIcon small>
            {{ icons.mdiMessageAlertOutline }}
          </VIcon>
          Signaler un problème
        </DUButton>
        <DUButton
          primary
          to="#"
        >
          <VIcon small>
            {{ icons.mdiPlus }}
          </VIcon>
          Ajouter une procédure
        </DUButton>
      </template>
    </LayoutHeader>
    <LayoutSidemenu>
      <template #menu="{ defaultClass, activeClass }">
        <NuxtLink
          v-if="proceduresByDocumentType.PLUi?.length"
          :class="{
            [activeClass]: documentType === 'PLUi',
            [defaultClass]: true
          }"
          :to="{ query: { type_document: 'plui' } }"
        >
          PLUi
        </NuxtLink>
        <NuxtLink
          v-if="proceduresByDocumentType.PLU?.length"
          :class="{
            [activeClass]: documentType === 'PLU',
            [defaultClass]: true
          }"
          :to="{ query: {} }"
        >
          DU communaux
        </NuxtLink>
        <NuxtLink
          v-if="proceduresByDocumentType.SCoT?.length"
          :class="{
            [activeClass]: documentType === 'SCoT',
            [defaultClass]: true
          }"
          :to="{ query: { type_document: 'scot' } }"
        >
          SCoT
        </NuxtLink>
      </template>
      <template #default>
        <DUHeading>{{ proceduresLabel }}</DUHeading>
        <DUTable
          v-if="displayedProcedures.length"
          style="--du-table__cols:5fr 7fr 2fr 5fr 7fr 5fr 5fr 3rem"
        >
          <template #header>
            <DUTableCell>Statut</DUTableCell>
            <DUTableCell>Procédure</DUTableCell>
            <DUTableCell>N°</DUTableCell>
            <DUTableCell>Type de DU</DUTableCell>
            <DUTableCell>{{ documentType === 'PLU' ? 'Commune' : 'Collectivité porteuse' }}</DUTableCell>
            <DUTableCell>Prescrit le</DUTableCell>
            <DUTableCell>Approuvé le</DUTableCell>
            <DUTableCell />
          </template>
          <template #default>
            <template v-for="procedure in proceduresPage">
              <DUTableRow
                :key="procedure.id"
                primary
                :to="`/frise/${procedure.id}`"
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
                  <ProcedureDocumentType>{{ procedure.documentType }}</ProcedureDocumentType>
                </DUTableCell>
                <DUTableCell>{{ documentType === 'PLU' ? procedure.townName : procedure.territorialAuthorityName }}</DUTableCell>
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
                :to="`/frise/${procedure.id}`"
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
                <DUTableCell>
                  <ProcedureDocumentType>{{ secondaryProcedure.documentType }}</ProcedureDocumentType>
                </DUTableCell>
                <DUTableCell>{{ documentType === 'PLU' ? secondaryProcedure.townName : secondaryProcedure.territorialAuthorityName }}</DUTableCell>
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
        <DUPagination :size="pages" />
      </template>
    </LayoutSidemenu>
  </LayoutMain>
</template>
