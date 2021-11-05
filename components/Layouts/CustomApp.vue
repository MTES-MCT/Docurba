<template>
  <div>
    <LayoutsAppBar :extended="extendedAppBar">
      <template #pageTitle>
        <slot name="headerPageTitle" /></slot>
      </template>
      <slot name="headerExtension" />
    </LayoutsAppBar>
    <v-main>
      <slot />
    </v-main>
  </div>
</template>

<script>
export default {
  props: {
    private: {
      type: Boolean,
      default: false
    },
    extendedAppBar: {
      type: Boolean,
      default: false
    }
  },
  watch: {
    '$user.id' () {
      this.redirectUser()
    }
  },
  mounted () {
    this.redirectUser()
  },
  methods: {
    redirectUser () {
      if (process.client && this.private && !this.$user.id) {
        this.$router.push('/')
      }
    }
  }
}
</script>
