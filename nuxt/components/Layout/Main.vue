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
    primary: {
      default: false,
      type: Boolean
    },
    top: {
      default: '0',
      type: String
    }
  }
}
</script>

<template>
  <div
    class="du-layout-main"
    :class="{ 'du-layout-main--primary': primary }"
  >
    <LayoutHeader
      :breadcrumb="breadcrumb"
      :label="label"
      :primary="primary"
    >
      <template #default>
        <slot name="header" />
      </template>
      <template #infos>
        <slot name="infos" />
      </template>
      <template #actions>
        <slot name="actions" />
      </template>
    </LayoutHeader>
    <div class="du-layout-main__cols">
      <DUSidemenu
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
  background-color: #f6f6f6;
  display: grid;
}
.du-layout-main--primary {
  background-color: #fff;
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
