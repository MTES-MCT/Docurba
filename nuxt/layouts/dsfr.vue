<script>
import {
  mdiAccountCircle,
  mdiChevronDown,
  mdiDomain,
  mdiHelpCircleOutline,
  mdiOpenInNew,
  mdiPoll,
} from '@mdi/js'
import { UserScope } from '~/store/auth'

export default {
  data() {
    return {
      icons: {
        mdiAccountCircle,
        mdiChevronDown,
        mdiDomain,
        mdiHelpCircleOutline,
        mdiOpenInNew,
        mdiPoll,
      },
      initialized: false,
    }
  },
  computed: {
    alerts() {
      return this.$store.getters['alert/messages']
    },
    elementStyle() {
      return this.menu.length
        ? {
          '--fr-header-xs__size': '9.78125rem',
          '--fr-header-lg__size': '10.78125rem',
        }
        : {
          '--fr-header-xs__size': '6.28125rem',
          '--fr-header-lg__size': '7.28125rem',
        }
    },
    mainAction() {
      if (!this.signedIn) {
        return {}
      }
      if (
        [UserScope.State, UserScope.Department].includes(this.user.scope)
        && this.user.departmentCode
      ) {
        return {
          label: 'Mes collectivités',
          to: {
            name: 'dsfr-departements-code_departement-collectivites',
            params: {
              code_departement: this.user.departmentCode,
            },
          },
        }
      }
      if (this.user.scope === UserScope.Region && this.user.regionCode) {
        return {
          label: 'Trame régionale',
          to: {
            name: 'dsfr-regions-code_region-trame',
            params: {
              code_region: this.user.regionCode,
            },
          },
        }
      }
      if (this.user.territorialAuthorityCode) {
        return {
          label: 'Ma collectivité',
          to: {
            name: 'dsfr-collectivites-code_collectivite',
            params: {
              code_collectivite: this.user.territorialAuthorityCode,
            },
          },
        }
      }

      return {}
    },
    menu() {
      return (
        this.$route.name !== 'dsfr'
        && this.signedIn
        && [UserScope.State, UserScope.Department].includes(this.user.scope)
        && this.user.departmentCode
      )
        ? [{
          active: this.$route.name === 'dsfr-departements-code_departement-collectivites',
          label: 'Mes collectivités',
          to: {
            name: 'dsfr-departements-code_departement-collectivites',
            params: {
              code_departement: this.user.departmentCode,
            },
          },
        }, {
          active: this.$route.name === 'dsfr-departements-code_departement-procedures',
          label: 'Mes procédures',
          to: {
            name: 'dsfr-departements-code_departement-procedures',
            params: {
              code_departement: this.user.departmentCode,
            },
          },
        }, {
          active: this.$route.name === 'dsfr-departements-code_departement-trame',
          label: 'Trame départementale',
          to: {
            name: 'dsfr-departements-code_departement-trame',
            params: {
              code_departement: this.user.departmentCode,
            },
          },
        }, {
          active: this.$route.name === 'dsfr-departements-code_departement-pacs',
          label: 'Mes PACs',
          to: {
            name: 'dsfr-departements-code_departement-pacs',
            params: {
              code_departement: this.user.departmentCode,
            },
          },
        }]
        : []
    },
    signedIn() {
      return this.$store.getters['auth/signedIn']
    },
    user() {
      return this.$store.getters['auth/user']
    }
  },
  async created() {
    await this.$store.dispatch('auth/init')
    this.initialized = true
  },
  methods: {
    dismissAlert(id) {
      this.$store.dispatch('alert/dismiss', id)
    },
    pauseAlert(id) {
      this.$store.dispatch('alert/pause', id)
    },
    restartAlert(id) {
      this.$store.dispatch('alert/restart', id)
    },
    openThemeSelector() {
      // TODO :: Implement this
    },
    async signOut() {
      try {
        await this.$store.dispatch('auth/signOut')

        if (this.$route.name !== 'dsfr') {
          this.$router.push({ name: 'dsfr' })
        }
      } catch (error) {
        this.$store.dispatch('alert/sendError', error.message)
      }
    },
  },
}
</script>

<template>
  <FRLayout v-if="initialized"
            :style="elementStyle"
            :theme="$route.query.theme">
    <FRHeader>
      <template #brand>
        République<br>
        Française
      </template>
      <template #heading>
        Docurba
      </template>
      <template #links>
        <FRDropdownMenu v-if="!signedIn"
                        :items="[{
                          label: 'Docurba pour:'
                        }, {
                          label: 'Les collectivités',
                          to: '/solutions/collectivites'
                        }, {
                          label: 'Les bureaux d\'étude',
                          to: '/solutions/bureaux-d-etude'
                        }, {
                          label: 'Les services de l\'État',
                          to: '/solutions/services-de-l-etat'
                        }]">
          <FRButton sm
                    tertiary-borderless>
            Solutions
            <FRIcon :value="icons.mdiChevronDown" />
          </FRButton>
        </FRDropdownMenu>
        <FRDropdownMenu :items="[{
                          label: 'Guide d\'utilisation',
                          to: '/docs/guide-d-utilisation'
                        }, {
                          label: 'FAQ',
                          to: '/docs/faq'
                        }, {
                          label: 'Webinaires',
                          to: '/docs/webinaires'
                        }, {
                          label: 'Contact',
                          to: '/docs/contact'
                        }, {
                          label: 'API',
                          to: '/docs/api'
                        }]">
          <FRButton sm
                    tertiary-borderless>
            Documentation
            <FRIcon :value="icons.mdiChevronDown" />
          </FRButton>
        </FRDropdownMenu>
        <template v-if="signedIn">
          <FRButton v-if="mainAction.to"
                    :to="mainAction.to">
            {{ mainAction.label }}
          </FRButton>
          <FRDropdownMenu end
                          :items="[{
                            action: signOut,
                            label: 'Se déconnecter'
                          }]">
            <FRButton secondary>
              <FRIcon :value="icons.mdiAccountCircle" />
              {{ user.firstname }}
              <FRIcon :value="icons.mdiChevronDown" />
            </FRButton>
          </FRDropdownMenu>
        </template>
        <FRButton v-else
                  secondary
                  :to="{ name: 'dsfr-connexion' }">
          <FRIcon :value="icons.mdiAccountCircle" />
          Se connecter
        </FRButton>
      </template>
      <template v-if="menu.length"
                #default>
        <FRMenu :value="menu" />
      </template>
    </FRHeader>
    <FRAlerts :value="alerts"
              @dismissed="dismissAlert($event)"
              @paused="pauseAlert($event)"
              @restarted="restartAlert($event)" />
    <Nuxt />
    <FRFooter>
      <template #banner>
        <FRActionable :to="{ name: 'dsfr-docs-api' }">
          <FRIcon :value="icons.mdiDomain" />
          Mise à disposition des données (API)
        </FRActionable>
        <FRActionable :to="{ name: 'dsfr-stats' }">
          <FRIcon :value="icons.mdiPoll" />
          Statistiques
        </FRActionable>
        <FRActionable :to="{ name: 'dsfr-docs' }">
          <FRIcon :value="icons.mdiHelpCircleOutline" />
          Aide à l'utilisation de Docurba
        </FRActionable>
      </template>
      <template #brand>
        Ministères<br>
        Transition écologique<br>
        Aménagement du territoire<br>
        Transports<br>
        Ville et logement
      </template>
      <template #description>
        <FRText sm>
          Docurba centralise les ressources à chaque étape de vos procédures d'urbanisme pour plus de rapidité, une meilleure conformité et une visibilité en temps réel.
        </FRText>
        <FRText sm>
          Le
          <FRLink to="https://github.com/MTES-MCT/Docurba">
            code source
          </FRLink>
          est ouvert et les contributions bienvenues.
        </FRText>
      </template>
      <template #links>
        <li>
          <FRActionable :to="{ name: 'dsfr-accessibilite' }">
            Accessibilité&nbsp;: non conforme
          </FRActionable>
        </li>
        <li>
          <FRActionable :to="{ name: 'dsfr-mentions-legales' }">
            Mentions légales
          </FRActionable>
        </li>
        <li>
          <FRActionable :to="{ name: 'dsfr-donnees-personnelles' }">
            Données personnelles
          </FRActionable>
        </li>
        <li>
          <FRActionable :to="{ name: 'dsfr-cookies' }">
            Gestion des cookies
          </FRActionable>
        </li>
        <li>
          <FRActionable :to="{ name: 'dsfr-plan-du-site' }">
            Plan du site
          </FRActionable>
        </li>
        <li>
          <FRActionable @actuated="openThemeSelector()">
            Paramètres d'affichage
          </FRActionable>
        </li>
      </template>
      <template #mention>
        Sauf mention explicite de propriété intellectuelle détenue par des tiers, les contenus de ce site sont proposés sous
        <FRLink :to="{ name: 'dsfr-licence' }">
          licence etalab-2.0
          <FRIcon :value="icons.mdiOpenInNew" />
        </FRLink>
      </template>
    </FRFooter>
  </FRLayout>
</template>
