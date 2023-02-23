<template>
  <v-row>
    <v-col cols="12">
      <PACContentSection :sections="pacData" :editable="editable" :open="[0]" />
    </v-col>
  </v-row>
</template>

<script>

export default {
  props: {
    editable: {
      type: Boolean,
      default: false
    },
    pacData: {
      type: Array,
      required: true
    }
  },
  data () {
    return {
      contentSearch: '',
      checkedItems: 0
      // PACroots
    }
  },
  mounted () {
    // this.checkedItems = this.PAC.filter(item => item.checked).length

    // this.PACroots.forEach((root, index) => {
    //   this.addCounter(root, [index + 1])
    // })
  },
  methods: {
    checkItem (section) {
      if (section.checked) {
        this.checkedItems += 1
      } else { this.checkedItems -= 1 }

      this.$emit('read', section)
    },
    scrollTo (item) {
      if (item.body.children && item.body.children.length) {
        if ((item.children && item.children.length) || item.slug === 'intro') {
          this.$vuetify.goTo(`#${item.path.replaceAll(/[^A-Za-z0-9]/g, '__')}`)
        } else {
          this.$vuetify.goTo(`#panel__${item.path.replaceAll(/[^A-Za-z0-9]/g, '__')}`)
        }
      }
    }
  }
}
</script>

<style scoped>
.sticky-tree {
  position: sticky;
  overflow: scroll;
  /* 128 = 80 (from search row ) + 48 (one tree leaf) */
  max-height: calc(100vh - 176px);
}
</style>
