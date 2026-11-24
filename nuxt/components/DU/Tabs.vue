<script>
export default {
  props: {
    value: {
      default: () => [],
      type: Array
    }
  }
}
</script>

<template>
  <div class="du-tabs">
    <div class="du-tabs__header">
      <DUActionable
        v-for="item, index in value"
        :key="index"
        class="du-tabs__tab"
        :class="{ 'du-tabs__tab--active': item.active }"
        :to="item.to"
      >
        {{ item.label }}
      </DUActionable>
    </div>
    <div class="du-tabs__body">
      <slot />
    </div>
  </div>
</template>

<style>
.du-tabs {
  display: grid;
}
.du-tabs__body {
  background-color: #fff;
  box-shadow: inset 0 0 0 .0625rem #ddd;
  padding: 1rem;
}
.du-tabs__header {
  column-gap: .5rem;
  display: grid;
  grid-auto-flow: column;
  justify-content: start;
  padding-left: 1rem;
  padding-right: 1rem;
}
.du-tabs__tab {
  background-color: #e3e3fd;
  color: #161616;
  font-size: 1rem;
  font-weight: 700;
  line-height: 1.5rem;
  padding: .5rem 1rem;
  text-decoration: none;
}
.du-tabs__tab:not(.du-tabs__tab--active):focus-visible,
.du-tabs__tab:not(.du-tabs__tab--active):hover {
  background-color: #c1c1fb;
}
.du-tabs__tab--active {
  background-color: #fff;
  box-shadow: inset 0 .125rem 0 0 #000091,
              inset .0625rem 0 0 0 #ddd,
              inset -.0625rem 0 0 0 #ddd,
              inset 0 -.0625rem 0 0 #fff;
  color: #000091;
  margin-bottom: -.0625rem;
  padding-bottom: .5625rem;
  position: relative;
}
</style>
