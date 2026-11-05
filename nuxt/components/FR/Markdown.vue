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
.fr-markdown h1,
.fr-markdown h2,
.fr-markdown h3,
.fr-markdown h4,
.fr-markdown h5,
.fr-markdown h6 {
  font-weight: 700;
}
.fr-markdown h1 {
  font-size: 1.75rem;
  line-height: 2.25rem;
}
.fr-markdown h2 {
  font-size: 1.5rem;
  line-height: 2rem;
}
.fr-markdown h3 {
  font-size: 1.375rem;
  line-height: 1.75rem;
}
.fr-markdown h4 {
  font-size: 1.25rem;
  line-height: 1.75rem;
}
.fr-markdown h5 {
  font-size: 1.125rem;
  line-height: 1.625rem;
}
.fr-markdown h6 {
  font-size: 1rem;
  line-height: 1.5rem;
}
.fr-markdown img {
  max-width: 100%;
}
.fr-markdown ol,
.fr-markdown ul {
  padding-left: 1.5rem;
}
.fr-markdown .column {
  display: grid;
  row-gap: .875rem;
}
.fr-markdown .column-block {
  column-gap: 1rem;
  display: grid;
  grid-auto-columns: 1fr;
  grid-auto-flow: column;
}

@media (min-width: 62rem) {
  .fr-markdown .column-block {
    column-gap: 1.5rem;
  }
}
</style>
