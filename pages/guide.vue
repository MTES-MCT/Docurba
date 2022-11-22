<template>
  <div class="g100">
    <v-container id="guide">
      <v-row>
        <v-col cols="12">
          <nuxt-content :document="guide" />
        </v-col>
      </v-row>
    </v-container>
  </div>
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

<style lang="scss">
#guide a.anchor {
    display: block;
    position: relative;
    top: -130px;
    visibility: hidden;
}
#guide img{
  display: block;
  max-width: 100%;
   margin-left: auto;
  margin-right: auto;
}

#guide hr{
  display: block;
  height: 1px;
  border: 0;
  border-top: 1px solid black;
  margin: 1em 0;
  padding: 0;
}
</style>
