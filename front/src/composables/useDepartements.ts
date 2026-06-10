import { computed } from 'vue'
import { useData } from '@/composables/useData'
import type { DataResults } from '@/data/Data'
import type { Departement } from '@/data/Departement'

export function useDepartements() {
  const { data, error, loading } = useData<DataResults<Departement>>('departements')

  const departements = computed<Array<Departement>>(() =>
    data.value ? data.value.results : []
  )
  const departementsCount = computed<number>(() =>
    data.value ? data.value.count : 0
  )

  return {
    departements,
    departementsCount,
    departementsError: error,
    departementsLoading: loading,
  }
}
