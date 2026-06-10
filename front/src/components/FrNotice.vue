<script setup lang="ts">
import { computed } from 'vue'
import FrButton from '@/components/FrButton.vue'
import FrContainer from '@/components/FrContainer.vue'

interface Emit {
  dismissed: [event: KeyboardEvent | MouseEvent | PointerEvent]
}
interface Props {
  alert?: boolean
  dismissMessage?: string
  warning?: boolean
}

const emit = defineEmits<Emit>()
const {
  alert = false,
  dismissMessage = 'Masquer le message',
  warning = false,
} = defineProps<Props>()

const type = computed<string>(() =>
  alert
    ? 'alert'
    : warning
      ? 'warning'
      : 'info'
)
</script>

<template>
  <div class="fr-notice"
       :class="`fr-notice--${type}`">
    <FrContainer>
      <div class="fr-notice__body">
        <p>
          <span class="fr-notice__title">
            <slot name="title" />
          </span>
          <slot />
        </p>
        <FrButton class="fr-icon--before fr-icon--before-close-line fr-notice__close"
                  icon
                  sm
                  :title="dismissMessage"
                  @actuated="emit('dismissed', $event)">{{ dismissMessage }}</FrButton>
      </div>
    </FrContainer>
  </div>
</template>

<style>
.fr-button.fr-notice__close {
  background-color: transparent;
  color: inherit;
}
.fr-notice {
  display: grid;
  padding-bottom: .75rem;
  padding-top: .75rem;
}
.fr-notice--alert {
  background-color: var(--color-error-950-100);
  color: var(--color-error-425-625);
}
.fr-notice--alert .fr-button.fr-notice__close:not([disabled]):focus,
.fr-notice--alert .fr-button.fr-notice__close:not([disabled]):hover {
  background-color: var(--color-error-950-100-hover);
}
.fr-notice--alert .fr-notice__title::before {
  mask-image: url('@/assets/icons/error-warning-fill.svg');
}
.fr-notice--info {
  background-color: var(--color-info-950-100);
  color: var(--color-info-425-625);
}
.fr-notice--info .fr-button.fr-notice__close:not([disabled]):focus,
.fr-notice--info .fr-button.fr-notice__close:not([disabled]):hover {
  background-color: var(--color-info-950-100-hover);
}
.fr-notice--info .fr-notice__title::before {
  mask-image: url('@/assets/icons/info-fill.svg');
}
.fr-notice--warning {
  background-color: var(--color-warning-950-100);
  color: var(--color-warning-425-625);
}
.fr-notice--warning .fr-button.fr-notice__close:not([disabled]):focus,
.fr-notice--warning .fr-button.fr-notice__close:not([disabled]):hover {
  background-color: var(--color-warning-950-100-hover);
}
.fr-notice--warning .fr-notice__title::before {
  mask-image: url('@/assets/icons/warning-fill.svg');
}
.fr-notice__body {
  align-items: center;
  display: grid;
  grid-auto-flow: column;
  justify-content: space-between;
}
.fr-notice__body a {
  box-shadow: inset 0 -.0625rem 0 0 currentColor;
  color: inherit;
  text-decoration: none;
}
.fr-notice__body a:focus,
.fr-notice__body a:hover {
  box-shadow: inset 0 -.0625rem 0 0 currentColor,
              0 .0625rem 0 0 currentColor;
}
.fr-notice__body p {
  font-family: var(--font-family-sans);
  font-size: .875rem;
  font-weight: 400;
  line-height: 1.5rem;
  margin-bottom: 0;
  margin-top: 0;
  padding-bottom: .25rem;
  padding-top: .25rem;
}
.fr-notice__title {
  font-weight: 700;
  margin-right: .5rem;
}
.fr-notice__title::before {
  background-color: currentColor;
  content: '';
  display: inline-block;
  height: 1.5rem;
  margin-right: .5rem;
  mask-size: 100% 100%;
  pointer-events: none;
  vertical-align: top;
  width: 1.5rem;
}

@media (min-width: 48rem) {
  .fr-notice__body p {
    font-size: 1rem;
  }
}
</style>
