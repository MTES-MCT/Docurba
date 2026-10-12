<script>
import { mdiArrowRight } from '@mdi/js'

export default {
  props: {
    to: {
      default: undefined,
      type: [String, Object]
    }
  },
  data () {
    return {
      icons: {
        mdiArrowRight
      }
    }
  }
}
</script>

<template>
  <DUActionable
    class="du-card"
    :disabled="!to"
    :to="to"
  >
    <div class="du-card__body">
      <slot />
    </div>
    <VIcon
      v-if="to"
      class="du-card__action"
      small
    >
      {{ icons.mdiArrowRight }}
    </VIcon>
  </DUActionable>
</template>

<style>
.du-card {
  align-content: space-between;
  background-color: #fff;
  box-shadow: inset 0 0 0 .0625rem #ddd;
  color: #161616;
  display: grid;
  padding: 1.5rem;
  row-gap: .5rem;
  text-decoration: none;
}
a.du-card:focus-visible,
a.du-card:hover {
  background-color: #f6f6f6;
}
.du-card .v-icon {
  color: inherit;
}
.du-card__action.v-icon {
  color: #000091;
  justify-self: end;
}
.du-card__body {
  display: grid;
  row-gap: 1rem;
}
</style>
