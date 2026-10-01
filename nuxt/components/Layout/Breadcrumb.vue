<script>
import { mdiChevronRight } from '@mdi/js'
export default {
  props: {
    items: {
      default: () => [],
      type: Array
    },
    label: {
      required: true,
      type: String
    }
  },
  data () {
    return {
      icons: {
        mdiChevronRight
      }
    }
  }
}
</script>

<template>
  <ul class="du-layout-breadcrumb">
    <li
      v-for="item in items"
      :key="item.value"
    >
      <NuxtLink :to="item.value">
        {{ item.label }}
      </NuxtLink>
      <VIcon small>
        {{ icons.mdiChevronRight }}
      </VIcon>
    </li>
    <li>{{ label }}</li>
  </ul>
</template>

<style>
ul.du-layout-breadcrumb {
  column-gap: .25rem;
  display: grid;
  grid-auto-flow: column;
  justify-content: start;
  list-style: none;
  padding-left: 0;
}
.du-layout-breadcrumb a {
  box-shadow: inset 0 -.0625rem 0 0 #666;
  color: #666 !important;
  text-decoration: none;
}
.du-layout-breadcrumb a:focus-visible,
.du-layout-breadcrumb a:hover {
  box-shadow: inset 0 -.078125rem 0 0 #666;
}
.du-layout-breadcrumb li {
  align-items: center;
  color: #161616;
  column-gap: .25rem;
  display: grid;
  font-size: .75rem;
  font-weight: 400;
  grid-auto-flow: column;
  line-height: 1.25rem;
}
.du-layout-breadcrumb .v-icon {
  color: #666;
}
</style>
