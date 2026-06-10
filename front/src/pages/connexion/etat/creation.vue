<script setup lang="ts">
import { computed, ref } from 'vue'
import FrButton from '@/components/FrButton.vue'
import FrButtons from '@/components/FrButtons.vue'
import FrCheckbox from '@/components/FrCheckbox.vue'
import FrContainer from '@/components/FrContainer.vue'
import FrField from '@/components/FrField.vue'
import FrFieldset from '@/components/FrFieldset.vue'
import { Administration } from '@/data/Administration'

// Definitions
definePage({
  meta: {
    signedOutOnly: true,
  },
})

// View
const administrationOptions = [{
  label: 'DDT(M)/DEAL',
  value: Administration.DdtDdtmDeal,
}, {
  label: 'DREAL',
  value: Administration.Dreal,
}]

const administration = ref('')
const administrationError = ref<boolean | string>(false)
const administrationSuccess = ref(false)
const email = ref('')
const emailError = ref<boolean | string>(false)
const emailSuccess = ref(false)
const firstname = ref('')
const firstnameError = ref<boolean | string>(false)
const firstnameSuccess = ref(false)
const lastname = ref('')
const lastnameError = ref<boolean | string>(false)
const lastnameSuccess = ref(false)
const newsletter = ref(false)
const password = ref('')
const passwordErrors = ref<{
  count: boolean
  number: boolean
  special: boolean
}>({
  count: false,
  number: false,
  special: false,
})
const passwordSuccess = ref(false)
const submitting = ref(false)

const administrationValidated = computed<boolean>(() =>
  !!administrationError.value || administrationSuccess.value
)
const emailValidated = computed<boolean>(() =>
  !!emailError.value || emailSuccess.value
)
const firstnameValidated = computed<boolean>(() =>
  !!firstnameError.value || firstnameSuccess.value
)
const lastnameValidated = computed<boolean>(() =>
  !!lastnameError.value || lastnameSuccess.value
)
const passwordError = computed<boolean>(() => !passwordSuccess.value && (
  passwordErrors.value.count
  || passwordErrors.value.number
  || passwordErrors.value.special
))
const passwordValidated = computed<boolean>(() =>
  !!passwordError.value || passwordSuccess.value
)

// Functions
async function submit() {
  submitting.value = true

  // TODO :: Implement this

  submitting.value = false
}

function validateAdministration() {
  if (administration.value) {
    administrationError.value = false
    administrationSuccess.value = true
  } else {
    administrationError.value = 'L\'administration est obligatoire.'
    administrationSuccess.value = false
  }
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

function validateFirstname() {
  if (firstname.value) {
    firstnameError.value = false
    firstnameSuccess.value = true
  } else {
    firstnameError.value = 'Le prénom est obligatoire.'
    firstnameSuccess.value = false
  }
}

function validateLastname() {
  if (lastname.value) {
    lastnameError.value = false
    lastnameSuccess.value = true
  } else {
    lastnameError.value = 'Le nom est obligatoire.'
    lastnameSuccess.value = false
  }
}

function validatePassword() {
  if (!password.value) {
    passwordErrors.value = {
      count: true,
      number: true,
      special: true,
    }

    return
  }

  passwordErrors.value = {
    count: password.value.length < 12,
    number: !/[0-9]/.test(password.value),
    special: /^[A-Za-z0-9]+$/.test(password.value),
  }
  passwordSuccess.value = (
    !passwordErrors.value.count
    && !passwordErrors.value.number
    && !passwordErrors.value.special
  )
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
          <h1 class="fr-text fr-text--h1">Inscription agent de l'État</h1>
          <FrFieldset>
            <FrField :error="emailError"
                     id="signup-email"
                     :success="emailSuccess"
                     type="email"
                     v-model:value="email"
                     @blur="validateEmail()"
                     @update:value="emailValidated && validateEmail()">
              <template #label>Identifant</template>
              <template #hint>Format attendu : nom@domaine.fr</template>
            </FrField>
            <FrField :error="passwordError"
                     id="signup-password"
                     :success="passwordSuccess"
                     type="password"
                     v-model:value="password"
                     @blur="validatePassword()"
                     @update:value="passwordValidated && validatePassword()">
              <template #label>Mot de passe</template>
              <template #message>
                <span>Votre mot de passe doit contenir :</span><br />
                <span class="fr-icon--before fr-icon--inline fr-icon--inline-xs"
                      :class="
                        passwordErrors.count
                          ? 'fr-text--error fr-icon--before-close-line'
                          : passwordValidated
                            ? 'fr-text--success fr-icon--before-check-line'
                            : 'fr-text--info fr-icon--before-info-fill'
                      ">12 caractères minimum</span><br />
                <span class="fr-icon--before fr-icon--inline fr-icon--inline-xs"
                      :class="
                        passwordErrors.special
                          ? 'fr-text--error fr-icon--before-close-line'
                          : passwordValidated
                            ? 'fr-text--success fr-icon--before-check-line'
                            : 'fr-text--info fr-icon--before-info-fill'
                      ">1 caractère spécial minimum</span><br />
                <span class="fr-icon--before fr-icon--inline fr-icon--inline-xs"
                      :class="
                        passwordErrors.number
                          ? 'fr-text--error fr-icon--before-close-line'
                          : passwordValidated
                            ? 'fr-text--success fr-icon--before-check-line'
                            : 'fr-text--info fr-icon--before-info-fill'
                      ">1 chiffre minimum</span>
              </template>
            </FrField>
            <div class="fr-row">
              <div class="fr-col--start fr-col-12 fr-col-md-6">
                <FrField :error="firstnameError"
                         id="signup-firstname"
                         :success="firstnameSuccess"
                         v-model:value="firstname"
                         @blur="validateFirstname()"
                         @update:value="firstnameValidated && validateFirstname()">
                  <template #label>Prénom</template>
                </FrField>
              </div>
              <div class="fr-col--start fr-col-12 fr-col-md-6">
                <FrField :error="lastnameError"
                         id="signup-lastname"
                         :success="lastnameSuccess"
                         v-model:value="lastname"
                         @blur="validateLastname()"
                         @update:value="lastnameValidated && validateLastname()">
                  <template #label>Nom</template>
                </FrField>
              </div>
            </div>
            <FrField :error="administrationError"
                     id="signup-administration"
                     :options="administrationOptions"
                     :success="administrationSuccess"
                     type="select"
                     v-model:value="administration"
                     @blur="validateAdministration()"
                     @update:value="administrationValidated && validateAdministration()">
              <template #label>Administration</template>
            </FrField>
            <FrCheckbox id="signup-newsletter"
                        v-model:value="newsletter">Cochez cette case afin de recevoir nos lettres d'informations mensuelles pour ne rien louper aux dernières actualités de Docurba.
Promis, seul un contenu court et pertinent vous sera envoyé une fois par mois 🌎</FrCheckbox>
          </FrFieldset>
          <FrButtons end>
            <FrButton :disabled="submitting"
                      secondary
                      to="/connexion/etat">J'ai déjà un compte</FrButton>
            <FrButton :disabled="
                        !!administrationError
                        || !!emailError
                        || !!firstnameError
                        || !!lastnameError
                        || !!passwordError
                        || submitting
                      "
                      @actuated="submit()">Créer mon compte</FrButton>
          </FrButtons>
        </FrContainer>
      </div>
    </div>
  </FrContainer>
</template>
