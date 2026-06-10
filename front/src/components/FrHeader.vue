<script setup lang="ts">
import FrBrand from '@/components/FrBrand.vue'
import FrContainer from '@/components/FrContainer.vue'
</script>

<template>
  <header class="fr-header"
          role="banner">
    <div class="fr-header__body">
      <FrContainer>
        <div class="fr-header__body-row">
          <FrBrand sm>
            <template #title>
              République<br />
              Française
            </template>
            <template #default>
              <p class="fr-header__service fr-text fr-text--h6">
                <slot name="service" />
              </p>
            </template>
          </FrBrand>
          <div v-if="$slots.tools"
               class="fr-header__tools">
            <slot name="tools" />
          </div>
        </div>
      </FrContainer>
    </div>
  </header>
</template>

<style>
.fr-header {
  display: grid;
}
.fr-header__body {
  display: grid;
}
.fr-header__body-row {
  align-items: center;
  display: grid;
  grid-auto-flow: column;
  justify-content: space-between;
  margin-left: -1rem;
  margin-right: -1rem;
}
.fr-header__service {
  display: grid;
}
.fr-header__tools {
  column-gap: .5rem;
  display: grid;
  grid-auto-flow: column;
  padding: 1rem;
}

@media (min-width: 62rem) {
  .fr-header {
    background-color: var(--color-grey-1000-75);
    filter: drop-shadow(var(--shadow-raised));
  }
  .fr-header__body-row {
    padding-bottom: .5rem;
    padding-top: .5rem;
  }
  .fr-header__service {
    padding: 1rem;
  }
}
</style>
