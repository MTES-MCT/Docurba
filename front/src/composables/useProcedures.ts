import type { MaybeRef } from 'vue'
import { computed, toValue } from 'vue'
import { useData } from '@/composables/useData'
import type { DataResults } from '@/data/Data'
import type { Procedure } from '@/data/Procedure'
import { toPath } from '@/utils/path'

export function useProcedures(
  params: {
    collectiviteId?: MaybeRef<string | null>
    departementId?: MaybeRef<string | null>
  } = {},
  page: MaybeRef<number> = 1,
  size: MaybeRef<number> = 25,
) {
  const collectiviteId = computed<string | null>(() =>
    ('collectiviteId' in params && toValue(params.collectiviteId)) || null
  )
  const departementId = computed<string | null>(() =>
    ('departementId' in params && toValue(params.departementId)) || null
  )
  const disabled = computed<boolean>(() =>
    ('collectiviteId' in params && !collectiviteId.value)
    || ('departementId' in params && !departementId.value)
  )
  const path = computed<string>(() => toPath(['procedures'], query.value))
  const query = computed<Record<string, boolean | string | Array<string>>>(() => {
    if (disabled.value) {
      return {}
    }

    const query: Record<string, boolean | string | Array<string>> = {}

    if (collectiviteId.value) {
      query.collectivite = collectiviteId.value
    }
    if (departementId.value) {
      query.departement = departementId.value
    }

    return {
      ...query,
      page: String(toValue(page)),
      size: String(toValue(size)),
    }
  })

  const { data, error, loading } = useData<DataResults<Procedure>>(path, { disabled })

  const procedures = computed<Array<Procedure>>(() =>
    (data.value && data.value.results) ?? []
  )
  const proceduresCount = computed<number>(() =>
    data.value ? data.value.count : 0
  )

  return {
    procedures,
    proceduresCount,
    proceduresError: error,
    proceduresLoading: loading,
  }
}
