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
    <div ref="content" class="content-sizer" />
    <div ref="page" class="page-sizer" />
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

<style scoped>
.page-sizer {
    min-height: 297mm;
    height: 297mm;
    position: absolute;
  }

.content-sizer {
  /* min-height: 297mm;
  height: 297mm; */
  min-height: 254.5mm;
  height: 254.5mm;
  position: absolute;
}
</style>
