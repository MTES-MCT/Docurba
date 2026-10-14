<script>
export default {
  props: {
    label: {
      default: '',
      type: String
    },
    towns: {
      default: () => [],
      type: Array
    },
    value: {
      default: false,
      type: Boolean
    }
  },
  computed: {
    model: {
      get () {
        return this.value
      },
      set (newValue) {
        this.$emit('input', newValue)
      }
    }
  }
}
</script>

<template>
  <div>
    <DULink @actuated="model = true">
      <slot />
    </DULink>
    <DUDialog v-model="model">
      <DUHeading :level="3">
        <div>{{ label }}</div>
        <div>
          <strong>
            <slot />
          </strong>
        </div>
      </DuHeading>
      <DULinksList>
        <DULink
          v-for="town in towns"
          :key="town.code"
          :to="{
            params: {
              code_collectivite: town.code
            },
            query: {
              vue: $route.query.vue
            }
          }"
        >
          {{ town.name }} ({{ town.code }})
        </DULink>
      </DULinksList>
    </DUDialog>
  </div>
</template>
