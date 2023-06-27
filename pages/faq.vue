<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-breadcrumbs class="pb-0 pl-0" :items="breadItems" />
      </v-col>
      <v-col cols="12">
        <h1 class="text-h1">
          Foire aux questions
        </h1>
      </v-col>
    </v-row>
    <v-row>
      <v-col
        v-for="(faqCard, i) in faqCards"
        :key="i"
        cols="12"
        sm="6"
        md="3"
        class="d-flex justify-center"
      >
        <div style="position: relative; display:inline-block;">
          <v-card
            outlined
            tile
            color="white"
            width="200"
            min-height="220"
            class="faq-card"
          >
            <v-img
              contain
              class="mt-4"
              max-height="100"
              :src="faqCard.img"
            />
            <v-card-title class="text-body-1 font-weight-bold text-center justify-center break-word" style="line-height:24px">
              {{ faqCard.title }}
            </v-card-title>
          </v-card>
          <div class="primary bottom-border" />
        </div>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <v-text-field
          v-model="search"
          dense
          label="Rechercher une question"
          filled
          hide-details
          color="primary"
        />
      </v-col>
    </v-row>
    <v-row class="mb-6">
      <v-col cosl="12">
        <v-tabs
          v-model="tab"
          background-color="white"
        >
          <v-tab
            v-for="item in items"
            :key="item.tab"
            class="no-text-transform font-weight-bold white"
          >
            {{ item.tab }}
          </v-tab>
        </v-tabs>

        <v-tabs-items v-model="tab" class="mt-3">
          <v-tab-item

            v-for="item in items"
            :key="item.tab"
          >
            <v-card flat color="white">
              <v-expansion-panels focusable accordion class="pa-1">
                <v-expansion-panel v-for="(q, i) in displayedQuestions" :key="'question-' +i">
                  <v-expansion-panel-header>
                    <h6 class="text-body-1">
                      {{ q.question }}
                    </h6>
                  </v-expansion-panel-header>
                  <v-expansion-panel-content>
                    <nuxt-content :document="q" />
                  </v-expansion-panel-content>
                </v-expansion-panel>
              </v-expansion-panels>
            </v-card>
          </v-tab-item>
        </v-tabs-items>
      </v-col>
    </v-row>

    <!-- <v-row>
      <v-row>
        <v-col cosl="12">
          <v-expansion-panels flat focusable popout>
            <v-expansion-panel v-for="(q, i) in displayedQuestions" :key="'question-' +i">
              <v-expansion-panel-header>
                <h6 class="text-h6">
                  {{ q.question }}
                </h6>
              </v-expansion-panel-header>
              <v-expansion-panel-content>
                <nuxt-content :document="q" />
              </v-expansion-panel-content>
            </v-expansion-panel>
          </v-expansion-panels>
        </v-col>
      </v-row>
    </v-row> -->
  </v-container>
</template>
<script>
export default {
  async asyncData ({ $content }) {
    const FAQ = await $content('FAQ', {
      deep: true
    }).fetch()

    return {
      FAQ: FAQ.filter(q => q.visible)
    }
  },
  data () {
    return {
      tab: null,
      breadItems: [
        {
          text: 'Accueil',
          disabled: false,
          to: '/'

        },
        {
          text: 'Foire aux questions',
          disabled: true,
          href: ''
        }],

      items: [
        { tab: 'Je suis une DDT', content: 'Tab 1 Content' },
        { tab: 'Je suis une collectivité', content: 'Tab 2 Content' },
        { tab: 'Je suis un Bureau d\'étude', content: 'Tab 3 Content' }],
      faqCards: [
        {
          title: 'Qu\'est ce que Docurba ?',
          img: '/images/faq/graph.png',
          link: ''
        },
        {
          title: 'Comment ça fonctionne ?',
          img: '/images/faq/technical-error.png',
          link: ''
        },
        {
          title: 'Premiers pas',
          img: '/images/faq/leaf.png',
          link: ''
        },
        {
          title: 'Contacter l\'équipe',
          img: '/images/faq/community.png',
          link: ''
        }
      ],
      search: this.$route.query.recherche || ''
    }
  },
  computed: {
    filteredQuestions () {
      const searchText = this.search.normalize('NFD').replace(/[\u0300-\u036F]/g, '').toLocaleLowerCase()

      return this.FAQ.filter((q) => {
        const question = q.question.normalize('NFD').replace(/[\u0300-\u036F]/g, '').toLocaleLowerCase()
        return question.includes(searchText)
      })
    },
    displayedQuestions () {
      if (this.search.length) {
        return this.filteredQuestions
      } else { return this.FAQ }
    }
  },
  watch: {
    search () {
      this.$router.replace({ path: '/faq', query: { recherche: this.search } })
    }
  }
}
</script>

<style lang="scss">

</style>
