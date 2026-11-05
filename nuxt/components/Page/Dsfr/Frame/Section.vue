<script>
import { mdiChevronDown, mdiChevronUp } from '@mdi/js'

export default {
  props: {
    label: {
      default: '',
      type: String,
    },
    path: {
      default: '',
      type: String,
    },
    scope: {
      default: '',
      type: String,
    },
    sections: {
      default: () => [],
      type: Array,
    },
  },
  data() {
    return {
      content: '',
      contentLoaded: false,
      icons: {
        mdiChevronDown,
        mdiChevronUp,
      },
    }
  },
  computed: {
    active: {
      get() {
        return (
          this.$route.query.chemin
          && (
            this.path === this.$route.query.chemin
            || this.$route.query.chemin.startsWith(`${this.path}/`)
          )
        )
      },
      set(value) {
        this.$router.push({
          query: {
            ...this.$route.query,
            chemin: value ? this.path : this.closedPath,
          },
        })
      }
    },
    closedPath() {
      return this.path.split('/').slice(0, -1).join('/') || undefined
    },
    code() {
      switch (this.scope) {
        case 'department':
          return this.$route.params.code_departement || null
        case 'region':
          return this.$route.params.code_region || null
        default:
          return null
      }
    },
    exactActive() {
      return this.path === this.$route.query.chemin
    },
  },
  watch: {
    contentLoaded(value) {
      if (!value || !this.exactActive) return

      this.scrollToTop()
    },
    exactActive(value) {
      if (!value) return

      this.scrollToTop()
    },
    path: {
      async handler(value) {
        if (!value) return

        const params = { path: value }

        if (this.scope) {
          params[`${this.scope}Code`] = this.code
        }

        this.content = await this.$store.dispatch('frame/getContent', params)
        this.contentLoaded = true
      },
      immediate: true,
    },
  },
  mounted() {
    if (!this.contentLoaded || !this.exactActive) return

    this.scrollToTop()
  },
  methods: {
    async scrollToTop() {
      if (!this.$el) return

      await this.$nextTick()

      window.scrollTo({
        behavior: 'smooth',
        top: (
          this.$el.getBoundingClientRect().top
          + window.pageYOffset
          - document.querySelector('.fr-header').clientHeight
        ),
      })
    },
  },
}
</script>

<template>
  <FRAccordion card
               :label="label"
               v-model="active">
    <FRGrid v-if="active && contentLoaded"
            gap="md lg-lg">
      <FRMarkdown v-if="content"
                  :value="content" />
      <PageDsfrFrameSection v-for="section in sections"
                            :key="section.path"
                            :label="section.label"
                            :path="section.path"
                            :scope="scope"
                            :sections="section.sections" />
    </FRGrid>
  </FRAccordion>
</template>
