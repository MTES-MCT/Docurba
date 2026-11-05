<script>
export default {
  props: {
    theme: {
      default: 'light',
      type: String,
    },
  },
}
</script>

<template>
  <div class="fr-layout"
       :data-fr-theme="theme">
    <slot />
  </div>
</template>

<style>
.fr-layout {
  --fr-header__size: var(--fr-header-xs__size);

  align-items: start;
  background-color: var(--fr-color__grey-1000-50);
  display: grid;
  grid-template-rows: auto auto 1fr auto;
  min-height: 100vh;
}

@media (min-width: 62rem) {
  .fr-layout {
    --fr-header__size: var(--fr-header-lg__size);
  }
}
</style>
