<template>
  <div class="mt-4">
    <div v-for="(section, i) in sortedSections" :key="i">
      <template v-if="section.children || section.slug === 'intro'">
        <nuxt-content :document="section" />
        <PACContentSection v-if="section.children" :sections="section.children" :editable="editable" />
      </template>
      <template v-else>
        <v-expansion-panels :id="`panel-${getFirstId(section)}`" flat>
          <v-expansion-panel>
            <v-hover v-slot="{hover}">
              <v-expansion-panel-header>
                <v-row align="center">
                  <v-col cols="auto">
                    {{ section.titre }}
                  </v-col>
                  <v-spacer />
                  <v-col v-if="editable" cols="auto" class="py-0">
                    <v-dialog max-width="1000">
                      <template #activator="{on}">
                        <v-btn v-show="hover" icon v-on="on">
                          <v-icon color="secondary">
                            {{ icons.mdiCommentOutline }}
                          </v-icon>
                        </v-btn>
                      </template>
                      <PACCommentCard :section="section" />
                    </v-dialog>
                  </v-col>
                </v-row>
              </v-expansion-panel-header>
            </v-hover>
            <v-expansion-panel-content eager>
              <nuxt-content :document="section" />
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>
      </template>
    </div>
  </div>
</template>

<script>
import { mdiCommentOutline } from '@mdi/js'

export default {
  props: {
    sections: {
      type: Array,
      required: true
    },
    editable: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      icons: { mdiCommentOutline }
    }
  },
  computed: {
    sortedSections () {
      return this.sections.map(s => s).sort((sa, sb) => {
        return sa.ordre - sb.ordre
      })
    }
  },
  methods: {
    getFirstId (section) {
      const targetEl = section.body.children.find(el => el.tag?.indexOf('h') === 0)
      const targetId = targetEl ? targetEl.props.id : section.path

      return targetId
    }
  }
}
</script>
