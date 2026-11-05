<script>
import { mdiArrowRight, mdiOpenInNew } from '@mdi/js'
import { kebabCase } from 'lodash'
import {
  displayTerritorialAuthorityCode,
  isMunicipalityInseeCode,
} from '~/store/territorialAuthority'

export default {
  props: {
    breadcrumbRoot: {
      default: () => [],
      type: Array,
    },
    territorialAuthority: {
      default: null,
      type: Object,
    },
  },
  data() {
    return {
      department: null,
      icons: {
        mdiArrowRight,
        mdiOpenInNew,
      },
    }
  },
  computed: {
    breadcrumb() {
      return [...this.breadcrumbRoot, {
        label: this.territorialAuthority.name,
        to: {
          name: 'dsfr-collectivites-code_collectivite',
          params: {
            code_collectivite: this.territorialAuthority.code,
          },
        },
      }]
    },
    departmentCode() {
      return this.territorialAuthority.departmentCode
    },
    displayedCode() {
      return displayTerritorialAuthorityCode(this.territorialAuthority)
    },
    toBanatic() {
      return `https://www.banatic.interieur.gouv.fr/${
        isMunicipalityInseeCode(this.territorialAuthority.code)
          ? 'commune'
          : 'intercommunalite'
      }/${
        this.territorialAuthority.code
      }-${
        kebabCase(this.territorialAuthority.name)
      }`
    },
  },
  watch: {
    departmentCode: {
      async handler(value) {
        this.department = value
          ? await this.$store.dispatch('department/get', value)
          : null
      },
      immediate: true,
    },
  },
}
</script>

<template>
  <FRGrid alt>
    <FRHighlight alt>
      <FRContainer>
        <FRGrid gap="md lg-lg"
                size="md lg-xl">
          <FRGrid gap="md">
            <FRBreadcrumb :value="breadcrumb">
              Plus d'informations
            </FRBreadcrumb>
            <FRGrid gap="xs">
              <FRText h1
                      tag="h1">
                Plus d'informations
              </FRText>
              <FRText h5
                      light>
                <em>
                  {{ territorialAuthority.name }}
                </em>
              </FRText>
            </FRGrid>
          </FRGrid>
        </FRGrid>
      </FRContainer>
    </FRHighlight>
    <FRContainer>
      <FRGrid size="md lg-lg">
        <div class="fr-row">
          <div class="fr-col fr-col-md-6">
            <FRCard>
              <FRGrid gap="md lg-lg"
                      start>
                <FRText h6
                        tag="h2">
                  Informations générales
                </FRText>
                <FRGrid gap="xs">
                  <FRText>
                    {{ displayedCode }}
                  </FRText>
                  <FRText v-if="department">
                    Département&nbsp;: {{ department.name }} ({{ department.code }})
                  </FRText>
                </FRGrid>
                <FRButton :to="toBanatic">
                  Consulter la fiche complète de la collectivité sur Banatic
                  <FRIcon :value="icons.mdiOpenInNew" />
                </FRButton>
              </FRGrid>
            </FRCard>
          </div>
          <div class="fr-col fr-col-md-6">
            <FRGrid gap="md lg-lg">
              <FRCard>
                <FRGrid gap="md lg-lg"
                        start>
                  <FRGrid gap="xs">
                    <FRText h6
                            tag="h2">
                      Données ouvertes
                    </FRText>
                    <FRDottedList sm>
                      <li>
                        Base territoriale
                      </li>
                      <li>
                        Géo-IDE
                      </li>
                      <li>
                        Géorisques
                      </li>
                      <li>
                        INPN
                      </li>
                      <li>
                        Géoportail de l'urbanisme
                      </li>
                    </FRDottedList>
                  </FRGrid>
                  <FRButton secondary
                            :to="{
                              name: 'dsfr-collectivites-code_collectivite-donnees',
                              params: {
                                code_collectivite: territorialAuthority.code,
                              },
                            }">
                    Consulter les données ouvertes sur la collectivité
                    <FRIcon :value="icons.mdiArrowRight" />
                  </FRButton>
                </FRGrid>
              </FRCard>
              <FRCard>
                <FRGrid gap="md lg-lg">
                  <FRText h6
                          tag="h2">
                    Ressources
                  </FRText>
                  <FRGrid gap="xs"
                          start>
                    <FRLink :to="{
                              name: 'dsfr-collectivites-code_collectivite-pac',
                              params: {
                                code_collectivite: territorialAuthority.code,
                              },
                            }">
                      Socle de porter-à-connaissance
                    </FRLink>
                    <FRLink :to="{
                              name: 'dsfr-collectivites-code_collectivite-ressources',
                              params: {
                                code_collectivite: territorialAuthority.code,
                              },
                            }">
                      Liens utiles
                    </FRLink>
                    <FRLink :to="{
                              name: 'dsfr-collectivites-code_collectivite-glossaire',
                              params: {
                                code_collectivite: territorialAuthority.code,
                              },
                            }">
                      Glossaire urbanisme
                    </FRLink>
                  </FRGrid>
                </FRGrid>
              </FRCard>
            </FRGrid>
          </div>
        </div>
      </FRGrid>
    </FRContainer>
  </FRGrid>
</template>
