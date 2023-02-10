<template>
  <v-container fluid>
    <v-row>
      <v-col :cols="collapsedTree ? 1 : 4" class="collapse-transition">
        <client-only>
          <PACEditingGitTreeview
            :value="selectedSections"
            :readonly-dirs="readonlyDirs"
            :selectable="selectable"
            :table="table"
            :table-keys="tableKeys"
            :git-ref="gitRef"
            @open="selectSection"
          />
        </client-only>
      </v-col>
      <v-col v-if="selectedSection" :cols="collapsedTree ? 11 : 8" class="fill-height collapse-transition">
        <PACEditingGitContentSection
          :project="project"
          :section="selectedSection"
          :git-ref="gitRef"
          :readonly-dirs="readonlyDirs"
          :table="table"
          :table-keys="tableKeys"
        />
      </v-col>
      <v-col v-else cols="">
        <v-card flat color="g100">
          <v-card-text>Selectionnez une section à éditer.</v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
// Each sections Table should have these keys.
// function sectionsCommonKeys (section) {
//   const { text, titre, path, slug, dir, ordre } = section
//   return { text, titre, path, slug, dir, ordre }
// }

export default {
  props: {
    // pacData should be a unified array of sections from DB. See if parent is mixing unifiedPac.js
    // pacData: {
    //   type: Array,
    //   required: true
    // },
    table: {
      type: String,
      required: true
    },
    // This should be the section identifiers in the table.
    // For exemple: {project_id: 'XXX'} for table pac_sections_project
    tableKeys: {
      type: Object,
      required: true
    },
    sectionsList: {
      type: Array,
      default () { return [] }
    },
    project: {
      type: Object,
      default () { return {} }
    },
    readonlyDirs: {
      type: Array,
      default () {
        return [
          'PAC/Cadre-juridique-et-grands-principes-de-la-planification'
        ]
      }
    },
    gitRef: {
      type: String,
      required: true
    }
  },
  data () {
    // The replace is due to git path not including first /
    const cleanedPaths = this.sectionsList.map((path) => {
      return path.replace('/PAC', 'PAC').replace(/\/intro$/, '')
    })

    return {
      selectedSections: cleanedPaths, // The replace is due to git path not including first /
      collapsedTree: false,
      selectedSection: null
    }
  },
  computed: {
    selectable () {
      // You can select sections only for projects.
      return this.table === 'pac_sections_project'
    }
  },
  methods: {
    // This method allow us to work on a clean data ref environement.
    selectSection (section) {
      this.selectedSection = Object.assign({}, section)
    }
  }
}
</script>
