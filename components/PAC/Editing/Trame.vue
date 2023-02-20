<template>
  <v-container fluid>
    <v-row>
      <v-col :cols="collapsedTree ? 1 : 4" class="collapse-transition">
        <client-only>
          <PACEditingGitTreeview
            :value="selectedSections"
            :readonly-dirs="readonlyDirs"
            :selectable="!!(project && project.id)"
            :project="project"
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
export default {
  props: {
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
    let cleanedPaths = []

    if (this.project && this.project.id) {
      cleanedPaths = this.project.PAC.map((path) => {
        return path.replace(/^\/PAC/, 'PAC').replace(/\/intro$/, '') // The replace is due to git path not including first /
      })
    }

    return {
      selectedSections: cleanedPaths,
      collapsedTree: false,
      selectedSection: null
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
