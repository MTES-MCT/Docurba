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
    value: {
      get () {
        const value = Number(this.$route.query.page)

        return !Number.isNaN(value) && value ? value : 1
      },
      set (newValue) {
        this.$router.push({
          ...this.$route,
          query: {
            ...this.$route.query,
            page: newValue || undefined
          }
        })
      }
    }
  }
}
</script>

<template>
  <div
    v-if="size > 1"
    class="du-pagination"
  >
    <DUActionable
      class="du-pagination__page"
      :disabled="value === 1"
      @actuated="value = 1"
    >
      <VIcon small>
        {{ icons.mdiPageFirst }}
      </VIcon>
    </DUActionable>
    <DUActionable
      class="du-pagination__page"
      :disabled="value === 1"
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
      class="du-pagination__page"
      :class="{
        'du-pagination__page--active': page === value,
        'du-pagination__page--spacer': page === '...'
      }"
      @actuated="value = page === '...' ? value : page"
    >
      {{ page }}
    </DUActionable>
    <DUActionable
      class="du-pagination__page"
      :disabled="value === size"
      @actuated="value = value + 1"
    >
      Suivant
      <VIcon small>
        {{ icons.mdiChevronRight }}
      </VIcon>
    </DUActionable>
    <DUActionable
      class="du-pagination__page"
      :disabled="value === size"
      @actuated="value = size"
    >
      <VIcon small>
        {{ icons.mdiPageLast }}
      </VIcon>
    </DUActionable>
  </div>
</template>

<style>
.du-pagination {
  column-gap: 1rem;
  display: grid;
  grid-auto-flow: column;
  justify-content: end;
}
.du-pagination__page {
  align-items: center;
  color: #161616;
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
}
.du-pagination__page .v-icon {
  color: inherit;
  margin: .25rem -.25rem;
}
.du-pagination__page[disabled] {
  color: #929292;
  cursor: default;
}
.du-pagination__page--active {
  background-color: #000091;
  color: #f5f5fe;
}
.du-pagination__page--spacer {
  cursor: default;
}
</style>
