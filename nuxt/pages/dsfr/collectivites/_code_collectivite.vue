<script>
export default {
  data() {
    return {
      intermunicipality: null,
      territorialAuthority: null,
    }
  },
  computed: {
    breadcrumb() {
      if (!this.departmentCode) {
        return []
      }

      const breadcrumb = []

      if (this.$store.getters['auth/accessDepartmentTerritorialAuthorities'](
        this.departmentCode,
      )) {
        breadcrumb.push({
          label: `Mes collectivités (${this.departmentCode})`,
          to: {
            name: 'dsfr-departements-code_departement-collectivites',
            params: {
              code_departement: this.departmentCode,
            },
          },
        })
      }
      if (this.intermunicipality) {
        breadcrumb.push({
          label: this.intermunicipality.name,
          to: {
            name: 'dsfr-collectivites-code_collectivite',
            params: {
              code_collectivite: this.intermunicipalityCode,
            },
            query: {
              vue: this.$route.query.vue,
            },
          },
        })
      }

      return breadcrumb
    },
    departmentCode() {
      return this.territorialAuthority && this.territorialAuthority.departmentCode
    },
    intermunicipalityCode() {
      return this.territorialAuthority && this.territorialAuthority.intermunicipalityCode
    },
    territorialAuthorityCode() {
      return this.$route.params.code_collectivite || null
    },
  },
  watch: {
    intermunicipalityCode: {
      async handler(value) {
        if (!value) return

        this.intermunicipality = await this.$store.dispatch('territorialAuthority/get', {
          code: value,
          includeMembers: true,
        })
      },
      immediate: true,
    },
    territorialAuthorityCode: {
      async handler(value) {
        if (!value) return

        this.territorialAuthority = await this.$store.dispatch('territorialAuthority/get', {
          code: value,
          includeMembers: true,
        })
      },
      immediate: true,
    },
  },
}
</script>

<template>
  <NuxtChild v-if="territorialAuthority"
             :breadcrumb-root="breadcrumb"
             :territorial-authority="territorialAuthority" />
  <div v-else />
</template>
