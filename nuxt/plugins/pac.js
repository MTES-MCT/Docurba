import { keyBy } from '@/plugins/utils'

export default ({ $supabase }, inject) => {
  inject('PAC', {
    async getAuthorFromEmail (email) {
      if (!email || process.env.DEV_EMAILS.includes(email.toLowerCase())) {
        return undefined
      }

      const { data: profiles } = await $supabase
        .from('profiles')
        .select('*')
        .ilike('email', email)

      return profiles[0]
    },
    async getAuthorsFromEmails (emails) {
      const filteredEmails = emails.filter(email => !process.env.DEV_EMAILS.includes(email.toLowerCase()))

      const { data: profiles } = await $supabase
        .from('profiles')
        .select('*')
        .ilikeAnyOf('email', filteredEmails)

      return keyBy(profiles, profile => profile.email?.toLowerCase())
    },
    pathToAnchor (path) {
      return path.replaceAll(/[^A-Za-z0-9]/g, '__')
    }
  })
}
