<template>
  <v-container>
    <v-row>
      <v-col>
        <v-treeview
          :items="PACroots"
          open-all
          item-text="titre"
          item-key="path"
          expand-icon=""
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import pacContent from '@/mixins/pacContent.js'

export default {
  mixins: [pacContent],
  computed: {
    PACroots () {
      const roots = this.PAC.filter((section) => {
        return section.depth === 2
      })

      return roots
    }
  }
}
</script>
