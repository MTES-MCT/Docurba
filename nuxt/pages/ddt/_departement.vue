<template>
  <nuxt-child />
</template>

<script>
export default {
  layout: 'ddt',
  async mounted () {
    await this.$user.isReady

    const routerDept = this.$route.params.departement
    const userDept = this.$user.profile.departement

    if (routerDept !== userDept && !this.$user.profile?.is_admin) {
      this.$router.push({ params: { departement: userDept } })
    }

    if (!this.$user.canViewSectionCollectivites()) {
      console.warn('User is not allowed to view this page.')
      this.$router.push('/')
    }
  }
}
</script>
