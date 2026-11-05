<script>
import { mdiChevronDown, mdiChevronUp } from '@mdi/js'

export default {
  props: {
    content: {
      default: '',
      type: String,
    },
    label: {
      default: '',
      type: String,
    },
    path: {
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
      icons: {
        mdiChevronDown,
        mdiChevronUp,
      },
    }
  },
  computed: {
    active() {
      return (
        this.$route.query.chemin
        && this.$route.query.chemin.startsWith(this.path)
      )
    },
    closedPath() {
      return this.path.split('/').slice(0, -1).join('/')
    },
    to() {
      return {
        query: {
          ...this.$route.query,
          chemin: this.active
            ? this.closedPath === '/'
              ? undefined
              : this.closedPath
            : this.path,
        },
      }
    },
  },
}
</script>

<template>
  <FRCard>
    <FRGrid gap="md lg-lg">
      <FRButton between
                :disabled="!content && !sections.length"
                lg
                tertiary-borderless
                :to="to">
        {{ label }}
        <FRIcon v-if="content || sections.length"
                :value="active ? icons.mdiChevronUp : icons.mdiChevronDown" />
      </FRButton>
      <template v-if="active">
        <FRMarkdown v-if="content"
                    :value="content" />
        <PageDsfrDepartmentFrameSection v-for="section in sections"
                                        :key="section.path"
                                        :content="section.content"
                                        :label="section.label"
                                        :path="section.path"
                                        :sections="section.sections" />
      </template>
    </FRGrid>
  </FRCard>
</template>
