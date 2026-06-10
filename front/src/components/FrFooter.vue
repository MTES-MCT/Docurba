<script setup lang="ts">
import FrBrand from '@/components/FrBrand.vue'
import FrContainer from '@/components/FrContainer.vue'

</script>

<template>
  <footer class="fr-footer"
          id="footer"
          role="contentinfo">
    <FrContainer>
      <div class="fr-footer__body">
        <FrBrand lg>
          <template #title>
            <slot name="brand" />
          </template>
        </FrBrand>
        <div class="fr-footer__details">
          <slot />
        </div>
      </div>
    </FrContainer>
  </footer>
</template>

<style>
.fr-footer {
  box-shadow: inset 0 .125rem 0 0 var(--color-blue-france-sun-113-625),
              inset 0 -.0625rem 0 0 var(--color-grey-900-175);
  display: grid;
  padding-bottom: 1rem;
  padding-top: 1rem;
}
.fr-footer__body {
  align-items: start;
  display: grid;
  grid-auto-flow: column;
  grid-template-columns: auto 50%;
  justify-content: space-between;
  margin-left: -1rem;
  margin-right: -1rem;
}
.fr-footer__details {
  display: grid;
  padding: 1rem;
  row-gap: 1rem;
}
</style>
