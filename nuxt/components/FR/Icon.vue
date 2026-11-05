<script>
export default {
  props: {
    md: {
      default: false,
      type: Boolean,
    },
    value: {
      default: '',
      type: String,
    },
  },
}
</script>

<template>
  <div v-if="value"
       class="fr-icon"
       :class="{ 'fr-icon--md': md }">
    <svg aria-hidden="true"
         role="img"
         viewBox="0 0 24 24"
         xmlns="http://www.w3.org/2000/svg">
      <path :d="value" />
    </svg>
  </div>
</template>

<style>
.fr-icon {
  --fr-icon__size: 1.5rem;

  display: grid;
  height: var(--fr-icon__size);
  width: var(--fr-icon__size);
}
.fr-icon--md {
  --fr-icon__size: 1rem;
}
.fr-icon > svg {
  fill: currentColor;
  height: 100%;
  width: 100%;
}
</style>
