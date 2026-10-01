<script>
export default {
  props: {
    end: {
      default: false,
      type: Boolean
    },
    horizontal: {
      default: false,
      type: Boolean
    },
    lg: {
      default: false,
      type: Boolean
    },
    md: {
      default: false,
      type: Boolean
    },
    sm: {
      default: false,
      type: Boolean
    },
    start: {
      default: false,
      type: Boolean
    },
    xs: {
      default: false,
      type: Boolean
    },
    xxs: {
      default: false,
      type: Boolean
    }
  }
}
</script>

<template>
  <div
    class="du-group"
    :class="{
      'du-group--end': end,
      'du-group--horizontal': horizontal,
      'du-group--lg': lg,
      'du-group--md': md,
      'du-group--sm': sm,
      'du-group--start': start,
      'du-group--xs': xs,
      'du-group--xxs': xxs
    }"
  >
    <slot />
  </div>
</template>

<style>
.du-group {
  align-items: center;
  display: grid;
}
.du-group--end {
  justify-items: end;
}
.du-group--horizontal {
  display: flex;
  flex-wrap: wrap;
}
.du-group--lg {
  gap: 1.5rem;
}
.du-group--md {
  gap: 1rem;
}
.du-group--sm {
  gap: .75rem;
}
.du-group--start {
  justify-items: start;
}
.du-group--xs {
  gap: .5rem;
}
.du-group--xxs {
  gap: .25rem;
}
</style>
