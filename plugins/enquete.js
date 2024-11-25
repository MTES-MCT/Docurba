export default ({ app, $supabase, $utils, $user, $analytics, $urbanisator }, inject) => {
  const enquete = {
    async getValidationCollectivitesForDepartement (departement) {
      const { data, error } = await $supabase
        .rpc('validated_collectivites_2024', {
          department_param: departement
        })
      return {
        success: !error,
        data,
        error
      }
    },
    async validateCollectivites (collectivitesToValidate) {
      try {
        if (!Array.isArray(collectivitesToValidate)) {
          return {
            success: false,
            data: null,
            error: 'collectivitesToValidate must be an array'
          }
        }

        const toUpsert = collectivitesToValidate
          .map(formatProceduresCollecToValidate)
          .flat()
        console.log('toUpsert: ', toUpsert)
        if (toUpsert.length === 0) {
          return {
            success: true,
            data: [],
            error: null
          }
        }

        const { data, error: upsertError } = await $supabase
          .from('procedures_validations')
          .upsert(toUpsert, {
            ignoreDuplicates: true
          })
          .select()

        if (upsertError) {
          return {
            success: false,
            data: null,
            error: `Failed to upsert validations: ${upsertError.message}`
          }
        }

        return {
          success: true,
          data,
          error: null
        }
      } catch (error) {
        console.error('Unexpected error in validateCollectivites:', error)
        return {
          success: false,
          data: null,
          error: error instanceof Error ? error.message : 'Unknown error occurred'
        }
      }
    }
  }

  function formatProceduresCollecToValidate (collectiviteToValidate) {
    if (!collectiviteToValidate?.code || !collectiviteToValidate?.departementCode) {
      return []
    }

    const infosCollec = {
      collectivite_code: collectiviteToValidate.code,
      departement: collectiviteToValidate.departementCode,
      test2024: true
    }

    const formatProcedure = procedure => ({
      procedure_id: procedure.id,
      status: procedure.status,
      doc_type: procedure.doc_type,
      ...infosCollec
    })

    const plans = (collectiviteToValidate.plans || []).map(formatProcedure)
    const scots = (collectiviteToValidate.scots || []).map(formatProcedure)

    return [...plans, ...scots].filter(
      e => e.status === 'opposable' || e.status === 'en cours'
    )
  }

  inject('enquete', enquete)
}
