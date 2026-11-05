<script>
export default {
  props: {
    value: {
      default: () => [],
      type: Array,
    },
  },
}
</script>

<template>
  <div class="fr-alerts">
    <div class="fr-alerts__body">
      <FRContainer>
        <FRAlert v-for="alert in value"
                 :key="alert.id"
                 dismissible
                 :error="alert.type === 'error'"
                 sm
                 :success="alert.type === 'success'"
                 :warning="alert.type === 'warning'"
                 @dismissed="$emit('dismissed', alert.id)"
                 @mouseenter.native="$emit('paused', alert.id)"
                 @mouseleave.native="$emit('restarted', alert.id)">
          <template v-if="alert.title"
                    #heading>
            {{ alert.title }}
          </template>
          <template v-if="alert.description"
                    #default>
            {{ alert.description }}
          </template>
        </FRAlert>
      </FRContainer>
    </div>
  </div>
</template>

<style>
.fr-alerts {
  position: relative;
  z-index: var(--fr-index__alert);
}
.fr-alerts__body {
  display: grid;
  left: 0;
  padding-top: 1rem;
  pointer-events: none;
  position: absolute;
  right: 0;
  top: 0;
}
.fr-alerts__body > .fr-container {
  justify-content: center;
  row-gap: 1rem;
}
.fr-alerts__body .fr-alert {
  pointer-events: auto;
}
</style>
