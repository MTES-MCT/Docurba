<template>
  <v-app>
    <v-navigation-drawer v-if="drawer" app clipped :permanent="drawer">
      <slot name="drawer" />
    </v-navigation-drawer>

    <LayoutsAppBar :extended="extendedAppBar">
      <template #pageTitle>
        <slot name="headerPageTitle" />
      </template>
      <slot name="headerExtension" />
    </LayoutsAppBar>
    <v-main>
      <slot />
    </v-main>
    <!-- <LayoutsFooter /> -->
  </v-app>
</template>

<script>
export default {
  props: {
    private: {
      type: Boolean,
      default: false
    },
    drawer: {
      type: Boolean,
      default: false
    },
    extendedAppBar: {
      type: Boolean,
      default: false
    }
  }
}
</script>
