<script>
export default {
  props: {
    id: {
      default: undefined,
      type: String
    },
    proceduresCount: {
      default: 0,
      type: Number
    },
    respondant: {
      default: null,
      type: Object
    },
    value: {
      default: false,
      type: Boolean
    }
  },
  computed: {
    disabled () {
      return (
        this.value &&
        !!this.respondant &&
        this.respondant.id !== this.$user.id
      )
    },
    hint () {
      return this.respondant
        ? `par ${this.respondant.firstname} ${this.respondant.lastname}`
        : undefined
    },
    label () {
      return this.value
        ? 'Collectivité validée'
        : this.proceduresCount === 1
          ? `Je confirme que ${
            this.$route.query.type === 'scot'
              ? 'le SCoT'
              : 'la procédure'
          } de la collectivité${
            this.$route.query.type === 'scot' ? '' : ' (hors SCoT)'
          } est à jour`
          : `Je confirme que les ${
            this.proceduresCount
          } ${
            this.$route.query.type === 'scot'
              ? 'SCoT'
              : 'procédures'
          } de la collectivité${
            this.$route.query.type === 'scot' ? '' : ' (hors SCoT)'
          } sont à jour`
    },
    model: {
      get () {
        return this.value
      },
      set (value) {
        this.$emit('input', value)
      }
    }
  }
}
</script>

<template>
  <DUField
    :id="id"
    v-model="model"
    :disabled="disabled"
    type="checkbox"
  >
    <template #default>
      {{ label }}
    </template>
    <template
      v-if="hint"
      #hint
    >
      {{ hint }}
    </template>
  </DUField>
</template>
