import { createClient } from '@supabase/supabase-js'

async function migrateDgd (configSource, configTarget) {
  const supabaseDev = createClient(configSource.url, configSource.admin_key, {
    auth: { persistSession: false },
    db: { schema: 'sudocu' }
  })

  const supabase = createClient(configTarget.url, configTarget.admin_key, {
    auth: { persistSession: false }
  })

  const pageSize = 1000
  let startIndex = 0
  let hasMore = true

  while (hasMore) {
    try {
      const { data: dgdRecords, error: selectError } = await supabaseDev
        .from('dgd')
        .select('*')
        .range(startIndex, startIndex + pageSize - 1)

      if (selectError) {
        throw selectError
      }

      if (dgdRecords.length === 0) {
        hasMore = false
        break
      }

      const versementsFormat = dgdRecords.map(e => ({
        amount: e.montantdgd,
        year: e.anneedgd,
        category: e.categoriedgd,
        comment: e.commentaire,
        procedure_id: null,
        from_sudocu_procedure_id: e.noserieprocedure,
        from_sudocu: e.noseriedgd
      }))

      const { error: insertVersementsError } = await supabase
        .from('versements')
        .upsert(versementsFormat, { onConflict: 'from_sudocu', ignoreDuplicates: true })

      if (insertVersementsError) {
        throw insertVersementsError
      }

      const { data: procedureMatches, error: procedureError } = await supabase
        .from('procedures')
        .select('id, from_sudocuh')
        .in('from_sudocuh', versementsFormat.map(v => v.from_sudocu_procedure_id))

      if (procedureError) {
        throw procedureError
      }

      const procedureIdMap = new Map(
        procedureMatches.map(p => [p.from_sudocuh, p.id])
      )

      const versementsWithProcedures = versementsFormat.map(v => ({
        ...v,
        procedure_id: procedureIdMap.get(v.from_sudocu_procedure_id) || null
      }))

      const { error: insertError } = await supabase
        .from('versements')
        .upsert(versementsWithProcedures, {
          onConflict: 'from_sudocu',
          ignoreDuplicates: false
        })

      if (insertError) {
        throw insertError
      }

      startIndex += pageSize
    } catch (error) {
      hasMore = false
      throw error
    }
  }
}

export { migrateDgd }
