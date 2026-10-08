<script>
import { mdiChevronLeft, mdiChevronRight, mdiPageFirst, mdiPageLast } from '@mdi/js'

export default {
  props: {
    size: {
      default: 0,
      type: Number
    }
  },
  data () {
    return {
      icons: {
        mdiChevronLeft,
        mdiChevronRight,
        mdiPageFirst,
        mdiPageLast
      }
    }
  },
  computed: {
    pages () {
      if (this.size < 2) {
        return []
      }
      if (this.size < 8) {
        return Array.from({ length: this.size }, (_, i) => i + 1)
      }

      const pages = [1]

      if (this.value - 2 > 2) {
        pages.push('...')
      }
      pages.push(
        Math.min(Math.max(this.value - 2, 2), this.size - 5),
        Math.min(Math.max(this.value - 1, 3), this.size - 4),
        Math.min(Math.max(this.value, 4), this.size - 3),
        Math.min(Math.max(this.value + 1, 5), this.size - 2),
        Math.min(Math.max(this.value + 2, 6), this.size - 1)
      )
      if (this.value + 2 < this.size - 1) {
        pages.push('...')
      }

      pages.push(this.size)

      return pages
    },
    value () {
      const value = Number(this.$route.query.page)

      return !Number.isNaN(value) && value ? value : 1
    }
  },
  watch: {
    value () {
      window.scrollTo({ top: 0 })
    }
  }
}
</script>

<template>
  <div
    v-if="size > 1"
    class="du-layout-pagination"
  >
    <DUActionable
      class="du-layout-pagination__page"
      :disabled="value === 1"
      :to="{
        query: {
          ...$route.query,
          page: undefined
        }
      }"
    >
      <VIcon small>
        {{ icons.mdiPageFirst }}
      </VIcon>
    </DUActionable>
    <DUActionable
      class="du-layout-pagination__page"
      :disabled="value === 1"
      :to="{
        query: {
          ...$route.query,
          page: value - 1 === 1 ? undefined : value - 1
        }
      }"
      @actuated="value = value - 1"
    >
      <VIcon small>
        {{ icons.mdiChevronLeft }}
      </VIcon>
      Précédent
    </DUActionable>
    <DUActionable
      v-for="page, index in pages"
      :key="index"
      class="du-layout-pagination__page"
      :class="{
        'du-layout-pagination__page--active': page === value,
        'du-layout-pagination__page--spacer': page === '...'
      }"
      :disabled="['...', value].includes(page)"
      :to="{
        query: {
          ...$route.query,
          page: page === 1 ? undefined : page
        }
      }"
    >
      {{ page }}
    </DUActionable>
    <DUActionable
      class="du-layout-pagination__page"
      :disabled="value === size"
      :to="{
        query: {
          ...$route.query,
          page: value + 1
        }
      }"
    >
      Suivant
      <VIcon small>
        {{ icons.mdiChevronRight }}
      </VIcon>
    </DUActionable>
    <DUActionable
      class="du-layout-pagination__page"
      :disabled="value === size"
      :to="{
        query: {
          ...$route.query,
          page: size
        }
      }"
    >
      <VIcon small>
        {{ icons.mdiPageLast }}
      </VIcon>
    </DUActionable>
  </div>
</template>

<style>
.du-layout-pagination {
  column-gap: 1rem;
  display: grid;
  grid-auto-flow: column;
  justify-content: center;
  margin-top: 1rem;
}
.du-layout-pagination__page {
  align-items: center;
  color: #161616 !important;
  column-gap: .75rem;
  cursor: pointer;
  display: grid;
  font-size: .875rem;
  font-weight: 500;
  grid-auto-flow: column;
  line-height: 1.5rem;
  min-width: 2rem;
  padding: .25rem .75rem;
  text-align: center;
  text-decoration: none;
}
.du-layout-pagination__page .v-icon {
  color: inherit;
  margin: .25rem -.25rem;
}
.du-layout-pagination__page:not([disabled]):focus-visible,
.du-layout-pagination__page:not([disabled]):hover {
  background-color: #f6f6f6;
}
.du-layout-pagination__page[disabled] {
  color: #929292 !important;
  cursor: default;
}
.du-layout-pagination__page--active[disabled] {
  background-color: #000091;
  color: #f5f5fe !important;
}
.du-layout-pagination__page--spacer {
  cursor: default;
}
</style>
