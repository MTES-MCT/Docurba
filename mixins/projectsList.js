// @vue/component
export default {
  data () {
    return {
      projects: [],
      sharedProjects: []
    }
  },
  mounted () {
    this.getProjects()
    this.getSharedProjects()
  },
  methods: {
    async getProjects () {
      const { data: projects, error } = await this.$supabase.from('projects').select('id, name, docType, created_at').eq('owner', this.$user.id)

      if (!error) {
        this.projects = projects
      } else {
      // eslint-disable-next-line no-console
        console.log(error)
      }
    },
    async getSharedProjects () {
      const { data: sharedProjects, error } = await this.$supabase.from('projectsSharing').select('project: project_id (id, name, docType, created_at)').eq('user_email', this.$user.email)

      if (!error) {
        this.sharedProjects = sharedProjects.map(p => p.project)
      } else {
      // eslint-disable-next-line no-console
        console.log(error)
      }
    }
  }
}
