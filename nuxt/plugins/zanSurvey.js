export default ({ app, $supabase, $utils, $user, $analytics, $urbanisator }, inject) => {
  const zanSurvey = {
    async getProcedures (departement) {
      let { data, error } = await $supabase
        .from('surveys_proceduresurvey')
        .select('procedures!inner(id,doc_type,status,name,type,numero,is_pluih,collectivite_porteuse_id,procedures_perimetres(collectivite_type,collectivite_code),core_proceduretopic(core_topic(display_name))),departements,is_validated,collectivite_code_id,profiles(email),responded_at')
        .contains('departements', [departement])

      data = data.map((e) => {
        const topics = e.procedures.core_proceduretopic?.map(e => e.core_topic.display_name)
        return {
          // Infos needed to compute the name. See utils.formatProcedureName
          name: e.procedures.name,
          type: e.procedures.type,
          numero: e.procedures.numero,
          doc_type: e.procedures.doc_type,
          is_pluih: e.procedures.is_pluih,
          procedures_perimetres: e.procedures.procedures_perimetres,
          collectivite_porteuse_id: e.procedures.collectivite_porteuse_id,
          // End of infos needed to compute the name.
          procedure_id: e.procedures.id,
          status: e.procedures.status,
          is_validated: e.is_validated,
          collectivite_code: e.collectivite_code_id,
          respondant_email: e.profiles?.email,
          responded_at: e.responded_at,
          topics
        }
      })
      return {
        success: !error,
        data,
        error
      }
    },

    async validateCollectivites (collectivitesCodes) {
      try {
        if (!Array.isArray(collectivitesCodes)) {
          return {
            success: false,
            data: null,
            error: 'collectivitesToValidate must be an array'
          }
        }
        const { error } = await $supabase.from('surveys_proceduresurvey').update({
          is_validated: true,
          respondant_id: $user.id,
          responded_at: new Date().toISOString()
        }).in('collectivite_code_id', collectivitesCodes)

        if (error) {
          return {
            success: false,
            error: `Failed to upsert validations: ${error}`
          }
        }

        return {
          success: true,
          error: null
        }
      } catch (error) {
        console.error('Unexpected error in validateCollectivites:', error)
        return {
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error occurred'
        }
      }
    },
    async cancelCollectiviteValidation (collectiviteCode) {
      try {
        const { error } = await $supabase.from('surveys_proceduresurvey').update({
          is_validated: false,
          respondant_id: null,
          responded_at: null
        }).eq('collectivite_code_id', collectiviteCode)

        if (error) {
          return {
            success: false,
            error: `Failed to upsert validations: ${error}`
          }
        }

        return {
          success: true,
          error: null
        }
      } catch (error) {
        console.error('Unexpected error in validateCollectivites:', error)
        return {
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error occurred'
        }
      }
    }
  }

  inject('zanSurvey', zanSurvey)
}
