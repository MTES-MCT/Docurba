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
    primary: {
      default: false,
      type: Boolean
    }
  }
}
</script>

<template>
  <div
    class="du-layout-header"
    :class="{ 'du-layout-header--primary': primary }"
  >
    <div class="du-layout-header__body">
      <DUBreadcrumb
        v-if="breadcrumb.length"
        :items="breadcrumb"
        :label="label"
      />
      <DUGroup xs>
        <h1 class="du-layout-header__heading">
          {{ label }}
        </h1>
        <p
          v-if="$slots.default"
          class="du-layout-header__description"
        >
          <slot />
        </p>
      </DUGroup>
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
  background-color: #fff;
  box-shadow: inset 0 -.0625rem 0 0 #ddd;
  display: grid;
  padding: 2rem 1.5rem;
}
.du-layout-header--primary {
  background-color: #f5f5fe;
  box-shadow: none;
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
.du-layout-header__description {
  color: #000 !important;
  font-size: 1.375rem;
  font-weight: 400;
  line-height: 1.75rem;
  margin-bottom: 0 !important;
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
