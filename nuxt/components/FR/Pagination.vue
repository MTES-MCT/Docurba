<script>
import { mdiChevronLeft, mdiChevronRight, mdiPageFirst, mdiPageLast } from '@mdi/js'

export default {
  props: {
    value: {
      default: 0,
      type: Number,
    },
  },
  data() {
    return {
      icons: {
        mdiChevronLeft,
        mdiChevronRight,
        mdiPageFirst,
        mdiPageLast,
      },
    }
  },
  computed: {
    items() {
      if (this.value < 2) {
        return []
      }

      const isOptional = this.page === 1
        ? (item) => item > 3
        : this.page === this.value
          ? (item) => item < this.value - 2
          : (item) => item < this.page - 1 || item > this.page + 1

      if (this.value < 8) {
        return Array.from({ length: this.value }, (_, i) => i + 1).map((item) => ({
          optional: item === '...' || isOptional(item),
          value: item,
        }))
      }

      const items = [1]

      if (this.page - 2 > 2) {
        items.push('...')
      }

      items.push(
        Math.min(Math.max(this.page - 2, 2), this.value - 5),
        Math.min(Math.max(this.page - 1, 3), this.value - 4),
        Math.min(Math.max(this.page, 4), this.value - 3),
        Math.min(Math.max(this.page + 1, 5), this.value - 2),
        Math.min(Math.max(this.page + 2, 6), this.value - 1),
      )

      if (this.page + 2 < this.value - 1) {
        items.push('...')
      }

      items.push(this.value)

      return items.map((item) => ({
        optional: item === '...' || isOptional(item),
        value: item,
      }))
    },
    page() {
      const pageNumber = Number(this.$route.query.page)
      const page = (!Number.isNaN(pageNumber) && pageNumber) || 1

      return page > this.value ? this.value : page
    },
  },
  watch: {
    page() {
      window.scrollTo({ top: 0 })
    },
  },
}
</script>

<template>
  <div v-if="value > 1"
       class="fr-pagination">
    <FRActionable class="fr-pagination__item"
                  :disabled="page === 1"
                  :to="{
                    query: {
                      ...$route.query,
                      page: undefined,
                    },
                  }">
      <FRIcon :value="icons.mdiPageFirst" />
    </FRActionable>
    <FRActionable class="fr-pagination__item"
                  :disabled="page === 1"
                  :to="{
                    query: {
                      ...$route.query,
                      page: page - 1 === 1 ? undefined : page - 1,
                    },
                  }">
      <FRIcon :value="icons.mdiChevronLeft" />
      <div class="fr-pagination__label">
        Précédent
      </div>
    </FRActionable>
    <FRActionable v-for="item, index in items"
                  :key="index"
                  class="fr-pagination__item"
                  :class="{
                    'fr-pagination__item--active': item.value === page,
                    'fr-pagination__item--optional': item.optional,
                    'fr-pagination__item--spacer': item.value === '...',
                  }"
                  :disabled="['...', page].includes(item.value)"
                  :to="{
                    query: {
                      ...$route.query,
                      page: item.value === 1 ? undefined : item.value,
                    },
                  }">
      {{ item.value }}
    </FRActionable>
    <FRActionable class="fr-pagination__item"
                  :disabled="page === value"
                  :to="{
                    query: {
                      ...$route.query,
                      page: page + 1,
                    },
                  }">
      <div class="fr-pagination__label">
        Suivant
      </div>
      <FRIcon :value="icons.mdiChevronRight" />
    </FRActionable>
    <FRActionable class="fr-pagination__item"
                  :disabled="page === value"
                  :to="{
                    query: {
                      ...$route.query,
                      page: value,
                    },
                  }">
      <FRIcon :value="icons.mdiPageLast" />
    </FRActionable>
  </div>
</template>

<style>
.fr-pagination {
  column-gap: 1rem;
  display: grid;
  grid-auto-flow: column;
  justify-content: center;
}
.fr-pagination__item {
  background-color: var(--fr-color__grey-1000-50);
  color: var(--fr-color__grey-50-1000);
  column-gap: .75rem;
  cursor: pointer;
  display: grid;
  font-size: .875rem;
  font-weight: 400;
  grid-auto-flow: column;
  justify-content: center;
  line-height: 1.5rem;
  min-width: 2rem;
  padding: .25rem .75rem;
  text-decoration: none;
}
.fr-pagination__item .fr-icon {
  --fr-icon__size: 1rem;

  margin: .25rem -.25rem;
}
.fr-pagination__item:not([disabled]):focus-visible,
.fr-pagination__item:not([disabled]):hover {
  background-color: var(--fr-color__grey-1000-50--hover);
}
.fr-pagination__item[disabled] {
  color: var(--fr-color__grey-625-425);
  cursor: not-allowed;
}
.fr-pagination__item--active[disabled] {
  background-color: var(--fr-color__blue-france-sun-113-625);
  color: var(--fr-color__blue-france-975-sun-113);
  cursor: default;
}
.fr-pagination__item--optional,
.fr-pagination__label {
  display: none;
}
.fr-pagination__item--spacer[disabled] {
  color: var(--fr-color__grey-50-1000);
  cursor: default;
}

@media (min-width: 48rem) {
  .fr-pagination__item--optional,
  .fr-pagination__label {
    display: grid;
  }
}
</style>
