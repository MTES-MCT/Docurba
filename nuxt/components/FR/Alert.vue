<script>
import {
  mdiAlert,
  mdiCheckCircle,
  mdiClose,
  mdiCloseOctagon,
  mdiInformation,
} from '@mdi/js'

export default {
  props: {
    dismissible: {
      default: false,
      type: Boolean,
    },
    error: {
      default: false,
      type: Boolean,
    },
    sm: {
      default: false,
      type: Boolean,
    },
    success: {
      default: false,
      type: Boolean,
    },
    type: {
      default: 'info',
      type: String,
    },
    warning: {
      default: false,
      type: Boolean,
    },
  },
  data () {
    return {
      icons: {
        mdiClose,
      },
    }
  },
  computed: {
    icon() {
      if (this.error) {
        return mdiCloseOctagon
      }
      if (this.success) {
        return mdiCheckCircle
      }
      if (this.warning) {
        return mdiAlert
      }

      return mdiInformation
    }
  },
}
</script>

<template>
  <div class="fr-alert"
       :class="{
         'fr-alert--error': error,
         'fr-alert--sm': sm,
         'fr-alert--success': success,
         'fr-alert--warning': warning,
       }">
    <FRIcon class="fr-alert__icon"
            :value="icon" />
    <div class="fr-alert__body">
      <FRText v-if="$slots.heading"
              h6>
        <slot name="heading" />
      </FRText>
      <FRText v-if="$slots.default">
        <slot />
      </FRText>
    </div>
    <FRButton v-if="dismissible"
              class="fr-alert__action"
              sm
              tertiary-borderless
              @actuated="$emit('dismissed', $event)">
      <FRIcon :value="icons.mdiClose" />
    </FRButton>
  </div>
</template>

<style>
.fr-alert {
  --fr-alert__color: var(--fr-color__info-425-625);

  align-items: start;
  background-color: var(--fr-color__grey-1000-50);
  box-shadow: inset 0 0 0 .0625rem var(--fr-alert__color),
              inset 2.5rem 0 0 0 var(--fr-alert__color);
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: auto 1fr auto;
}
.fr-alert--error {
  --fr-alert__color: var(--fr-color__error-425-625);
}
.fr-alert--sm .fr-alert__body {
  padding-bottom: .5rem;
  padding-left: .5rem;
  padding-top: .5rem;
}
.fr-alert--sm .fr-alert__body:last-child {
  padding-right: .5rem;
}
.fr-alert--sm .fr-alert__icon {
  margin-bottom: .5rem;
  margin-top: .5rem;
}
.fr-alert--success {
  --fr-alert__color: var(--fr-color__success-425-625);
}
.fr-alert--warning {
  --fr-alert__color: var(--fr-color__warning-425-625);
}
.fr-alert__action {
  margin: .25rem;
}
.fr-alert__body {
  align-content: center;
  align-self: stretch;
  display: grid;
  padding-bottom: 1rem;
  padding-left: 1rem;
  padding-top: 1rem;
  row-gap: .125rem;
}
.fr-alert__body:last-child {
  padding-right: 1rem;
}
.fr-alert__icon {
  color: var(--fr-color__grey-1000-50);
  margin: 1rem .5rem;
}
</style>
