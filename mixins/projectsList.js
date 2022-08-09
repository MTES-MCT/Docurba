import { sortBy } from 'lodash'

// @vue/component
export default {
  data () {
    return {
      projects: [],
      sharings: [],
      sharedProjects: [],
      search: '',
      projectListLoaded: false
    }
  },
  computed: {
    searchValue () {
      return this.search.toLowerCase().normalize('NFD').replace(/[À-ÿ]/gu, '')
    },
    filteredProjects () {
      if (this.search) {
        const filteredProjects = this.projects.filter((project) => {
          const normalizedTitle = project.name.toLowerCase().normalize('NFD').replace(/[À-ÿ]/gu, '')
          return normalizedTitle.includes(this.searchValue)
        })

        return sortBy(filteredProjects, p => p.name)
      } else { return sortBy(this.projects, p => p.name) }
    },
    filteredSharings () {
      if (this.search) {
        const filteredSharedProjects = this.sharings.filter((sharing) => {
          const project = sharing.project
          const normalizedTitle = project.name.toLowerCase().normalize('NFD').replace(/[À-ÿ]/gu, '')
          return normalizedTitle.includes(this.searchValue)
        })

        return sortBy(filteredSharedProjects, s => s.project.name)
      } else { return sortBy(this.sharings, s => s.project.name) }
    },
    filteredSharedProjects () {
      return this.filteredSharings.map(sharing => sharing.project)
    }
  },
  async mounted () {
    await Promise.all([
      this.getProjects(),
      this.getSharedProjects()
    ])

    this.projectListLoaded = true
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
      const { data: sharings, error } = await this.$supabase.from('projects_sharing').select('id, role, project: project_id (id, name, docType, created_at, towns, trame)').eq('user_email', this.$user.email)

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
