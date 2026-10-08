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
    }
  }
}
</script>

<template>
  <div class="du-layout-header">
    <div class="du-layout-header__body">
      <LayoutBreadcrumb
        v-if="breadcrumb.length"
        :items="breadcrumb"
        :label="label"
      />
      <h1 class="du-layout-header__heading">
        {{ label }}
      </h1>
      <div
        v-if="$slots.actions || $slots.infos"
        class="du-layout-header__footer"
      >
        <DUDottedList v-if="$slots.infos">
          <slot name="infos" />
        </DUDottedList>
        <div
          v-if="$slots.actions"
          class="du-layout-header__actions"
        >
          <slot name="actions" />
        </div>
      </div>
    </div>
  </div>
</template>

<style>
.du-layout-header {
  background-color: #f5f5fe;
  display: grid;
  padding: 2rem 1.5rem;
}
.du-layout-header__actions {
  column-gap: 1rem;
  display: grid;
  grid-auto-flow: column;
}
.du-layout-header__body {
  display: grid;
  margin-left: auto;
  margin-right: auto;
  max-width: 75rem;
  row-gap: 1rem;
  width: 100%;
}
.du-layout-header__footer {
  align-items: center;
  display: grid;
  grid-auto-flow: column;
  justify-content: space-between;
  margin-top: .5rem;
}
h1.du-layout-header__heading {
  color: #000 !important;
  font-size: 2.5rem;
  font-weight: 800;
  line-height: 3rem;
}
</style>
