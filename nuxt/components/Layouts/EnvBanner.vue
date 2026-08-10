<template>
  <div v-if="visible" class="env-banner">
    {{ label }}
  </div>
</template>

<script>
import { ENVIRONMENT, ENVIRONMENT_LABEL } from '@/plugins/environement'

export default {
  computed: {
    label () {
      return ENVIRONMENT_LABEL[process.env.USER_ENVIRONMENT]
    },
    visible () {
      return this.environment !== ENVIRONMENT.PRODUCTION
    }
  }
}
</script>

<style>
.env-banner {
  background-color: var(--v-primary-base);
  color: #fff;
  display: grid;
  left: 0;
  padding: .5rem 4.6875rem .5rem .8125rem;
  pointer-events: none;
  position: absolute;
  text-align: center;
  top: 3.375rem;
  transform: rotate(-22.5deg);
  transform-origin: bottom left;
  width: 15.25rem;
}
</style>
