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
  <FRGrid alt
          gap="md"
          size="md lg-xl">
    <FRContainer>
      <FRBreadcrumb :value="breadcrumb">
        Connexion
      </FRBreadcrumb>
    </FRContainer>
    <FRContainer sm>
      <FRGrid gap="md lg-xl">
        <FRText h1
                tag="h1">
          Connexion
        </FRText>
        <FRCard borderless
                lg>
          <FRGrid gap="md lg-lg">
            <FRText h5
                    tag="h2">
              Me connecter avec ProConnect
            </FRText>
            <FRText sm>
              ProConnect est la solution proposée par l'État pour sécuriser et simplifier la connexion aux services en ligne.
            </FRText>
            <FRGrid gap="md lg-lg"
                    x-start>
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
            <FRText h5
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
                Adresse email professionnelle
              </FRField>
              <FRField :error="!!signInError"
                        id="signin-password"
                        type="password"
                        v-model="password">
                <template #default>
                  Mot de passe
                </template>
                <template #description>
                  <FRLink sm
                          :to="{ name: 'dsfr-mot-de-passe-oublie' }">
                    Je n'ai pas encore de mot de passe ou je l'ai oublié
                  </FRLink>
                </template>
              </FRField>
              <FRField id="signin-should-remember"
                       sm
                       type="checkbox"
                       v-model="shouldRemember">
                Se souvenir de moi
              </FRField>
              <FRButton :disabled="signInLoading"
                        secondary
                        @actuated="signIn()">
                Se connecter
              </FRButton>
            </FRForm>
            <FRSeparator />
            <FRText h5
                    tag="h2">
              Vous n'avez pas de compte&nbsp;?
            </FRText>
            <FRButton tertiary
                      :to="{ name: 'dsfr-compte-creation' }">
              Créer mon compte Docurba
            </FRButton>
          </FRGrid>
        </FRCard>
      </FRGrid>
    </FRContainer>
  </FRGrid>
</template>
