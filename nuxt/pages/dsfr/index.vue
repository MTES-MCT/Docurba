<script>
export default {
  data() {
    return {
      selectedDepartmentCode: '',
      selectedTerritorialAuthorityCode: '',
      territorialAuthorities: [],
    }
  },
  computed: {
    territorialAuthorityOptions() {
      if (!this.selectedDepartmentCode) {
        return [{
          disabled: true,
          label: 'Sélectionnez un département',
        }]
      }

      return this.territorialAuthorities.map(({ code, inseeCode, name }) => ({
        group: inseeCode ? 'Communes' : 'Groupements',
        label: name,
        value: code,
      }))
    },
  },
  watch: {
    selectedDepartmentCode: {
      async handler(value) {
        if (!value) return

        this.territorialAuthorities = await this.$store.dispatch(
          'territorialAuthority/list',
          { departmentCode: value },
        )
      },
      immediate: true,
    },
  },
}
</script>

<template>
  <FRContainer>
    <FRGrid gap="md lg-lg"
            size="md lg-lg">
      <FRText center
              h1
              tag="h1">
        Docurba vous accompagne dans l'élaboration de vos PLU
      </FRText>
      <FRContainer alt>
        <FRGrid gap="md lg-lg"
                size="md lg-lg">
          <FRText h6>
            Pour commencer, accédez aux ressources de votre territoire&nbsp;:
          </FRText>
          <div class="fr-row">
            <div class="fr-col fr-col-md-10">
              <div class="fr-row">
                <div class="fr-col fr-col-md-4">
                  <DUFieldDepartment id="search-department"
                                     v-model="selectedDepartmentCode" />
                </div>
                <div class="fr-col fr-col-md-8">
                  <FRFieldAutocomplete :groups-order="['Groupements', 'Communes']"
                                       id="search-territorial-authority"
                                       :options="territorialAuthorityOptions"
                                       placeholder="Commune ou Groupement"
                                       v-model="selectedTerritorialAuthorityCode" />
                </div>
              </div>
            </div>
            <div class="fr-col fr-col-md-2">
              <FRButton :disabled="!selectedTerritorialAuthorityCode"
                        :to="{
                          name: 'dsfr-collectivites-code_collectivite',
                          params: {
                            code_collectivite: selectedTerritorialAuthorityCode,
                          },
                        }">
                Accéder
              </FRButton>
            </div>
          </div>
        </FRGrid>
      </FRContainer>
    </FRGrid>
  </FRContainer>
</template>
