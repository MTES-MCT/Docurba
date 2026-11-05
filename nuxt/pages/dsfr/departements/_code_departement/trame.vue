<script>
export default {
  data() {
    return {
      frame: [],
    }
  },
  computed: {
    departmentCode() {
      return this.$route.params.code_departement || null
    },
  },
  watch: {
    departmentCode: {
      async handler(value) {
        if (!value) return

        this.frame = await this.$store.dispatch('frame/getForDepartment', value)
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
            Trame départementale
          </FRText>
        </FRGrid>
      </FRContainer>
    </FRHighlight>
    <FRContainer>
      <FRGrid gap="md lg-lg"
              size="md lg-lg">
        <PageDsfrDepartmentFrameSection v-for="section in frame"
                                        :key="section.path"
                                        :content="section.content"
                                        :label="section.label"
                                        :path="section.path"
                                        :sections="section.sections" />
      </FRGrid>
    </FRContainer>
  </FRGrid>
</template>
