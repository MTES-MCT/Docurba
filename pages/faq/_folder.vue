<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <div class="text-h1 my-8">
          {{ title }}
        </div>
      </v-col>
    </v-row>
    <v-row v-for="qa in FAQ" :id="qa.slug" :key="qa.slug">
      <v-col cols="12">
        <div class="text-h2 text--secondary">
          <a class="text-decoration-none" :href="'#' + qa.slug">{{ qa.question }}</a>
        </div>
      </v-col>
      <v-col cols="12">
        <nuxt-content :document="qa" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import _ from 'lodash'

export default {
  async asyncData ({ $content, route }) {
    const FAQ = await $content(`FAQ/${route.params.folder}`, {
      deep: true
    }).fetch()
    const nullOrderQuestions = FAQ.filter(q => !q.order && q.visible)
    const withOrderQuestions = FAQ.filter(q => q.order && q.visible)
    return {
      FAQ: _.orderBy(withOrderQuestions, ['order'], ['asc']).concat(nullOrderQuestions)
    }
  },
  computed: {
    title () {
      const splitedPath = this.FAQ[0].dir.split('/')
      return splitedPath[splitedPath.length - 1]
    }
  }
}
</script>
