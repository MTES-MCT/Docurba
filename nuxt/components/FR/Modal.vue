<script>
import { mdiClose } from '@mdi/js'

export default {
  data() {
    return {
      icons: {
        mdiClose,
      },
    }
  },
  beforeCreate() {
    document.documentElement.setAttribute('data-fr-modal', true)
  },
  destroyed() {
    document.documentElement.removeAttribute('data-fr-modal')
  },
}
</script>

<template>
  <div class="fr-modal__backdrop">
    <div class="fr-modal">
      <FRButton sm
                tertiary-borderless
                @actuated="$emit('closed', $event)">
        Fermer
        <FRIcon :value="icons.mdiClose" />
      </FRButton>
      <div class="fr-modal__body">
        <slot />
      </div>
    </div>
  </div>
</template>

<style>
[data-fr-modal] {
  max-height: 100%;
  overflow: hidden;
}

.fr-modal {
  background-color: var(--fr-color__grey-1000-50);
  box-shadow: 0 0 0 .0625rem var(--fr-color__grey-900-175);
  display: grid;
  max-height: 100%;
  max-width: 50rem;
  overflow: auto;
  padding: 1rem 2rem 4rem;
  row-gap: 1rem;
}
.fr-modal > .fr-button {
  justify-self: end;
}
.fr-modal__backdrop {
  align-content: center;
  background-color: hsla(0, 0%, 9%, .64);
  display: grid;
  inset: 0;
  justify-content: center;
  padding: 1rem;
  position: fixed;
  z-index: var(--fr-index__modal);
}
.fr-modal__body {
  display: grid;
  row-gap: 1rem;
}

@media (min-width: 62rem) {
  .fr-modal__backdrop {
    padding: 1.5rem;
  }
}
</style>
