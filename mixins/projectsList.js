// @vue/component
export default {
  data () {
    return {
      projects: [],
      sharedProjects: [],
      search: ''
    }
  },
  computed: {
    searchValue () {
      return this.search.toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu, '')
    },
    filteredProjects () {
      if (this.search) {
        return this.projects.filter((project) => {
          const normalizedTitle = project.name.toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu, '')
          return normalizedTitle.includes(this.searchValue)
        })
      } else { return this.projects }
    },
    filteredSharedProjects () {
      if (this.search) {
        return this.sharedProjects.filter((project) => {
          const normalizedTitle = project.name.toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu, '')
          return normalizedTitle.includes(this.searchValue)
        })
      } else { return this.sharedProjects }
    }
  },
  mounted () {
    this.getProjects()
    this.getSharedProjects()
  },
  methods: {
    async getProjects () {
      const { data: projects, error } = await this.$supabase.from('projects').select('*').eq('owner', this.$user.id)

      if (!error) {
        this.projects = projects
      } else {
      // eslint-disable-next-line no-console
        console.log(error)
      }
    },
    async getSharedProjects () {
      const { data: sharedProjects, error } = await this.$supabase.from('projects_sharing').select('project: project_id (id, name, docType, created_at)').eq('user_email', this.$user.email)

      if (!error) {
        this.sharedProjects = sharedProjects.map(p => p.project)
      } else {
      // eslint-disable-next-line no-console
        console.log(error)
      }
    }
  }
}
