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
        if (!value) return

        this.frame = await this.$store.dispatch(
          'frame/get',
          this.scope ? { [`${this.scope}Code`]: value } : undefined,
        )
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
    <FRContainer>
      <FRGrid gap="md lg-lg"
              size="md lg-lg">
        <PageDsfrFrameSection v-for="section in frame"
                              :key="section.path"
                              :label="section.label"
                              :path="section.path"
                              :scope="scope"
                              :sections="section.sections" />
      </FRGrid>
    </FRContainer>
  </FRGrid>
</template>
