<script>
import { mdiArrowRight, mdiOpenInNew } from '@mdi/js'
import { kebabCase } from 'lodash'
import { displayTerritorialAuthorityCode } from '~/plugins/territorial-authority'

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
  data () {
    return {
      department: null,
      icons: {
        mdiArrowRight,
        mdiOpenInNew
      }
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
            }
          ]
        : []
    },
    departmentCode () {
      return this.territorialAuthority?.departmentCode || null
    },
    displayedCode () {
      return displayTerritorialAuthorityCode(this.territorialAuthority)
    },
    intermunicipalityCode () {
      return this.territorialAuthority?.intermunicipalityCode || null
    },
    label () {
      return this.territorialAuthority?.name || ''
    },
    mandatoryJurisdiction () {
      // TODO :: Get this
      return null
    },
    membersActive: {
      get () {
        return this.$route.query.perimetre === this.territorialAuthorityCode
      },
      set (newValue) {
        this.$router.push({
          query: {
            ...this.$route.query,
            perimetre: newValue ? this.territorialAuthorityCode : undefined
          }
        })
      }
    },
    mountainArea () {
      // TODO :: Get this
      return false
    },
    optionalJurisdiction () {
      // TODO :: Get this
      return null
    },
    residentsCount () {
      // TODO :: Get this
      return 0
    },
    territorialAuthorityCode () {
      return this.$route.params.code_collectivite || null
    },
    toBanatic () {
      return this.territorialAuthority
        ? `https://www.banatic.interieur.gouv.fr/${
            this.intermunicipalityCode ? 'commune' : 'intercommunalite'
          }/${
            this.territorialAuthorityCode
          }-${
            kebabCase(this.territorialAuthority.name)
          }`
        : null
    }
  },
  watch: {
    departmentCode: {
      async handler (value) {
        if (!process.client) {
          return
        }

        this.department = value
          ? await this.$departmentApi.get(value)
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
    label="Plus d'informations"
  >
    <template #header>
      <em>{{ label }}</em>
    </template>
    <template #default>
      <DUGroup
        grid
        md
      >
        <DUCard lg>
          <DUHeading
            :level="3"
            strong
          >
            Informations générales
          </DUHeading>
          <DUGroup
            start
            xs
          >
            <DUText>{{ displayedCode }}</DUText>
            <DUText v-if="department">
              Département&nbsp;: {{ department.name }} ({{ department.code }})
            </DUText>
            <PageDepartementsCollectivitesTowns
              v-if="territorialAuthority.members.length"
              v-model="membersActive"
              :label="label"
              :towns="territorialAuthority.members"
            >
              Périmètre&nbsp;: {{ territorialAuthority.members.length }} membre{{ territorialAuthority.members.length === 1 ? '' : 's' }}
            </PageDepartementsCollectivitesTowns>
            <DUText v-if="residentsCount">
              Population&nbsp;: {{ residentsCount }} habitant{{ residentsCount === 1 ? '' : 's' }}
            </DUText>
          </DUGroup>
          <DUGroup
            v-if="mountainArea || mandatoryJurisdiction || optionalJurisdiction"
            start
            xs
          >
            <DUText v-if="mountainArea">
              Zone de montagne
            </DUText>
            <DUText v-if="mandatoryJurisdiction">
              Compétence obligatoire {{ mandatoryJurisdiction }}
            </DUText>
            <DUText v-if="optionalJurisdiction">
              Compétence facultative {{ optionalJurisdiction }}
            </DUText>
          </DUGroup>
          <DUGroup start>
            <DUButton
              primary
              :to="toBanatic"
            >
              Consulter la fiche complète de la collectivité sur Banatic
              <VIcon small>
                {{ icons.mdiOpenInNew }}
              </VIcon>
            </DUButton>
          </DUGroup>
        </DUCard>
        <DUGroup md>
          <DUCard lg>
            <DUGroup xs>
              <DUHeading
                :level="3"
                strong
              >
                Données ouvertes
              </DUHeading>
              <DUDottedList sm>
                <li>Base territoriale</li>
                <li>Géo-IDE</li>
                <li>Géorisques</li>
                <li>INPN</li>
                <li>Géoportail de l'urbanisme</li>
              </DUDottedList>
            </DUGroup>
            <DUGroup start>
              <DUButton
                secondary
                :to="{
                  name: 'collectivites-code_collectivite-donnees-data',
                  params: {
                    code_collectivite: territorialAuthorityCode
                  }
                }"
              >
                Consulter les données ouvertes sur la collectivité
                <VIcon small>
                  {{ icons.mdiArrowRight }}
                </VIcon>
              </DUButton>
            </DUGroup>
          </DUCard>
          <DUCard lg>
            <DUHeading
              :level="3"
              strong
            >
              Ressources
            </DUHeading>
            <DUGroup
              sm
              start
            >
              <DULink :to="`/collectivites/${territorialAuthorityCode}/pac`">
                Socle de porter-à-connaissance
              </DULink>
              <DULink :to="`/collectivites/${territorialAuthorityCode}/ressources`">
                Liens utiles
              </DULink>
              <DULink :to="`/collectivites/${territorialAuthorityCode}/glossaire`">
                Glossaire urbanise
              </DULink>
            </DUGroup>
          </DUCard>
        </DUGroup>
      </DUGroup>
    </template>
  </LayoutMain>
</template>
