import { computed } from 'vue'
import { useData } from '@/composables/useData'
import type { DataResults } from '@/data/Data'
import type { Region } from '@/data/Region'

export function useRegions() {
  const { data, error, loading } = useData<DataResults<Region>>('regions')

  const regions = computed<Array<Region>>(() =>
    data.value ? data.value.results : []
  )
  const regionsCount = computed<number>(() =>
    data.value ? data.value.count : 0
  )

  return {
    regions,
    regionsCount,
    regionsError: error,
    regionsLoading: loading,
  }
}
