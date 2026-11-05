<script>
export default {
  props: {
    value: {
      default: '',
      type: String,
    },
  },
  computed: {
    document() {
      return this.value
        ? { body: this.$md.compile(this.value) }
        : null
    },
  },
}
</script>

<template>
  <NuxtContent v-if="document"
               class="fr-markdown"
               :document="document" />
</template>

<style>
.fr-markdown {
  color: var(--fr-color__grey-200-850);
  display: grid;
  font-size: .875rem;
  font-weight: 400;
  line-height: 1.5rem;
  row-gap: .875rem;
}
.fr-markdown a {
  color: var(--fr-color__blue-france-sun-113-625);
}
.fr-markdown a:focus-visible,
.fr-markdown a:hover {
  color: var(--fr-color__blue-france-sun-113-625--hover);
}
.fr-markdown ol,
.fr-markdown ul {
  padding-left: 1.5rem;
}
</style>
