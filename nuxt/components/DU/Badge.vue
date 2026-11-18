<script>
export default {
  props: {
    sm: {
      default: false,
      type: Boolean
    }
  }
}
</script>

<template>
  <div
    class="du-badge"
    :class="{ 'du-badge--sm': sm }"
  >
    <slot />
  </div>
</template>

<style>
.du-badge {
  --du-badge__bg: #eeeeee;
  --du-badge__border: transparent;
  --du-badge__color: #3a3a3a;

  background-color: var(--du-badge__bg);
  border-radius: .25rem;
  box-shadow: inset 0 0 0 .0625rem var(--du-badge__border);
  color: var(--du-badge__color);
  column-gap: .5rem;
  display: grid;
  font-size: .875rem;
  font-weight: 700;
  grid-auto-flow: column;
  line-height: 1.5rem;
  padding-left: .5rem;
  padding-right: .5rem;
  text-transform: uppercase;
  white-space: nowrap;
}
.du-badge > .v-icon {
  margin: .25rem -.25rem;
}
.du-badge--sm {
  column-gap: .375rem;
  font-size: .75rem;
  line-height: 1.25rem;
  padding-left: .375rem;
  padding-right: .375rem;
}
.du-badge--sm > .v-icon {
  margin-left: -.125rem;
  margin-right: -.125rem;
}
</style>
