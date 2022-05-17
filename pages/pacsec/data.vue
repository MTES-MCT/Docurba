<template>
  <DataSourcesList :region="currentRegion" :data-sources="dataset" :themes="themes" />
</template>

<script>
export default {
  async asyncData ({ $daturba }) {
    return await $daturba.getData()
  },
  data () {
    return {
      dataset: [],
      themes: []
    }
  },
  computed: {
    currentRegion () {
      return this.$route.query.region
    }
  }
}
</script>
