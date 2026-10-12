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
      if (!this.departmentCode) {
        return []
      }

      const breadcrumb = []

      if (this.$user.canViewSectionCollectivites({ departement: this.departmentCode })) {
        breadcrumb.push({
          label: `Mes collectivités (${this.departmentCode})`,
          value: `/ddt/${this.departmentCode}/collectivites`
        })
      }
      if (this.intermunicipality) {
        breadcrumb.push({
          label: this.intermunicipality.name,
          value: {
            name: 'collectivites-code_collectivite',
            params: {
              code_collectivite: this.intermunicipalityCode
            },
            query: {
              vue: this.$route.query.vue
            }
          }
        })
      }

      return breadcrumb
    },
    departmentCode () {
      return this.territorialAuthority?.departmentCode || null
    },
    intermunicipalityCode () {
      return this.territorialAuthority?.intermunicipalityCode || null
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
  <NuxtChild
    v-if="territorialAuthority"
    :intermunicipality="intermunicipality"
    :breadcrumb-root="breadcrumb"
    :territorial-authority="territorialAuthority"
  />
</template>
