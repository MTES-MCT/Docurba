<script>
export default {
  props: {
    breadcrumb: {
      default: () => [],
      type: Array
    },
    label: {
      default: '',
      type: String
    },
    menu: {
      default: () => [],
      type: Array
    },
    top: {
      default: '0',
      type: String
    }
  }
}
</script>

<template>
  <div class="du-layout-main">
    <LayoutHeader
      :breadcrumb="breadcrumb"
      :label="label"
    >
      <template #infos>
        <slot name="infos" />
      </template>
      <template #actions>
        <slot name="actions" />
      </template>
    </LayoutHeader>
    <div class="du-layout-main__cols">
      <LayoutSidemenu
        v-if="menu.length"
        :top="top"
        :value="menu"
      />
      <div class="du-layout-main__body">
        <slot />
      </div>
    </div>
  </div>
</template>

<style>
.du-layout-main {
  display: grid;
}
.du-layout-main__body {
  align-items: start;
  display: grid;
  row-gap: 1.5rem;
}
.du-layout-main__cols {
  column-gap: 2.5rem;
  display: grid;
  grid-auto-columns: auto 1fr;
  grid-auto-flow: column;
  margin-left: auto;
  margin-right: auto;
  max-width: 78rem;
  padding: 1.5rem;
  width: 100%;
}
</style>
