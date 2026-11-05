<script>
import { mdiOpenInNew } from '@mdi/js'

export default {
  data() {
    return {
      email: '',
      icons: {
        mdiOpenInNew,
      },
      password: '',
      shouldRemember: false,
      signInError: null,
      signInLoading: false,
    }
  },
  computed: {
    breadcrumb() {
      return [{
        label: 'Accueil',
        to: {
          name: 'dsfr',
        },
      }]
    },
    signedIn() {
      return this.$store.getters['auth/signedIn']
    },
  },
  watch: {
    signedIn: {
      handler(value) {
        if (value) {
          this.$router.push({ name: 'dsfr' })
        }
      },
      immediate: true,
    },
  },
  methods: {
    async signIn() {
      this.signInError = null
      this.signInLoading = true

      try {
        await this.$store.dispatch('auth/signIn', {
          email: this.email,
          password: this.password,
        })
      } catch (error) {
        this.signInError = (() => {
          switch (error.message) {
            case 'Invalid login credentials':
              return 'Identifiant ou mot de passe invalide'
            case 'missing email or phone':
              return 'Identifiant manquant'
            default:
              return error.message
          }
        })()
      }

      this.signInLoading = false
    },
  },
}
</script>

<template>
  <FRContainer>
    <FRGrid gap="md lg-lg"
            size="md lg-lg">
      <FRBreadcrumb :value="breadcrumb">
        Connexion
      </FRBreadcrumb>
      <FRGrid size="md lg-xxl">
        <FRContainer alt
                     sm>
          <FRGrid gap="md lg-lg"
                  size="md lg-xxl">
            <FRText h3
                    tag="h1">
              Connexion à Docurba
            </FRText>
            <FRText h4
                    tag="h2">
              Se connecter avec ProConnect
            </FRText>
            <FRText sm>
              ProConnect est la solution proposée par l'État pour sécuriser et simplifier la connexion aux services en ligne.
            </FRText>
            <FRGrid gap="md lg-lg"
                    start>
              <FRButton :disabled="signInLoading">
                S'identifier avec<br />
                ProConnect
              </FRButton>
              <FRLink to="https://www.proconnect.gouv.fr/">
                Qu'est-ce que ProConnect&nbsp;?
                <FRIcon :value="icons.mdiOpenInNew" />
              </FRLink>
            </FRGrid>
            <FRSeparator>
              Ou
            </FRSeparator>
            <FRText h4
                    tag="h2">
              Se connecter avec son compte
            </FRText>
            <FRAlert v-if="signInError"
                     error>
              {{ signInError }}
            </FRAlert>
            <FRForm @submitted="signIn()">
              <FRField :error="!!signInError"
                       id="signin-email"
                       v-model="email">
                <template #label>
                  Identifiant
                </template>
                <template #hint>
                  Format attendu&nbsp;: nom@domaine.fr
                </template>
              </FRField>
              <FRField :error="!!signInError"
                       id="signin-password"
                       type="password"
                       v-model="password">
                <template #label>
                  Mot de passe
                </template>
                <template #description>
                  <FRLink :to="{ name: 'dsfr-mot-de-passe-oublie' }">
                    Mot de passe oublié&nbsp;?
                  </FRLink>
                </template>
              </FRField>
              <FRField id="signin-should-remember"
                       type="checkbox"
                       v-model="shouldRemember">
                <template #label>
                  Se souvenir de moi
                </template>
              </FRField>
              <FRButton :disabled="signInLoading"
                        @actuated="signIn()">
                Se connecter
              </FRButton>
            </FRForm>
            <FRSeparator />
            <FRText h4
                    tag="h2">
              Vous n'avez pas de compte&nbsp;?
            </FRText>
            <FRButton secondary
                      :to="{ name: 'dsfr-compte-creation' }">
              Créer un compte
            </FRButton>
          </FRGrid>
        </FRContainer>
      </FRGrid>
    </FRGrid>
  </FRContainer>
</template>
