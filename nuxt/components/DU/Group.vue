<script>
export default {
  props: {
    between: {
      default: false,
      type: Boolean
    },
    end: {
      default: false,
      type: Boolean
    },
    horizontal: {
      default: false,
      type: Boolean
    },
    grid: {
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
    padLg: {
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
    xl: {
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
      'du-group--between': between,
      'du-group--end': end,
      'du-group--grid': grid,
      'du-group--horizontal': horizontal,
      'du-group--lg': lg,
      'du-group--md': md,
      'du-group--pad-lg': padLg,
      'du-group--sm': sm,
      'du-group--start': start,
      'du-group--xl': xl,
      'du-group--xs': xs,
      'du-group--xxs': xxs
    }"
  >
    <slot />
  </div>
</template>

<style>
.du-group {
  display: grid;
}
.du-group--between {
  grid-auto-flow: column;
  justify-content: space-between;
}
.du-group--end {
  justify-items: end;
}
.du-group--grid {
  grid-auto-columns: 1fr;
  grid-auto-flow: column;
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
.du-group--pad-lg {
  padding: 1.5rem;
}
.du-group--sm {
  gap: .75rem;
}
.du-group--start {
  justify-items: start;
}
.du-group--xl {
  gap: 2rem;
}
.du-group--xs {
  gap: .5rem;
}
.du-group--xxs {
  gap: .25rem;
}
</style>
