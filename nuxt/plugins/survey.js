import { orderBy, uniq } from 'lodash'

// interface SurveyEntry {
//   id: string
//   procedure: Procedure | null
//   respondant: SurveyRespondant | null
//   responseDate: string | null
//   validated: boolean
// }
// interface SurveyRespondant {
//   firstname: string
//   id: string
//   lastname: string
// }

export default ({ $procedureApi, $supabase, $user }, inject) => {
  const id = process.env.SURVEY_ID || null
  const startDate = process.env.SURVEY_START_DATE
    ? new Date(process.env.SURVEY_START_DATE)
    : null
  const endDate = process.env.SURVEY_END_DATE
    ? new Date(process.env.SURVEY_END_DATE)
    : null
  const now = new Date()

  inject('survey', {
    active: (
      !!id &&
      !!startDate &&
      !!endDate &&
      now >= new Date(startDate) &&
      now < new Date(endDate)
    ),
    endDate,
    startDate,
    year: process.env.SURVEY_YEAR || '',
    async getEntries ({ departmentCode }) {
      const { data, error } = await $supabase.from('surveys_proceduresurvey')
        .select([
          'collectivite_code_id',
          'id',
          'is_validated',
          'procedure_id',
          'profiles(firstname,lastname,user_id)',
          'responded_at'
        ].join())
        .eq('survey_id', id)
        .contains('departements', [departmentCode])

      if (error) {
        throw error
      }
      if (!data) {
        return []
      }

      const procedures = await $procedureApi.listForTerritorialAuthorities(
        uniq(data.map(d => d.collectivite_code_id))
      )
      const existingProcedureById = Object.fromEntries(procedures.map(({ id }) => [id, true]))

      return _fromApiSurveyEntries(
        data.filter(d => existingProcedureById[d.procedure_id]),
        { procedures }
      )
    },
    async toggleEntries (entries, validate) {
      const patch = {
        respondant:
          validate
            ? {
                firstname: $user.profile.firstname,
                id: $user.id,
                lastname: $user.profile.lastname
              }
            : null,
        responseDate: validate ? new Date().toJSON() : null,
        validated: validate
      }
      const apiPatch = {
        is_validated: patch.validated,
        respondant_id: patch.respondant?.id,
        responded_at: patch.responseDate
      }

      await $supabase.from('surveys_proceduresurvey')
        .upsert(entries.map(({ id }) => ({
          id,
          ...apiPatch
        })))

      return entries.map(entry => ({
        ...entry,
        ...patch
      }))
    }
  })
}

function _fromApiSurveyEntry (apiSurveyEntry, { procedures }) {
  return {
    id: apiSurveyEntry.id,
    procedure: _fromApiSurveyProcedure(apiSurveyEntry, { procedures }),
    respondant: _fromApiSurveyRespondant(apiSurveyEntry),
    responseDate: apiSurveyEntry.responded_at || null,
    validated: !!apiSurveyEntry.is_validated
  }
}

function _fromApiSurveyEntries (apiSurveyEntries, { procedures }) {
  return orderBy(
    apiSurveyEntries.map(apiSurveyEntry =>
      _fromApiSurveyEntry(apiSurveyEntry, { procedures })
    ),
    [
      ({ procedure }) => {
        switch (procedure.status) {
          case 'En cours':
            return 1
          case 'Opposable':
            return 2
          default:
            return 3
        }
      },
      ({ procedure }) => procedure.prescriptionDate || '0000-00-00',
      ({ procedure }) => procedure.lastUpdateDate || '0000-00-00',
      ({ procedure }) => procedure.approvalDate || '0000-00-00'
    ],
    ['asc', 'desc', 'desc', 'desc']
  )
}

function _fromApiSurveyProcedure (apiSurveyEntry, { procedures }) {
  return procedures.find(({ id }) => id === apiSurveyEntry.procedure_id) || null
}

function _fromApiSurveyRespondant (apiSurveyEntry) {
  return apiSurveyEntry.profiles
    ? {
        firstname: apiSurveyEntry.profiles.firstname,
        id: apiSurveyEntry.profiles.user_id,
        lastname: apiSurveyEntry.profiles.lastname
      }
    : null
}
