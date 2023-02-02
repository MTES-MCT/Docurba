<template>
  <v-container fluid>
    <v-row>
      <v-col :cols="collapsedTree ? 1 : 4" class="collapse-transition">
        <client-only>
          <!-- <PACEditingTreeview
            v-model="selectedSections"
            :p-a-c="PAC"
            :collapsed="collapsedTree"
            :table="table"
            :table-keys="tableKeys"
            :project-id="$route.params.projectId"
            :selectable="selectable"
            @open="selectSection"
            @collapse="collapsedTree = !collapsedTree"
          /> -->
          <PACEditingGitTreeview
            v-model="selectedSections"
            :selectable="selectable"
            :table="table"
            :table-keys="tableKeys"
            @open="selectSection"
          />
        </client-only>
      </v-col>
      <v-col v-if="selectedSection" :cols="collapsedTree ? 11 : 8" class="fill-height collapse-transition">
        <!-- <PACEditingContentSection
          :readonly-dirs="readonlyDirs"
          :section="selectedSection"
          :p-a-c="PAC"
          :table="table"
          :table-keys="tableKeys"
          :attachements-folders="attachementsFolders"
        /> -->
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
    // attachementsFolders () {
    //   // Beware, this could be unreactive to project changes.
    //   if (this.project && this.project.id && this.project.towns) {
    //     return [this.project.towns[0].code_departement]
    //   } else { return [] }
    // }
  },
  watch: {
    selectedSections () {
      this.changeSelectedSections()
    }
  },
  methods: {
    // This method allow us to work on a clean data ref environement.
    selectSection (section) {
      // console.log(section)
      this.selectedSection = section
      // const selectedSection = this.PAC.find(s => s.path === section.path)
      // this.selectedSection = Object.assign(sectionsCommonKeys(selectedSection), this.tableKeys)
    },
    async changeSelectedSections () {
      if (this.selectable && this.tableKeys.project_id) {
      // This make it so we can't save sections as objects in reading mode for comments and checked features.
        await this.$supabase.from('projects').update({
          PAC: this.selectedSections.map(s => s || s.path)
        }).eq('id', this.tableKeys.project_id)

        this.$notifications.notifyUpdate(this.tableKeys.project_id)
      }
    }
  }
}
</script>
