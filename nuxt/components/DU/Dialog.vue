<script>
import { mdiClose } from '@mdi/js'

export default {
  props: {
    value: {
      default: false,
      type: Boolean
    }
  },
  data () {
    return {
      icons: {
        mdiClose
      }
    }
  },
  computed: {
    model: {
      get () {
        return this.value
      },
      set (newValue) {
        this.$emit('input', newValue)
      }
    }
  }
}
</script>

<template>
  <VDialog
    v-model="model"
    content-class="du-dialog"
  >
    <DUButton
      sm
      tertiary-borderless
      @actuated="model = false"
    >
      Fermer
      <VIcon small>
        {{ icons.mdiClose }}
      </VIcon>
    </DUButton>
    <div class="du-dialog__body">
      <slot />
    </div>
  </VDialog>
</template>

<style>
.du-dialog {
  background-color: #fff;
  border-radius: 0;
  display: grid;
  justify-items: end;
  max-width: 50rem;
  padding: 1rem 1rem 4rem;
  row-gap: 1rem;
}
.du-dialog > .du-button {
  width: auto;
}
.du-dialog__body {
  display: grid;
  padding-left: 1rem;
  padding-right: 1rem;
  row-gap: 1.5rem;
}
</style>
