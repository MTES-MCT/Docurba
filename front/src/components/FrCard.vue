<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  level?: 1 | 2 | 3 | 4 | 5 | 6
}

const {
  level = 3,
} = defineProps<Props>()

const tag = computed<'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6'>(() => `h${level}`)
</script>

<template>
  <div class="fr-card">
    <div class="fr-card__body">
      <div class="fr-card__content">
        <component :is="tag"
                   class="fr-card__title">
          <slot name="title" />
        </component>
        <slot />
      </div>
      <div v-if="$slots.footer"
           class="fr-card__footer">
        <slot name="footer" />
      </div>
    </div>
  </div>
</template>

<style>
.fr-card {
  background-color: var(--color-grey-1000-50);
  box-shadow: inset 0 0 0 .0625rem var(--color-grey-900-175);
  display: grid;
}
.fr-card__body {
  display: grid;
  align-content: space-between;
  padding: 2rem;
  row-gap: 2rem;
}
.fr-card__content {
  display: grid;
  row-gap: .75rem;
}
.fr-card__footer {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.fr-card__title {
  color: var(--color-grey-50-1000);
  font-family: var(--font-family-sans);
  font-size: 1.5rem;
  font-weight: 700;
  line-height: 2rem;
  margin-bottom: 0;
  margin-top: 0;
}

@media (min-width: 48rem) {
  .fr-card__footer {
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: end;
  }
  .fr-card__title {
    font-size: 1.75rem;
    line-height: 2.25rem;
  }
}
</style>
