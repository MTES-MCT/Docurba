// function communKeys (section) {
//   const { text, titre, path, slug, dir, ordre } = section
//   return { text, titre, path, slug, dir, ordre }
// }

// This are functions to decompose and recompose sections data model based on their table.
// const tablesMap = {
//   'pac_sections_project' (section) {
//     // eslint-disable-next-line camelcase
//     const { project_id } = section

//     return Object.assign(communKeys(section), { project_id })
//   }
// }

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

      // newSection.dept = this.departementCode
      const { data: savedSection, err } = await this.$supabase.from(this.table).insert([newSection])

      if (savedSection && !err) {
        // console.log(savedSection)
        // this.PAC.push(Object.assign({
        //   body: this.mdParser.parse(savedSection.text)
        // }, savedSection[0]))

        if (this.table === 'pac_sections_project') {
          this.$notifications.notifyUpdate(this.tableKeys.project_id)
        }
      } else {
        // eslint-disable-next-line no-console
        console.log('error adding new section', savedSection, err)
      }
    },
    async deleteSection (matchKeys) {
      return await this.$supabase
        .from(this.table)
        .delete()
        .match(matchKeys)

      // if (data && !err) {
      //   const deletedSectionIndex = this.PAC.findIndex(s => s.path === deletedSection.path)
      //   const originalSection = this.originalPAC.find(s => s.path === deletedSection.path)

      //   if (originalSection) {
      //     this.PAC.splice(deletedSectionIndex, 1, originalSection)
      //   } else { this.PAC.splice(deletedSectionIndex, 1) }
      // } else {
      //   // eslint-disable-next-line no-console
      //   console.log('err deleting a section')
      // }
    }
  }
}
