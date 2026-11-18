<script>
import { mdiAlert, mdiCheckCircle, mdiClose, mdiCloseOctagon, mdiInformation } from '@mdi/js'

export default {
  props: {
    dismissible: {
      default: false,
      type: Boolean
    },
    error: {
      default: false,
      type: Boolean
    },
    sm: {
      default: false,
      type: Boolean
    },
    success: {
      default: false,
      type: Boolean
    },
    type: {
      default: 'info',
      type: String
    },
    warning: {
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
    icon () {
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
  }
}
</script>

<template>
  <div
    class="du-alert"
    :class="{
      'du-alert--error': error,
      'du-alert--sm': sm,
      'du-alert--success': success,
      'du-alert--warning': warning,
    }"
  >
    <VIcon class="du-alert__icon">
      {{ icon }}
    </VIcon>
    <div class="du-alert__body">
      <div
        v-if="$slots.heading"
        class="du-alert__heading"
      >
        <slot name="heading" />
      </div>
      <div
        v-if="$slots.default"
        class="du-alert__description"
      >
        <slot />
      </div>
    </div>
    <DUButton
      v-if="dismissible"
      class="du-alert__action"
      sm
      tertiary-borderless
      @actuated="$emit('dismissed', $event)"
    >
      <VIcon>
        {{ icons.mdiClose }}
      </VIcon>
    </DUButton>
  </div>
</template>

<style>
.du-alert {
  --du-alert__color: #0063cb;

  align-items: start;
  background-color: #ffffff;
  box-shadow: inset 0 0 0 .0625rem var(--du-alert__color),
              inset 2.5rem 0 0 0 var(--du-alert__color);
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: auto 1fr auto;
}
.du-alert--error {
  --du-alert__color: #ce0500;
}
.du-alert--sm .du-alert__body {
  padding-bottom: .5rem;
  padding-left: .5rem;
  padding-top: .5rem;
}
.du-alert--sm .du-alert__body:last-child {
  padding-right: 1rem;
}
.du-alert--sm .du-alert__icon {
  margin-bottom: .5rem;
  margin-top: .5rem;
}
.du-alert--success {
  --du-alert__color: #18753c;
}
.du-alert--warning {
  --du-alert__color: #b34000;
}
.du-alert__action {
  margin: .25rem;
}
.du-alert__body {
  align-content: center;
  align-self: stretch;
  display: grid;
  padding-bottom: 1rem;
  padding-left: 1rem;
  padding-top: 1rem;
  row-gap: .125rem;
}
.du-alert__body:last-child {
  padding-right: 1.5rem;
}
.du-alert__description {
  color: #3a3a3a;
  font-size: 1rem;
  font-weight: 400;
  line-height: 1.5rem;
}
.du-alert__heading {
  color: #161616;
  font-size: 1.25rem;
  font-weight: 700;
  line-height: 1.75rem;
}
.du-alert__icon {
  color: #ffffff !important;
  margin: 1rem .5rem;
}
</style>
