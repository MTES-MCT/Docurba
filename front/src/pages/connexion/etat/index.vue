<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import FrButton from '@/components/FrButton.vue'
import FrContainer from '@/components/FrContainer.vue'
import FrField from '@/components/FrField.vue'
import FrFieldset from '@/components/FrFieldset.vue'
import FrLink from '@/components/FrLink.vue'
import FrSeparator from '@/components/FrSeparator.vue'
import { useAuth } from '@/composables/useAuth'

// Definitions
definePage({
  meta: {
    signedOutOnly: true,
  },
})

// Route
const router = useRouter()

// Data
const { signedIn, signIn } = useAuth()

// View
const email = ref('')
const emailError = ref<boolean | string>(false)
const emailSuccess = ref<boolean>(false)
const password = ref('')
const passwordError = ref<boolean | string>(false)
const passwordSuccess = ref(false)
const submitting = ref(false)

const emailValidated = computed<boolean>(() =>
  !!emailError.value || emailSuccess.value
)
const passwordValidated = computed<boolean>(() =>
  !!passwordError.value || passwordSuccess.value
)

// Functions
async function submit() {
  submitting.value = true

  await signIn(email.value, password.value)

  submitting.value = false

  if (!signedIn.value) return

  router.replace('/tableau-de-bord')
}

function validateEmail() {
  if (!email.value) {
    emailError.value = 'L\'identifiant est obligatoire.'
    emailSuccess.value = false

    return
  }
  if (!/^.*?[a-z0-9]+.*?@.*?[a-z0-9]+.*?\..*?[a-z0-9]+.*?$/.test(email.value)) {
    emailError.value = 'Veuillez entrer un email valide.'
    emailSuccess.value = false

    return
  }

  emailError.value = false
  emailSuccess.value = true
}

function validatePassword() {
  if (password.value) {
    passwordError.value = false
    passwordSuccess.value = true
  } else {
    passwordError.value = 'Le mot de passe est obligatoire.'
    passwordSuccess.value = false
  }
}
</script>

<template>
  <FrContainer fluid
               id="content"
               role="main"
               tag="main"
               vertical>
    <div class="fr-row fr-row--center">
      <div class="fr-col-12 fr-col-md-8 fr-col-lg-6">
        <FrContainer class="fr-bg--grey"
                     vertical>
          <h1 class="fr-text fr-text--h1">Connexion agent de l'État</h1>
          <h2 class="fr-text fr-text--h2">Se connecter avec son compte</h2>
          <FrFieldset>
            <FrField :error="emailError"
                     id="login-email"
                     :success="emailSuccess"
                     type="email"
                     v-model:value="email"
                     @blur="validateEmail()"
                     @update:value="emailValidated && validateEmail()">
              <template #label>Identifant</template>
              <template #hint>Format attendu : nom@domaine.fr</template>
            </FrField>
            <FrField :error="passwordError"
                     id="login-password"
                     :success="passwordSuccess"
                     type="password"
                     v-model:value="password"
                     @blur="validatePassword()"
                     @update:value="passwordValidated && validatePassword()">
              <template #label>Mot de passe</template>
            </FrField>
            <p class="fr-text">
              <FrLink to="/connexion/mot-de-passe-oublie">Mot de passe oublié ?</FrLink>
            </p>
          </FrFieldset>
          <FrButton :disabled="!!emailError || !!passwordError || submitting"
                    @actuated="submit()">Se connecter</FrButton>
          <FrSeparator />
          <h2 class="fr-text fr-text--h2">Vous n'avez pas de compte ?</h2>
          <FrButton :disabled="submitting"
                    secondary
                    to="/connexion/etat/creation">Créer un compte</FrButton>
        </FrContainer>
      </div>
    </div>
  </FrContainer>
</template>
