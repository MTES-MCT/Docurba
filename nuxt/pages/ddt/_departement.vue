<template>
  <nuxt-child />
</template>

<script>
export default {
  layout: 'ddt',
  async mounted () {
    await this.$user.isReady
    if (!this.$user.canViewSectionCollectivites({ departement: this.$route.params.departement })) {
      console.warn('User is not allowed to view this page.')
      this.$nuxt.context.redirect(302, '/')
    }
  }
}
</script>
