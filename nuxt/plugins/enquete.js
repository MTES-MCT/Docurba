export default ({ app, $supabase, $utils, $user, $analytics, $urbanisator }, inject) => {
  const enquete = {
    VALIDATED_SINCE: '2025-06-01',
    async deleteValidationForCollectivite (code) {
      try {
        if (!code) {
          return {
            success: false,
            data: null,
            error: 'Code parameter is required'
          }
        }

        console.log('code to delete: ', code)
        const { data, error } = await $supabase
          .from('procedures_validations')
          .delete()
          .eq('collectivite_code', code)
          .gte('created_at', this.VALIDATED_SINCE)
          .select()
        console.log('DELETED:', data)
        if (error) {
          return {
            success: false,
            data: null,
            error: `Failed to delete validations: ${error.message}`
          }
        }

        return {
          success: true,
          data,
          error: null
        }
      } catch (error) {
        console.error('Unexpected error in deleteValidationForCollectivite:', error)
        return {
          success: false,
          data: null,
          error: error instanceof Error ? error.message : 'Unknown error occurred'
        }
      }
    },
    async getValidatedCollectivitesForDepartement (departement) {
      const { data, error } = await $supabase
        .rpc('validated_collectivites', {
          since: this.VALIDATED_SINCE,
          departement
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
      profile_id: $user.id
    }

    const formatProcedure = procedure => ({
      procedure_id: procedure.id,
      status: procedure.status,
      doc_type: procedure.doc_type,
      ...infosCollec
    })

    const plans = (collectiviteToValidate.plans || []).map(formatProcedure).filter(
      e => e.status === 'opposable' || e.status === 'en cours'
    )
    const scots = (collectiviteToValidate.scots || []).map(formatProcedure).filter(
      e => e.status === 'opposable' || e.status === 'en cours'
    )

    if (plans.length === 0) {
      plans.push({ ...infosCollec, status: 'RNU' })
    }

    return [...plans, ...scots]
  }

  inject('enquete', enquete)
}
