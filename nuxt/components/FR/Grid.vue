<script>
export default {
  props: {
    alt: {
      default: false,
      type: Boolean,
    },
    aside: {
      default: false,
      type: Boolean,
    },
    between: {
      default: false,
      type: Boolean,
    },
    end: {
      default: false,
      type: Boolean,
    },
    gap: {
      default: '',
      type: String,
    },
    horizontal: {
      default: false,
      type: Boolean,
    },
    size: {
      default: '',
      type: String,
    },
    start: {
      default: false,
      type: Boolean,
    },
  },
  computed: {
    elementClass() {
      const elementClass = []

      if (this.alt) {
        elementClass.push('fr-grid--alt')
      }
      if (this.aside) {
        elementClass.push('fr-grid--aside')
      }
      if (this.between) {
        elementClass.push('fr-grid--between')
      }
      if (this.end) {
        elementClass.push('fr-grid--end')
      }
      if (this.gap) {
        this.gap.split(' ').forEach((gap) => {
          if (gap.includes('-')) {
            const [screen, ...parts] = gap.split('-')

            elementClass.push(`fr-grid-${screen}--gap-${parts.join('-')}`)
          } else {
            elementClass.push(`fr-grid--gap-${gap}`)
          }
        })
      }
      if (this.horizontal) {
        elementClass.push('fr-grid--horizontal')
      }
      if (this.size) {
        this.size.split(' ').forEach((size) => {
          if (size.includes('-')) {
            const [screen, ...parts] = size.split('-')

            elementClass.push(`fr-grid-${screen}--${parts.join('-')}`)
          } else {
            elementClass.push(`fr-grid--${size}`)
          }
        })
      }
      if (this.start) {
        elementClass.push('fr-grid--start')
      }

      return elementClass
    },
  },
}
</script>

<template>
  <div class="fr-grid"
       :class="elementClass">
    <slot />
  </div>
</template>

<style>
.fr-grid {
  --fr-grid__gap: 0;
  --fr-grid__size: 0;

  display: grid;
  gap: var(--fr-grid__gap);
  padding-bottom: var(--fr-grid__size);
  padding-top: var(--fr-grid__size);
}
.fr-grid--alt {
  background-color: var(--fr-color__grey-975-75);
}
.fr-grid--between,
.fr-grid--horizontal {
  align-items: center;
}
.fr-grid--between {
  grid-auto-flow: column;
  justify-content: space-between;
}
.fr-grid--end {
  justify-items: end;
}
.fr-grid--horizontal {
  display: flex;
  flex-wrap: wrap;
  justify-content: start;
}
.fr-grid--start {
  justify-items: start;
}
/* Gaps */
.fr-grid--gap-xxs {
  --fr-grid__gap: var(--fr-size__xxs);
}
.fr-grid--gap-xs {
  --fr-grid__gap: var(--fr-size__xs);
}
.fr-grid--gap-sm {
  --fr-grid__gap: var(--fr-size__sm);
}
.fr-grid--gap-md {
  --fr-grid__gap: var(--fr-size__md);
}
.fr-grid--gap-lg {
  --fr-grid__gap: var(--fr-size__lg);
}
.fr-grid--gap-xl {
  --fr-grid__gap: var(--fr-size__xl);
}
.fr-grid--gap-xxl {
  --fr-grid__gap: var(--fr-size__xxl);
}
/* Sizes */
.fr-grid--xxs {
  --fr-grid__size: var(--fr-size__xxs);
}
.fr-grid--xs {
  --fr-grid__size: var(--fr-size__xs);
}
.fr-grid--sm {
  --fr-grid__size: var(--fr-size__sm);
}
.fr-grid--md {
  --fr-grid__size: var(--fr-size__md);
}
.fr-grid--lg {
  --fr-grid__size: var(--fr-size__lg);
}
.fr-grid--xl {
  --fr-grid__size: var(--fr-size__xl);
}
.fr-grid--xxl {
  --fr-grid__size: var(--fr-size__xxl);
}

@media (min-width: 36rem) {
  /* Gaps */
  .fr-grid-sm--gap-xxs {
    --fr-grid__gap: var(--fr-size__xxs);
  }
  .fr-grid-sm--gap-xs {
    --fr-grid__gap: var(--fr-size__xs);
  }
  .fr-grid-sm--gap-sm {
    --fr-grid__gap: var(--fr-size__sm);
  }
  .fr-grid-sm--gap-md {
    --fr-grid__gap: var(--fr-size__md);
  }
  .fr-grid-sm--gap-lg {
    --fr-grid__gap: var(--fr-size__lg);
  }
  .fr-grid-sm--gap-xl {
    --fr-grid__gap: var(--fr-size__xl);
  }
  .fr-grid-sm--gap-xxl {
    --fr-grid__gap: var(--fr-size__xxl);
  }
  /* Sizes */
  .fr-grid-sm--xxs {
    --fr-grid__size: var(--fr-size__xxs);
  }
  .fr-grid-sm--xs {
    --fr-grid__size: var(--fr-size__xs);
  }
  .fr-grid-sm--sm {
    --fr-grid__size: var(--fr-size__sm);
  }
  .fr-grid-sm--md {
    --fr-grid__size: var(--fr-size__md);
  }
  .fr-grid-sm--lg {
    --fr-grid__size: var(--fr-size__lg);
  }
  .fr-grid-sm--xl {
    --fr-grid__size: var(--fr-size__xl);
  }
  .fr-grid-sm--xxl {
    --fr-grid__size: var(--fr-size__xxl);
  }
}

@media (min-width: 48rem) {
  .fr-grid--aside {
    grid-auto-flow: column;
    grid-auto-columns: auto 1fr;
  }
  /* Gaps */
  .fr-grid-md--gap-xxs {
    --fr-grid__gap: var(--fr-size__xxs);
  }
  .fr-grid-md--gap-xs {
    --fr-grid__gap: var(--fr-size__xs);
  }
  .fr-grid-md--gap-sm {
    --fr-grid__gap: var(--fr-size__sm);
  }
  .fr-grid-md--gap-md {
    --fr-grid__gap: var(--fr-size__md);
  }
  .fr-grid-md--gap-lg {
    --fr-grid__gap: var(--fr-size__lg);
  }
  .fr-grid-md--gap-xl {
    --fr-grid__gap: var(--fr-size__xl);
  }
  .fr-grid-md--gap-xxl {
    --fr-grid__gap: var(--fr-size__xxl);
  }
  /* Sizes */
  .fr-grid-md--xxs {
    --fr-grid__size: var(--fr-size__xxs);
  }
  .fr-grid-md--xs {
    --fr-grid__size: var(--fr-size__xs);
  }
  .fr-grid-md--sm {
    --fr-grid__size: var(--fr-size__sm);
  }
  .fr-grid-md--md {
    --fr-grid__size: var(--fr-size__md);
  }
  .fr-grid-md--lg {
    --fr-grid__size: var(--fr-size__lg);
  }
  .fr-grid-md--xl {
    --fr-grid__size: var(--fr-size__xl);
  }
  .fr-grid-md--xxl {
    --fr-grid__size: var(--fr-size__xxl);
  }
}

@media (min-width: 62rem) {
  /* Gaps */
  .fr-grid-lg--gap-xxs {
    --fr-grid__gap: var(--fr-size__xxs);
  }
  .fr-grid-lg--gap-xs {
    --fr-grid__gap: var(--fr-size__xs);
  }
  .fr-grid-lg--gap-sm {
    --fr-grid__gap: var(--fr-size__sm);
  }
  .fr-grid-lg--gap-md {
    --fr-grid__gap: var(--fr-size__md);
  }
  .fr-grid-lg--gap-lg {
    --fr-grid__gap: var(--fr-size__lg);
  }
  .fr-grid-lg--gap-xl {
    --fr-grid__gap: var(--fr-size__xl);
  }
  .fr-grid-lg--gap-xxl {
    --fr-grid__gap: var(--fr-size__xxl);
  }
  /* Sizes */
  .fr-grid-lg--xxs {
    --fr-grid__size: var(--fr-size__xxs);
  }
  .fr-grid-lg--xs {
    --fr-grid__size: var(--fr-size__xs);
  }
  .fr-grid-lg--sm {
    --fr-grid__size: var(--fr-size__sm);
  }
  .fr-grid-lg--md {
    --fr-grid__size: var(--fr-size__md);
  }
  .fr-grid-lg--lg {
    --fr-grid__size: var(--fr-size__lg);
  }
  .fr-grid-lg--xl {
    --fr-grid__size: var(--fr-size__xl);
  }
  .fr-grid-lg--xxl {
    --fr-grid__size: var(--fr-size__xxl);
  }
}

@media (min-width: 78rem) {
  /* Gaps */
  .fr-grid-xl--gap-xxs {
    --fr-grid__gap: var(--fr-size__xxs);
  }
  .fr-grid-xl--gap-xs {
    --fr-grid__gap: var(--fr-size__xs);
  }
  .fr-grid-xl--gap-sm {
    --fr-grid__gap: var(--fr-size__sm);
  }
  .fr-grid-xl--gap-md {
    --fr-grid__gap: var(--fr-size__md);
  }
  .fr-grid-xl--gap-lg {
    --fr-grid__gap: var(--fr-size__lg);
  }
  .fr-grid-xl--gap-xl {
    --fr-grid__gap: var(--fr-size__xl);
  }
  .fr-grid-xl--gap-xxl {
    --fr-grid__gap: var(--fr-size__xxl);
  }
  /* Sizes */
  .fr-grid-xl--xxs {
    --fr-grid__size: var(--fr-size__xxs);
  }
  .fr-grid-xl--xs {
    --fr-grid__size: var(--fr-size__xs);
  }
  .fr-grid-xl--sm {
    --fr-grid__size: var(--fr-size__sm);
  }
  .fr-grid-xl--md {
    --fr-grid__size: var(--fr-size__md);
  }
  .fr-grid-xl--lg {
    --fr-grid__size: var(--fr-size__lg);
  }
  .fr-grid-xl--xl {
    --fr-grid__size: var(--fr-size__xl);
  }
  .fr-grid-xl--xxl {
    --fr-grid__size: var(--fr-size__xxl);
  }
}
</style>
