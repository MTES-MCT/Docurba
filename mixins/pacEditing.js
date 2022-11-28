import { v4 as uuidv4 } from 'uuid'

// @vue/component
export default {
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
    // eslint-disable-next-line vue/prop-name-casing
    PAC: {
      type: Array,
      required: true
    }
  },
  data () {
    let projectId = null

    if (this.table === 'pac_sections_project' && this.tableKeys.project_id) {
      projectId = this.tableKeys.project_id
    }

    return {
      projectId
    }
  },
  methods: {
    async addNewSection (parentSection) {
      const dir = parentSection.slug === 'intro' ? parentSection.dir : parentSection.path

      const newSection = Object.assign({
        slug: 'new-section',
        dir,
        titre: 'Nouvelle section',
        path: `${dir}/${Date.now()}`,
        text: 'Nouvelle section'
      }, this.tableKeys)

      const { data: savedSection, err } = await this.$supabase.from(this.table).insert([newSection]).select()

      if (savedSection && !err) {
        if (this.table === 'pac_sections_project') {
          this.$notifications.notifyUpdate(this.tableKeys.project_id)
        }
      } else {
        // eslint-disable-next-line no-console
        console.log('error adding new section', savedSection, err)
      }
    },
    // Change should be +1 or -1
    async changeSectionOrder (section, change) {
      const parent = this.PAC.find((p) => {
        return p !== section &&
          section.dir.includes(p.path.replace(/\/intro$/, '')) &&
            p.depth + 1 === section.depth
      })

      const newIndex = section.ordre + change

      if (newIndex >= 0 && newIndex < parent.children.length) {
        // This interchange position of items in array in one operation.
        [
          parent.children[section.ordre],
          parent.children[newIndex]
        ] = [
          parent.children[newIndex],
          parent.children[section.ordre]
        ]

        if (this.table) {
          const updatedSections = parent.children.map((s, i) => {
            return Object.assign({
              id: s.id || uuidv4(), // if a section from a lower level was never changed it need an id to be upsert.
              path: s.path,
              dir: s.dir,
              ordre: i
            }, this.tableKeys)
          })

          await this.$supabase.from(this.table).upsert(updatedSections)
        }
      }
    },
    async deleteSection (matchKeys) {
      return await this.$supabase
        .from(this.table)
        .delete()
        .match(matchKeys)
    }
  }
}
