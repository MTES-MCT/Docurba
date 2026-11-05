<script>
export default {
  props: {
    display: {
      default: false,
      type: Boolean,
    },
    light: {
      default: false,
      type: Boolean,
    },
    mention: {
      default: false,
      type: Boolean,
    },
    rows: {
      default: 0,
      type: Number,
    },
    tag: {
      default: 'p',
      type: String,
    },
    // Alignments
    center: {
      default: false,
      type: Boolean,
    },
    end: {
      default: false,
      type: Boolean,
    },
    // Headings
    h1: {
      default: false,
      type: Boolean,
    },
    h2: {
      default: false,
      type: Boolean,
    },
    h3: {
      default: false,
      type: Boolean,
    },
    h4: {
      default: false,
      type: Boolean,
    },
    h5: {
      default: false,
      type: Boolean,
    },
    h6: {
      default: false,
      type: Boolean,
    },
    // Sizes
    lg: {
      default: false,
      type: Boolean,
    },
    md: {
      default: false,
      type: Boolean,
    },
    sm: {
      default: false,
      type: Boolean,
    },
    xl: {
      default: false,
      type: Boolean,
    },
    xs: {
      default: false,
      type: Boolean,
    },
  },
}
</script>

<template>
  <component :is="tag"
             class="fr-text"
             :class="{
               'fr-text--center': center,
               'fr-text--display': display,
               'fr-text--ellipsis': !!rows,
               'fr-text--end': end,
               'fr-text--h1': h1,
               'fr-text--h2': h2,
               'fr-text--h3': h3,
               'fr-text--h4': h4,
               'fr-text--h5': h5,
               'fr-text--h6': h6,
               'fr-text--light': light,
               'fr-text--lg': lg,
               'fr-text--md': display && md,
               'fr-text--mention': mention,
               'fr-text--sm': sm,
               'fr-text--xl': xl,
               'fr-text--xs': xs,
             }"
             :style="rows ? { '--fr-text__rows': rows } : undefined">
    <slot />
  </component>
</template>

<style>
.fr-text {
  --fr-text__line: 1.5rem;
  --fr-text__size: 1rem;

  color: var(--fr-color__grey-200-850);
  font-size: var(--fr-text__size);
  font-weight: 400;
  line-height: var(--fr-text__line);
}
.fr-text > .fr-link {
  color: inherit;
  column-gap: .25rem;
  display: inline-grid;
  font-size: inherit;
  line-height: inherit;
}
.fr-text--display,
.fr-text--h1,
.fr-text--h2,
.fr-text--h3,
.fr-text--h4,
.fr-text--h5,
.fr-text--h6 {
  color: var(--fr-color__grey-50-1000) !important;
  font-weight: 700;
}
.fr-text--display.fr-text--light,
.fr-text--h1.fr-text--light,
.fr-text--h2.fr-text--light,
.fr-text--h3.fr-text--light,
.fr-text--h4.fr-text--light,
.fr-text--h5.fr-text--light,
.fr-text--h6.fr-text--light {
  font-weight: 400;
}
.fr-text--ellipsis {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: var(--fr-text__rows);
  line-clamp: var(--fr-text__rows);
  max-height: calc(var(--fr-text__rows) * var(--fr-text__line));
  overflow: hidden;
}
.fr-text--mention {
  color: var(--fr-color__grey-425-625);
}
/* Alignments */
.fr-text--center {
  text-align: center;
}
.fr-text--end {
  text-align: right;
}
/* Headings */
.fr-text--h1 {
  --fr-text__line: 3rem;
  --fr-text__size: 2.5rem;
}
.fr-text--h2 {
  --fr-text__line: 2.5rem;
  --fr-text__size: 2rem;
}
.fr-text--h3 {
  --fr-text__line: 2.25rem;
  --fr-text__size: 1.75rem;
}
.fr-text--h4 {
  --fr-text__line: 2rem;
  --fr-text__size: 1.5rem;
}
.fr-text--h5 {
  --fr-text__line: 1.75rem;
  --fr-text__size: 1.375rem;
}
.fr-text--h6 {
  --fr-text__line: 1.75rem;
  --fr-text__size: 1.25rem;
}
/* Sizes */
.fr-text--display.fr-text--lg {
  --fr-text__line: 5rem;
  --fr-text__size: 4.5rem;
}
.fr-text--display.fr-text--md {
  --fr-text__line: 4.5rem;
  --fr-text__size: 4rem;
}
.fr-text--display.fr-text--sm {
  --fr-text__line: 4rem;
  --fr-text__size: 3.5rem;
}
.fr-text--display.fr-text--xl {
  --fr-text__line: 5.5rem;
  --fr-text__size: 5rem;
}
.fr-text--display.fr-text--xs {
  --fr-text__line: 4.5rem;
  --fr-text__size: 4rem;
}
.fr-text--lg {
  --fr-text__line: 1.625rem;
  --fr-text__size: 1.125rem;
}
.fr-text--sm {
  --fr-text__line: 1.5rem;
  --fr-text__size: .875rem;
}
.fr-text--xl {
  --fr-text__line: 2rem;
  --fr-text__size: 1.25rem;
}
.fr-text--xs {
  --fr-text__line: 1.25rem;
  --fr-text__size: .75rem;
}
</style>
