import type { MaybeRef } from 'vue'
import { computed, toValue } from 'vue'
import { useData } from '@/composables/useData'
import type { Collectivite } from '@/data/Collectivite'
import type { DataResults } from '@/data/Data'
import { toPath } from '@/utils/path'

export function useCollectivites(
  params: {
    departementId?: MaybeRef<string | null>
    ids?: MaybeRef<Array<string>>
  } = {},
  page: MaybeRef<number> = 1,
  size: MaybeRef<number> = 25,
) {
  const departementId = computed<string | null>(() =>
    ('departementId' in params && toValue(params.departementId)) || null
  )
  const ids = computed<Array<string> | null>(() =>
    ('ids' in params && toValue(params.ids)) || null
  )
  const disabled = computed<boolean>(() =>
    ('departementId' in params && !departementId.value)
    || ('ids' in params && (!ids.value || !ids.value.length))
  )
  const path = computed<string>(() => toPath(['collectivites'], query.value))
  const query = computed<Record<string, boolean | string | Array<string>>>(() => {
    if (disabled.value) {
      return {}
    }

    const query: Record<string, boolean | string | Array<string>> = {}

    if (departementId.value) {
      query.departement = departementId.value
    }
    if (ids.value && ids.value.length) {
      query.id = ids.value
    }

    return {
      ...query,
      page: String(toValue(page)),
      size: String(toValue(size)),
    }
  })

  const { data, error, loading } = useData<DataResults<Collectivite>>(path, { disabled })

  const collectivites = computed<Array<Collectivite>>(() =>
    data.value ? data.value.results : []
  )
  const collectivitesCount = computed<number>(() =>
    data.value ? data.value.count : 0
  )

  return {
    collectivites,
    collectivitesCount,
    collectivitesError: error,
    collectivitesLoading: loading,
  }
}
