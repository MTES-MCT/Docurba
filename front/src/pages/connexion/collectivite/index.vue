<script setup lang="ts">
import { computed, ref } from 'vue'
import FrButton from '@/components/FrButton.vue'
import FrContainer from '@/components/FrContainer.vue'
import FrField from '@/components/FrField.vue'
import FrFieldset from '@/components/FrFieldset.vue'
import FrSeparator from '@/components/FrSeparator.vue'

// Definitions
definePage({
  meta: {
    signedOutOnly: true,
  },
})

// View
const email = ref('')
const emailError = ref<boolean | string>(false)
const emailSuccess = ref(false)
const submitting = ref(false)

const emailValidated = computed<boolean>(() =>
  !!emailError.value || emailSuccess.value
)

// Functions
async function submit() {
  submitting.value = true

  // TODO :: Implement this

  submitting.value = false
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
          <h1 class="fr-text fr-text--h1">Connexion Collectivité</h1>
          <h2 class="fr-text fr-text--h2">Recevoir un lien de connexion</h2>
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
          </FrFieldset>
          <FrButton :disabled="!!emailError || submitting"
                    @actuated="submit()">Envoyer le lien</FrButton>
          <FrSeparator />
          <h2 class="fr-text fr-text--h2">Vous n'avez pas de compte ?</h2>
          <FrButton :disabled="submitting"
                    secondary
                    to="/connexion/collectivite/creation">Créer un compte</FrButton>
        </FrContainer>
      </div>
    </div>
  </FrContainer>
</template>
