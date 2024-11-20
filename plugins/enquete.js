export default ({ app, $supabase, $utils, $user, $analytics }, inject) => {
  const enquete = {
    async validateCollectivite (collectivitesCodes) {
      // TODO: get all procedure en cours ou opposable principale sur la collectivite
      const procedures = await this.$urbanisator.getCollectivitesProcedures(collectivitesCodes)
      console.log('procedures to validate: ', procedures)
      const toUpsert = {
        collectivite_code: '',
        procedure_id: '',
        status: '',
        departement: '',
        doc_type: ''
      }
      console.log('toUpsert: ', toUpsert)
      // const { error: errorUpsertValidation } = await $supabase.from('procedures_validations')
      //   .upsert(toUpsert, { onConflict: 'project_id,user_email,role', ignoreDuplicates: true })
      //   .select()
      // if (errorUpsertValidation) { console.log('errorUpsertValidation: ', errorUpsertValidation) }
    }
  }
  inject('sharing', enquete)
}
