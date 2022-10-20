<template>
  <nuxt-content :document="guide" />
</template>

<script>
export default {
  async asyncData ({ $content }) {
    const guide = await $content('Guide', {
      deep: true
    }).fetch()

    return {
      guide: guide[0]
    }
  }
}
</script>
