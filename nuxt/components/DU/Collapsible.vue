<script>
import { mdiChevronDown, mdiChevronUp } from '@mdi/js'

export default {
  props: {
    value: {
      default: false,
      type: Boolean
    },
    label: {
      default: '',
      type: String
    }
  },
  data () {
    return {
      icons: {
        mdiChevronDown,
        mdiChevronUp
      }
    }
  }
}
</script>

<template>
  <div class="du-collapsible">
    <DUActionable
      class="du-collapsible__action"
      @actuated="$emit('input', !value)"
    >
      {{ label }}
      <VIcon small>
        {{ value ? icons.mdiChevronUp : icons.mdiChevronDown }}
      </VIcon>
    </DUActionable>
    <div
      v-if="value"
      class="du-collapsible__body"
    >
      <slot />
    </div>
  </div>
</template>

<style>
.du-collapsible {
  box-shadow: inset 0 -.0625rem 0 0 #ddd;
  display: grid;
}
.du-collapsible__action {
  align-items: center;
  background-color: #e3e3fd;
  box-shadow: inset 0 .0625rem 0 0 #ddd;
  color: #000091;
  cursor: pointer;
  display: grid;
  font-size: 1rem;
  font-weight: 500;
  grid-auto-flow: column;
  justify-content: space-between;
  line-height: 1.5rem;
  padding: .75rem 1rem;
}
.du-collapsible__action:last-child {
  background-color: transparent;
  box-shadow: inset 0 .0625rem 0 0 #ddd,
              inset 0 -.0625rem 0 0 #ddd;
}
.du-collapsible__body {
  display: grid;
  padding: 1rem;
  row-gap: 1rem;
}
</style>
