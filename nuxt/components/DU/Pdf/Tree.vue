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
  <ol class="du-pdf-tree">
    <li
      v-for="item in value"
      :key="item.path"
    >
      <a :href="`#${item.id}`">
        {{ item.label }}
      </a>
      <DUPdfTree
        v-if="item.children.length"
        :value="item.children"
      />
    </li>
  </ol>
</template>

<style>
.du-pdf > .du-pdf-tree {
  padding-left: 0;
}
.du-pdf ol.du-pdf-tree {
  margin-bottom: 0;
}
.du-pdf-tree {
  display: grid;
  list-style: none;
  row-gap: 10pt;
}
.du-pdf-tree li {
  display: grid;
  justify-items: start;
  row-gap: 10pt;
}
</style>
