<template>
  <v-container fluid>
    <v-row>
      <v-col :cols="collapsedTree ? 1 : 4" class="collapse-transition">
        <client-only>
          <PACEditingGitTreeview
            :value="selectedSections"
            :selectable="selectable"
            :table="table"
            :table-keys="tableKeys"
            @open="selectSection"
          />
        </client-only>
      </v-col>
      <v-col v-if="selectedSection" :cols="collapsedTree ? 11 : 8" class="fill-height collapse-transition">
        <PACEditingGitContentSection
          :project="project"
          :section="selectedSection"
          :content-ref="'test'"
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
import pacContent from '@/mixins/pacContent.js'

// Each sections Table should have these keys.
// function sectionsCommonKeys (section) {
//   const { text, titre, path, slug, dir, ordre } = section
//   return { text, titre, path, slug, dir, ordre }
// }

export default {
  mixins: [pacContent],
  props: {
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
          '/PAC/Cadre-juridique-et-grands-principes-de-la-planification'
        ]
      }
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
  // watch: {
  //   selectedSections () {
  //     this.changeSelectedSections()
  //   }
  // },
  methods: {
    // This method allow us to work on a clean data ref environement.
    selectSection (section) {
      this.selectedSection = Object.assign({}, section)
    }
    // async changeSelectedSections () {
    //   if (this.selectable && this.tableKeys.project_id) {
    //   // This make it so we can't save sections as objects in reading mode for comments and checked features.
    //     await this.$supabase.from('projects').update({
    //       PAC: this.selectedSections.map(s => s || s.path)
    //     }).eq('id', this.tableKeys.project_id)

    //     this.$notifications.notifyUpdate(this.tableKeys.project_id)
    //   }
    // }
  }
}
</script>
