// @vue/component
export default {
  data () {
    return {
      projects: [],
      sharings: [],
      sharedProjects: [],
      search: '',
      subscription: null
    }
  },
  computed: {
    searchValue () {
      return this.search.toLowerCase().normalize('NFD').replace(/[À-ÿ]/gu, '')
    },
    filteredProjects () {
      if (this.search) {
        return this.projects.filter((project) => {
          const normalizedTitle = project.name.toLowerCase().normalize('NFD').replace(/[À-ÿ]/gu, '')
          return normalizedTitle.includes(this.searchValue)
        })
      } else { return this.projects }
    },
    filteredSharings () {
      if (this.search) {
        return this.sharings.filter((sharing) => {
          const project = sharing.project
          const normalizedTitle = project.name.toLowerCase().normalize('NFD').replace(/[À-ÿ]/gu, '')
          return normalizedTitle.includes(this.searchValue)
        })
      } else { return this.sharings }
    },
    filteredSharedProjects () {
      return this.filteredSharings.map(sharing => sharing.project)
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
      const { data: sharings, error } = await this.$supabase.from('projects_sharing').select('project: project_id (id, name, docType, created_at, towns, trame)').eq('user_email', this.$user.email)

      if (!error) {
        this.sharings = sharings
        this.sharedProjects = sharings.map(p => p.project)
      } else {
      // eslint-disable-next-line no-console
        console.log(error)
      }
    }
  }
}
