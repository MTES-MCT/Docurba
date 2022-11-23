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
#guide p{
  margin-bottom:0;
}

#guide h1, h2, h3{
    margin-bottom:24px;
    margin-top:24px;
}

// background--text text--lighten-2 font-weight-bold rounded g300 rounded-lg pa-4
#guide blockquote{
background-color: var(--v-background-base)
}

#guide img{
  display: block;
  max-width: 100%;
  margin-left: auto;
  margin-right: auto;
  margin-top: 24px;
  margin-bottom: 24px;
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
