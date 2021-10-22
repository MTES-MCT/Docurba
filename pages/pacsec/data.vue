<template>
  <DataSourcesList :region="currentRegion" />
</template>

<script>
export default {
  computed: {
    currentRegion () {
      return this.$route.query.region
    }
  }
}
</script>
