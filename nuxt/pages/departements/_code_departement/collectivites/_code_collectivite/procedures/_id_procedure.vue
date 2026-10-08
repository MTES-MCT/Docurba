<script>
export default {
  data () {
    return {
      intermunicipality: null,
      territorialAuthority: null
    }
  },
  computed: {
    breadcrumb () {
      if (!this.departmentCode || !this.territorialAuthorityCode) {
        return []
      }

      const breadcrumb = []

      if (this.$user.canViewSectionCollectivites({ departement: this.departmentCode })) {
        breadcrumb.push({
          label: `Mes collectivités (${this.departmentCode})`,
          value: {
            name: 'departements-code_departement-collectivites',
            params: {
              code_departement: this.departmentCode
            }
          }
        })
      }
      if (this.intermunicipality) {
        breadcrumb.push({
          label: this.intermunicipality.name,
          value: {
            name: 'departements-code_departement-collectivites-code_collectivite',
            params: {
              code_collectivite: this.intermunicipalityCode,
              code_departement: this.departmentCode
            }
          }
        })
      }
      if (this.territorialAuthority) {
        breadcrumb.push({
          label: this.territorialAuthority.name,
          value: {
            name: 'departements-code_departement-collectivites-code_collectivite',
            params: {
              code_collectivite: this.territorialAuthorityCode,
              code_departement: this.departmentCode
            }
          }
        })
      }

      return breadcrumb
    },
    departmentCode () {
      return this.$route.params.code_departement?.padStart(2, '0') || null
    },
    intermunicipalityCode () {
      return this.territorialAuthority?.intermunicipalityCode || null
    },
    procedureId () {
      return this.$route.params.id_procedure || null
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
      },
      immediate: true
    }
  }
}
</script>

<template>
  <LayoutMain
    :breadcrumb="breadcrumb"
    label="Page procédure non implémentée"
  >
    <DUButton
      primary
      :to="`/frise/${procedureId}`"
    >
      Page alternative
    </DUButton>
  </LayoutMain>
</template>
