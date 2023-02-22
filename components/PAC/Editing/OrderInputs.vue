<template>
  <div :class="showBtn ? 'd-inline' : 'd-none'">
    <v-btn
      v-show="!!parent"
      depressed
      tile
      small
      icon
      @click.stop="changeOrder(-1)"
    >
      <v-icon>{{ icons.mdiChevronUp }}</v-icon>
    </v-btn>
    <v-btn
      v-show="!!parent"
      depressed
      tile
      small
      icon
      @click.stop="changeOrder(1)"
    >
      <v-icon>{{ icons.mdiChevronDown }}</v-icon>
    </v-btn>
  </div>
</template>
<script>
import { mdiChevronUp, mdiChevronDown } from '@mdi/js'

export default {
  props: {
    showBtn: {
      type: Boolean,
      default: false
    },
    gitRef: {
      type: String,
      required: true
    },
    section: {
      type: Object,
      required: true
    },
    sections: {
      type: Array,
      required: true
    }
  },
  data () {
    return {
      icons: { mdiChevronUp, mdiChevronDown },
      parent: this.findParent(this.sections)
    }
  },
  methods: {
    findParent (sections) {
      const parent = sections.find((section) => {
        if (section.children) {
          return !!section.children.find((child) => {
            return child.path === this.section.path
          })
        } else { return false }
      })

      if (parent) {
        return parent
      } else {
        const grandParent = sections.find((section) => {
          return this.section.path.includes(section.path)
        })

        if (grandParent) {
          return this.findParent(grandParent.children)
        } else { return null }
      }
    },
    async changeOrder (change) {
      const sectionIndex = this.parent.children.findIndex(c => c.path === this.section.path)
      const newIndex = sectionIndex + change

      if (newIndex >= 0 && newIndex < this.parent.children.length) {
        // This interchange position of items in array in one operation.
        [
          this.parent.children[sectionIndex],
          this.parent.children[newIndex]
        ] = [
          this.parent.children[newIndex],
          this.parent.children[sectionIndex]
        ]

        const updatedSections = this.parent.children.map((child, index) => {
          const { path } = child
          return {
            path,
            ref: this.gitRef,
            order: index
          }
        })

        const { data: supSections } = await this.$supabase.from('pac_sections').upsert(updatedSections).select()
        this.$emit('change', { sections: this.parent.children, supSections })
      }
    }
  }
}
</script>
