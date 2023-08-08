import { required, email, min, regex, integer } from 'vee-validate/dist/rules'
import { extend, ValidationObserver, ValidationProvider, setInteractionMode } from 'vee-validate'
// import test from '@/assets/data/testInputs.json'

// eslint-disable-next-line
setInteractionMode('eager')

extend('required', {
  ...required,
  message: '{_field_} ne doit pas être vide'
})

extend('email', {
  ...email,
  message: 'Email doit être valide'
})

extend('min', {
  ...min,
  message: '{_field_} doit contenir au moins {length} caractères.'
})

extend('needToBeOui', {
  params: ['target'],
  validate (value, { target }) {
    return value === 'oui'
  },
  message: 'Vous n\'êtes pas sur la bonne collectivité.'
})

extend('requiredCollectivite', {
  validate (value) {
    console.log('requiredCollectivite:', value)
    return (value.EPCI || value.code_commune_INSEE)
  },
  message: 'Vous devez choisir une collectivité'
})

extend('password', {
  params: ['target'],
  validate (value, { target }) {
    return value === target
  },
  message: 'Les champs "mot de passe" sont différents'
})

extend('integer', {
  ...integer,
  message: '{_field_} must be an integer'
})

extend('regex_phone', {
  ...regex,
  message: '{_field_} {_value_} should be a valid phone number'
})

extend('regex_date', {
  ...regex,
  message: '{_field_} must be in the format dd/MM/yyyy'
})

extend('asMuchAsCan', {
  ...required,
  message: 'Please fill as much as you can'
})

extend('expirationDateCreditCard', {
  validate (value, args) {
    return !!value
  },
  message: 'Please fill as much as you can'
})
// @vue/component
export default {
  components: {
    ValidationProvider,
    ValidationObserver
  },
  props: {
    value: {
      type: Object,
      default () { return {} }
    }
    // test: {
    //   type: Object,
    //   default () {
    //     return process.env.NODE_ENV === 'development' ? test : {}
    //   }
    // }
  },
  methods: {
    input (data) {
      this.$emit('input', Object.assign({}, this.value, data))
    }
  }
}
