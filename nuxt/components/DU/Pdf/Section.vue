<script>
export default {
  props: {
    children: {
      default: () => [],
      type: Array
    },
    content: {
      default: '',
      type: String
    },
    depth: {
      default: 2,
      type: Number
    },
    id: {
      default: undefined,
      type: String
    },
    label: {
      default: '',
      type: String
    }
  },
  computed: {
    document () {
      return this.content
        ? {
            body: this.$md.compile(
              this.$md.parse(this.content)
            )
          }
        : ''
    }
  }
}
</script>

<template>
  <div class="du-pdf-section">
    <component
      :is="`h${depth}`"
      :id="id"
    >
      {{ label }}
    </component>
    <NuxtContent
      v-if="document"
      :document="document"
    />
    <template v-if="children.length">
      <DUPdfSection
        v-for="child in children"
        :id="child.id"
        :key="child.path"
        :children="child.children"
        :content="child.content"
        :depth="Math.min(depth + 1, 6)"
        :label="child.label"
      />
    </template>
  </div>
</template>
