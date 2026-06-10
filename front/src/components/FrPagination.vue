<script setup lang="ts">
import { computed } from 'vue'
import type { RouteLocationRaw } from 'vue-router'
import { useRoute } from 'vue-router'
import BaseActionable from '@/components/BaseActionable.vue'
import { useRouteQueryParam } from '@/composables/useRouteQueryParam'

interface Props {
  size: number
}

const {
  size,
} = defineProps<Props>()

const route = useRoute()

const currentPage = useRouteQueryParam<number>('page', {
  fromQuery: (query) => {
    const number = Number(query)

    return Number.isNaN(number) ? 1 : number
  },
  toQuery: (value) => value === 1 ? undefined : String(value),
})

const firstVisiblePage = computed<number>(() =>
  Math.max(Math.min(currentPage.value - 2, size - 4), 1)
)
const pages = computed<Array<{
  number: number
  to: RouteLocationRaw | undefined
}>>(() => (
  size < 7
    ? Array.from(Array(size).keys())
    : [
      firstVisiblePage.value,
      firstVisiblePage.value + 1,
      firstVisiblePage.value + 2,
      firstVisiblePage.value + 3,
      firstVisiblePage.value + 4,
    ]
).map((number) => ({
  number,
  to: toPage.value(number),
})))
const toFirstPage = computed<RouteLocationRaw | undefined>(() =>
  toPage.value(1)
)
const toNextPage = computed<RouteLocationRaw | undefined>(() =>
  toPage.value(currentPage.value + 1)
)
const toLastPage = computed<RouteLocationRaw | undefined>(() =>
  toPage.value(size)
)
const toPage = computed<(page: number) => RouteLocationRaw | undefined>(() =>
  (page: number) =>
    page === currentPage.value || page < 1 || page > size
      ? undefined
      : {
        ...route,
        query: {
          ...route.query,
          page,
        },
      }
)
const toPrevPage = computed<RouteLocationRaw | undefined>(() =>
  toPage.value(currentPage.value - 1)
)
</script>

<template>
  <nav aria-label="Pagination"
       class="fr-pagination"
       role="navigation">
    <ul class="fr-pagination__list">
      <li>
        <BaseActionable class="fr-pagination__link fr-icon--before fr-icon--before-arrow-left-s-first-line"
                        :disabled="!toFirstPage"
                        :to="toFirstPage">Première page</BaseActionable>
      </li>
      <li>
        <BaseActionable class="fr-pagination__link fr-icon--before fr-icon--before-arrow-left-s-line"
                        :disabled="!toPrevPage"
                        :to="toPrevPage">Page précédente</BaseActionable>
      </li>
      <li v-for="{ number, to } in pages"
          :key="number">
        <BaseActionable class="fr-pagination__link"
                        :class="{ 'fr-pagination__link--active': number === currentPage }"
                        :disabled="!to"
                        :to="to">{{ number }}</BaseActionable>
      </li>
      <li>
        <BaseActionable class="fr-pagination__link fr-icon--after fr-icon--after-arrow-right-s-line"
                        :disabled="!toNextPage"
                        :to="toNextPage">Page suivante</BaseActionable>
      </li>
      <li>
        <BaseActionable class="fr-pagination__link fr-icon--after fr-icon--after-arrow-right-s-last-line"
                        :disabled="!toLastPage"
                        :to="toLastPage">Dernière page</BaseActionable>
      </li>
    </ul>
  </nav>
</template>

<style>
.fr-pagination {
  display: grid;
  justify-content: center;
}
.fr-pagination li {
  display: grid;
}
.fr-pagination__link {
  align-items: center;
  color: var(--color-grey-200-850);
  column-gap: .5rem;
  display: grid;
  font-family: var(--font-family-sans);
  font-size: .875rem;
  font-weight: 400;
  grid-auto-flow: column;
  line-height: 1.5rem;
  min-width: 2rem;
  padding: .25rem .75rem;
  text-align: center;
  text-decoration: none;
}
.fr-pagination__link[disabled] {
  color: var(--color-grey-625-425);
  cursor: default;
}
.fr-pagination__link:not([disabled]):focus,
.fr-pagination__link:not([disabled]):hover {
  background-color: var(--color-grey-1000-50-hover);
}
.fr-pagination__link--active[disabled] {
  background-color: var(--color-blue-france-sun-113-625);
  color: var(--color-blue-france-975-sun-113);
}
.fr-pagination__link.fr-icon--before,
.fr-pagination__link.fr-icon--after {
  height: 2rem;
  overflow: hidden;
  padding-left: .25rem;
  padding-right: .25rem;
  white-space: nowrap;
  width: 2rem;
}
.fr-pagination__link.fr-icon--before {
  justify-content: start;
}
.fr-pagination__link.fr-icon--after {
  justify-content: end;
}
.fr-pagination__link.fr-icon--before::before,
.fr-pagination__link.fr-icon--after::after {
  margin: .25rem;
}
.fr-pagination__list {
  column-gap: 1rem;
  display: grid;
  grid-auto-flow: column;
  list-style: none;
  margin-bottom: 0;
  margin-top: 0;
  padding-left: 0;
}
</style>
