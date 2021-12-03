<template>
  <nuxt />
</template>

<script>
export default {
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
