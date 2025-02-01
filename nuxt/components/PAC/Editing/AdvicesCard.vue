<template>
  <v-card v-show="currentAdvice" flat outlined color="info" dark>
    <v-card-text>
      <nuxt-content class="white--text" :document="currentAdvice" />
    </v-card-text>
    <v-card-actions>
      <v-spacer />
      <v-btn color="white" outlined @click="markAsRed(currentAdvice)">
        {{ (advices.length-1) > displayedAdvices ? 'suivant' : 'terminer' }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
const storageKey = 'docurba_PAC_advices'

export default {
  props: {
    avoidedTags: {
      type: Array,
      default () { return [] }
    }
  },
  data () {
    return {
      advices: [],
      displayedAdvices: []
    }
  },
  computed: {
    currentAdvice () {
      return this.advices.find((advice) => {
        return !this.displayedAdvices.includes(`${this.$route.path} - ${advice.name}`)
      })
    }
  },
  async mounted () {
    this.displayedAdvices = JSON.parse(localStorage.getItem(storageKey)) || []
    const advices = await this.$content('PAC_Advices', {
      deep: true
    }).fetch()

    this.advices = advices.filter(advice => !this.avoidedTags.includes(advice.tag) && advice.visible !== false)
  },
  methods: {
    markAsRed (advice) {
      this.displayedAdvices.push(`${this.$route.path} - ${advice.name}`)
      localStorage.setItem(storageKey, JSON.stringify(this.displayedAdvices))
    }
  }
}
</script>
