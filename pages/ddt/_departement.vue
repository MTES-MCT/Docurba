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

    if (routerDept !== userDept) {
      this.$router.push({ params: { departement: userDept } })
    }
  }
}
</script>
