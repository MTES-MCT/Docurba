<script>
export default {
  props: {
    breadcrumbRoot: {
      default: () => [],
      type: Array
    },
    intermunicipality: {
      default: null,
      type: Object
    },
    territorialAuthority: {
      default: null,
      type: Object
    }
  },
  computed: {
    breadcrumb () {
      return this.territorialAuthority
        ? [
            ...this.breadcrumbRoot,
            {
              label: this.territorialAuthority.name,
              value: {
                name: 'collectivites-code_collectivite',
                params: {
                  code_collectivite: this.territorialAuthorityCode
                }
              }
            },
            {
              label: 'Plus d\'informations',
              value: {
                name: 'collectivites-code_collectivite-informations',
                params: {
                  code_collectivite: this.territorialAuthorityCode
                }
              }
            }
          ]
        : []
    },
    departmentCode () {
      return this.territorialAuthority?.departmentCode || null
    },
    intermunicipalityCode () {
      return this.territorialAuthority?.intermunicipalityCode || null
    },
    label () {
      return this.territorialAuthority?.name || ''
    },
    tabs () {
      return [
        ['data', 'Base territoriale'],
        ['geoide', 'Géo-IDE'],
        ['georisques', 'Géorisques'],
        ['inpn', 'INPN'],
        ['gpu', 'GPU']
      ].map(([id, label]) => ({
        id,
        label,
        to: {
          name: `collectivites-code_collectivite-donnees-${id}`,
          params: {
            code_collectivite: this.territorialAuthorityCode
          }
        }
      }))
    },
    territorialAuthorityCode () {
      return this.$route.params.code_collectivite || null
    },
    towns () {
      return this.territorialAuthority.intermunicipalityCode
        ? [this.territorialAuthority]
        : this.territorialAuthority.members.filter(member =>
          member.type.startsWith('COM')
        )
    },
    townCodes () {
      return this.towns.map(({ code }) => code)
    }
  },
  created () {
    if (!this.$route.path.endsWith('/donnees')) {
      return
    }

    this.$router.replace({
      name: 'collectivites-code_collectivite-donnees-data',
      params: {
        code_collectivite: this.territorialAuthorityCode
      }
    })
  }
}
</script>

<template>
  <LayoutMain
    :breadcrumb="breadcrumb"
    label="Données ouvertes"
  >
    <template #header>
      <em>{{ label }}</em>
    </template>
    <template #default>
      <DUCard lg>
        <VTabs>
          <VTab
            v-for="tab in tabs"
            :key="tab.id"
            nuxt
            :to="tab.to"
          >
            {{ tab.label }}
          </VTab>
        </VTabs>
        <NuxtChild
          :territorial-authority="territorialAuthority"
          :towns="towns"
        />
      </DUCard>
    </template>
  </LayoutMain>
</template>
