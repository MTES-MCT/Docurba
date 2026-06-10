<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import FrButton from '@/components/FrButton.vue'
import FrButtons from '@/components/FrButtons.vue'
import FrCheckbox from '@/components/FrCheckbox.vue'
import FrContainer from '@/components/FrContainer.vue'
import FrField from '@/components/FrField.vue'
import FrFieldset from '@/components/FrFieldset.vue'
import { useCollectivites } from '@/composables/useCollectivites'
import { useDepartements } from '@/composables/useDepartements'
import type { CollectiviteLabel } from '@/data/Collectivite'
import { EPCI_TYPES } from '@/data/Collectivite'
import type { Option, OptionGroup, Options } from '@/data/Option'
import { Poste } from '@/data/Poste'

// Definitions
definePage({
  meta: {
    signedOutOnly: true,
  },
})

// Data
const departementId = ref('')

const { collectivites } = useCollectivites({ departementId })
const { departements } = useDepartements()

// View
const posteOptions = [{
  label: 'Bureau d\'études',
  value: Poste.BureauDEtudes,
}, {
  label: 'Collectivité, Élu·e',
  value: Poste.CollectiviteElue,
}, {
  label: 'Collectivité, Technicien·ne ou employé·e',
  value: Poste.CollectiviteTechnicienneEmployee,
}, {
  label: 'Agence d\'urbanisme',
  value: Poste.AgenceDUrbanisme,
}, {
  label: 'Autre',
  value: Poste.Autre,
}]

const collectiviteId = ref('')
const collectiviteError = ref<boolean | string>(false)
const collectiviteSuccess = ref(false)
const departementError = ref<boolean | string>(false)
const departementSuccess = ref(false)
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
const phone = ref('')
const phoneError = ref<boolean | string>(false)
const phoneSuccess = ref(false)
const poste = ref('')
const posteError = ref<boolean | string>(false)
const posteSuccess = ref(false)
const submitting = ref(false)

const collectiviteOptions = computed<Options<string>>(() => {
  if (!departementId.value) {
    return [{
      disabled: true,
      label: 'Sélectionnez un département',
      value: '',
    }]
  }

  const optionsByLabel: Record<CollectiviteLabel, Array<Option<string>>> = {
    Communes: [],
    EPCIs: [],
    Groupements: [],
  }

  for (const collectivite of collectivites.value) {
    const label = collectivite.type === 'COM'
      ? 'Communes'
      : EPCI_TYPES.includes(collectivite.type)
        ? 'EPCIs'
        : 'Groupements'

    optionsByLabel[label].push({
      label: collectivite.name,
      value: collectivite.id,
    })
  }

  const labels: Array<CollectiviteLabel> = ['Groupements', 'EPCIs', 'Communes']
  const optionsGroups: Array<OptionGroup<string>> = []

  for (const label of labels) {
    if (!optionsByLabel[label].length) continue

    optionsGroups.push({
      label,
      options: optionsByLabel[label],
    })
  }

  return optionsGroups
})
const collectiviteValidated = computed<boolean>(() =>
  !!collectiviteError.value || collectiviteSuccess.value
)
const departementOptions = computed<Options<string>>(() =>
  departements.value.map(({ id, name }) => ({ label: `${name} - ${id}`, value: id }))
)
const departementValidated = computed<boolean>(() =>
  !!departementError.value || departementSuccess.value
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
const phoneValidated = computed<boolean>(() =>
  !!phoneError.value || phoneSuccess.value
)
const posteValidated = computed<boolean>(() =>
  !!posteError.value || posteSuccess.value
)

// Watchers
watch(departementId, () => {
  collectiviteId.value = ''
})

// Functions
async function submit() {
  submitting.value = true

  // TODO :: Implement this

  submitting.value = false
}

function validateCollectivite() {
  if (collectiviteId.value) {
    collectiviteError.value = false
    collectiviteSuccess.value = true
  } else {
    collectiviteError.value = 'La collectivité est obligatoire.'
    collectiviteSuccess.value = false
  }
}

function validateDepartement() {
  if (departementId.value) {
    departementError.value = false
    departementSuccess.value = true
  } else {
    departementError.value = 'Le département est obligatoire.'
    departementSuccess.value = false
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

function validatePhone() {
  if (phone.value) {
    phoneError.value = false
    phoneSuccess.value = true
  } else {
    phoneError.value = 'Le numéro de téléphone est obligatoire.'
    phoneSuccess.value = false
  }
}

function validatePoste() {
  if (poste.value) {
    posteError.value = false
    posteSuccess.value = true
  } else {
    posteError.value = 'Le poste est obligatoire.'
    posteSuccess.value = false
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
          <h1 class="fr-text fr-text--h1">Inscription Collectivité</h1>
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
            <FrField :error="phoneError"
                     id="signup-phone"
                     :success="phoneSuccess"
                     type="tel"
                     v-model:value="phone"
                     @blur="validatePhone()"
                     @update:value="phoneValidated && validatePhone()">
              <template #label>Téléphone professionel</template>
            </FrField>
            <FrField :error="posteError"
                     id="signup-poste"
                     :options="posteOptions"
                     :success="posteSuccess"
                     type="select"
                     v-model:value="poste"
                     @blur="validatePoste()"
                     @update:value="posteValidated && validatePoste()">
              <template #label>Poste</template>
            </FrField>
            <FrField :error="departementError"
                     id="signup-departement"
                     :options="departementOptions"
                     :success="departementSuccess"
                     type="autocomplete"
                     v-model:value="departementId"
                     @blur="validateDepartement()"
                     @update:value="departementValidated && validateDepartement()">
              <template #label>Département</template>
            </FrField>
            <FrField :error="collectiviteError"
                     id="signup-collectivite"
                     :options="collectiviteOptions"
                     :success="collectiviteSuccess"
                     type="autocomplete"
                     v-model:value="collectiviteId"
                     @blur="validateCollectivite()"
                     @update:value="collectiviteValidated && validateCollectivite()">
              <template #label>Collectivité</template>
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
                        !!collectiviteError
                        || !!departementError
                        || !!emailError
                        || !!firstnameError
                        || !!lastnameError
                        || !!phoneError
                        || !!posteError
                        || submitting
                      "
                      @actuated="submit()">Créer mon compte</FrButton>
          </FrButtons>
        </FrContainer>
      </div>
    </div>
  </FrContainer>
</template>
