<script setup lang="ts">
import BaseActionable from '@/components/BaseActionable.vue'

interface Props {
  lg?: boolean
  sm?: boolean
}

const {
  lg = false,
  sm = false,
} = defineProps<Props>()
</script>

<template>
  <div class="fr-brand fr-link-container"
       :class="{
         'fr-brand--lg': lg,
         'fr-brand--sm': sm,
       }">
    <BaseActionable class="fr-brand__logo"
                    to="/">
      <p>
        <slot name="title" />
      </p>
    </BaseActionable>
    <slot />
  </div>
</template>

<style>
.fr-brand {
  align-items: center;
  display: grid;
  grid-auto-flow: column;
}
.fr-brand:focus-within,
.fr-brand:hover {
  background-color: var(--color-grey-1000-75-hover);
}
.fr-brand--lg .fr-brand__logo p {
  font-size: 1.3125rem;
  line-height: 1.3541666667rem;
}
.fr-brand--lg .fr-brand__logo p::before {
  background-position: 0 -.078125rem,
                       00,
                       00;
  background-size: 3.4375rem 1.40625rem,
                   3.4375rem 1.25rem,
                   0;
  height: 1.25rem;
  margin-bottom: .4166666667rem;
  width: 3.4375rem;
}
.fr-brand--lg .fr-brand__logo p::after {
  background-position: 0 calc(100% + 2.34375rem);
  background-size: 6.5625rem 4.6875rem;
  height: 2.7604166667rem;
  min-width: 3.28125rem;
}
.fr-brand--sm .fr-brand__logo p {
  font-size: .7875rem;
  line-height: .8125rem;
}
.fr-brand--sm .fr-brand__logo p::before {
  background-position: 0 -.046875rem,
                       00,
                       00;
  background-size: 2.0625rem .84375rem,
                   2.0625rem .75rem,
                   0;
  height: .75rem;
  margin-bottom: .25rem;
  width: 2.0625rem;
}
.fr-brand--sm .fr-brand__logo p::after {
  background-position: 0 calc(100% + 1.40625rem);
  background-size: 3.9375rem 2.8125rem;
  height: 1.65625rem;
  min-width: 1.96875rem;
}
.fr-brand__logo {
  display: grid;
  padding: 1rem;
  text-decoration: none;
}
.fr-brand__logo p {
  color: var(--color-grey-50-1000);
  display: inline-block;
  font-family: var(--font-family-sans);
  font-size: 1.05rem;
  font-weight: 700;
  letter-spacing: -.01em;
  line-height: 1.0833333333rem;
  margin-bottom: 0;
  margin-top: 0;
  text-indent: -.1em;
  text-transform: uppercase;
  vertical-align: middle;
}
.fr-brand__logo p::before {
  background-image: url('@/assets/images/marianne.svg'),
                    linear-gradient(90deg, #000091, #000091 50%, #e1000f 0, #e1000f),
                    linear-gradient(90deg, #000, #000);
  background-position: 0 -.0625rem,
                       00,
                       00;
  background-size: 2.75rem 1.125rem,
                   2.75rem 1rem,
                   0;
  content: '';
  display: block;
  height: 1rem;
  margin-bottom: .3333333333rem;
  width: 2.75rem;
}
.fr-brand__logo p::after {
  background-image: url('@/assets/images/liberte-egalite-fraternite.svg');
  background-position: 0 calc(100% + 1.875rem);
  background-size: 5.25rem 3.75rem;
  background-repeat: no-repeat;
  content: '';
  display: block;
  height: 2.2083333333rem;
  min-width: 2.625rem;
}

@media (prefers-color-scheme: dark) {
  .fr-brand--lg .fr-brand__logo p::after {
    background-position: -3.28125rem 100%;
  }
  .fr-brand--sm .fr-brand__logo p::after {
    background-position: -1.96875rem 100%;
  }
  .fr-brand__logo p::after {
    background-position: -2.625rem 100%;
  }
}
</style>
