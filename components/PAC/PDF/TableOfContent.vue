<template>
  <v-container>
    <v-row>
      <v-col>
        <v-treeview
          :items="PACroots"
          open-all
          item-text="titre"
          item-key="path"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  props: {
    project: {
      type: Object,
      required: true
    }
  },
  computed: {
    PACroots () {
      const roots = this.project.PAC.filter(section => section.toc && section.toc[0] && section.toc[0].depth === 2).sort((sa, sb) => {
        return sa.ordre - sb.ordre
      })

      return roots
    }
  }
}
</script>
