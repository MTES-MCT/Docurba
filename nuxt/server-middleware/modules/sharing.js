const supabase = require('./supabase.js')

module.exports = {
  async  latestProcedurePrincipaleSharedUrl (email) {
    const { data: latestSharing } = await this.$supabase
      .from('projects_sharing')
      .select('id, projects!inner(id, procedures!inner(id))')
      .eq('user_email', email)
      .eq('role', 'write_frise')
      .eq('projects.procedures.is_principale', true)
      .order('created_at', { ascending: false })
      .limit(1)
      .maybeSingle()

    if (!latestSharing) {
      return
    }

    const latestProcedurePrincipaleShared = latestSharing.projects.procedures[0]
    const sharedProcedureUrl = `${process.env.APP_URL}/frise/${latestProcedurePrincipaleShared.id}`

    return sharedProcedureUrl
  },
  async updateNotifiedStatus (emails, projectId) {
    if (!emails || emails.length === 0) {
      console.log('No emails provided to update notification status')
      return
    }
    console.log('emails to update notif: ', emails)
    const { data, error } = await supabase
      .from('projects_sharing')
      .update({ email_notified: true })
      .in('user_email', emails)
      .eq('project_id', projectId)
      .eq('role', 'write_frise')

    if (error) {
      console.error('Error updating email_notified status:', error)
      throw error
    }

    console.log(`Updated email_notified status for ${data?.length ?? 0} rows`)
    return data
  }
}
