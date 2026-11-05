<script>
export default {
  props: {
    scope: {
      default: '',
      type: String,
    },
  },
  data() {
    return {
      frame: [],
      loading: true,
    }
  },
  computed: {
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
    label() {
      switch (this.scope) {
        case 'department':
          return 'Trame départementale'
        case 'region':
          return 'Trame régionale'
        default:
          return 'Trame nationale'
      }
    },
  },
  watch: {
    code: {
      async handler(value) {
        this.loading = true

        try {
          this.frame = await this.$store.dispatch(
            'frame/get',
            this.scope ? { [`${this.scope}Code`]: value } : undefined,
          )
        } catch {
          this.frame = []
        }

        this.loading = false
      },
      immediate: true,
    },
  },
}
</script>

<template>
  <FRGrid alt>
    <FRHighlight alt>
      <FRContainer>
        <FRGrid gap="md lg-lg"
                size="md lg-xl">
          <FRText h1
                  tag="h1">
            {{ label }}
          </FRText>
        </FRGrid>
      </FRContainer>
    </FRHighlight>
    <FRContainer v-if="!loading">
      <FRGrid gap="md lg-lg"
              size="md lg-lg">
        <template v-if="frame.length">
          <PageDsfrFrameSection v-for="section in frame"
                                :key="section.path"
                                :label="section.label"
                                :path="section.path"
                                :scope="scope"
                                :sections="section.sections" />
        </template>
        <FRText v-else
                center>
          Cette trame est vide
        </FRText>
      </FRGrid>
    </FRContainer>
  </FRGrid>
</template>
