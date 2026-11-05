<script>
import { accessDepartments, accessTerritorialAuthorities } from '~/store/auth'

export default {
  data() {
    return {
      intermunicipality: null,
      territorialAuthority: null,
    }
  },
  computed: {
    accessDepartments() {
      return accessDepartments(this.$store.getters['auth/user'])
    },
    accessTerritorialAuthorities() {
      return accessTerritorialAuthorities(this.$store.getters['auth/user'], {
        departmentCode: this.departmentCode
      })
    },
    breadcrumb() {
      if (!this.departmentCode) {
        return []
      }

      const breadcrumb = []

      if (this.accessTerritorialAuthorities) {
        breadcrumb.push({
          label: 'Mes collectivités',
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
