<script>
import { mdiMenuDown, mdiMenuUp } from '@mdi/js'

export default {
  props: {
    disabled: {
      default: false,
      type: Boolean
    },
    label: {
      default: '',
      type: String
    },
    value: {
      default: false,
      type: Boolean
    }
  },
  data () {
    return {
      icons: {
        mdiMenuDown,
        mdiMenuUp
      }
    }
  }
}
</script>

<template>
  <div class="du-collapsible-card">
    <DUCard>
      <slot name="header" />
    </DUCard>
    <div
      v-if="!disabled"
      class="du-collapsible-card__body"
    >
      <DUActionable
        class="du-collapsible-card__action"
        @actuated="$emit('input', !value)"
      >
        <VIcon>
          {{ value ? icons.mdiMenuUp : icons.mdiMenuDown }}
        </VIcon>
        {{ value ? '' : label }}
      </DUActionable>
      <div
        v-if="value"
        class="du-collapsible-card__content"
      >
        <slot />
      </div>
    </div>
  </div>
</template>

<style>
.du-collapsible-card {
  background-color: #f6f6f6;
  display: grid;
  padding: 1.5rem;
  row-gap: 1rem;
}
.du-collapsible-card .du-card {
  box-shadow: inset 0 0 0 .0625rem #ddd,
              0 .25rem .25rem 0 hsl(0 0% 0% / 25%);
}
.du-collapsible-card__action {
  color: #666;
  column-gap: .5rem;
  cursor: pointer;
  display: grid;
  font-size: .75rem;
  font-weight: 400;
  grid-auto-flow: column;
  justify-content: start;
  line-height: 1.5rem;
  padding-left: .5rem;
  padding-right: .5rem;
}
.du-collapsible-card__action .v-icon {
  color: #000091;
  font-size: 2rem;
  height: 2rem;
  margin-bottom: -.25rem;
  margin-top: -.25rem;
  pointer-events: none;
  width: 2rem;
}
.du-collapsible-card__action .v-icon__svg {
  height: 2rem;
  width: 2rem;
}
.du-collapsible-card__body {
  column-gap: 1rem;
  display: grid;
  grid-auto-columns: 1fr 50rem;
  grid-auto-flow: column;
}
.du-collapsible-card__content {
  display: grid;
  gap: 1rem;
  grid-template-columns: 16rem 16rem 16rem;
}
</style>
