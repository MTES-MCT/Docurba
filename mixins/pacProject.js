// @vue/component
export default {
  // pacProject need to be a function that return a project.
  // In Vue 2 provided properties are not reactive. In Vue3 we will be able to use
  // The composition API to change this and make it simpler to use.
  inject: ['pacProject'],
  computed: {
    _project () {
      return this.pacProject()
    },
    pacProjectId () {
      return this._project.id
    },
    PAC () {
      return this._project.PAC
    }
  },
  created () {
    if (!this.pacProject) {
      // eslint-disable-next-line no-console
      console.error(new Error('You are using a pacPojectMixin but no pacProject was provided.'))
    }
  },
  methods: {
    async savePacItem (updatedItem) {
      // updatedItem will be saved by merging data with oldVersion of item. So you need to give it a path.
      if (updatedItem.path) {
        const currentItem = this.PAC.find(i => i.path === updatedItem.path)

        if (currentItem) {
          Object.assign(currentItem, updatedItem)

          // Because PAC is a JSON data for simplicity. This method update the whole pac project.
          // 2 people making changes at the same time can create conflicts and data loss.
          // 2 components with different pacProject ref for a same projectId can also create conflicts and data loss.
          await this.$supabase.from('projects').update({ PAC: this.PAC }).eq('id', this.pacProjectId)
        } else {
          // eslint-disable-next-line no-console
          console.error('Item to update not found, try to create a new aitem instead')
        }
      } else {
        // eslint-disable-next-line no-console
        console.error('Updated item need a path')
      }
    }
  }
}
