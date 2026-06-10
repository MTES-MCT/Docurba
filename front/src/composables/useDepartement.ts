import type { MaybeRef } from 'vue'
import { computed, toValue } from 'vue'
import { useData } from '@/composables/useData'
import type { Departement } from '@/data/Departement'

export function useDepartement(departementId: MaybeRef<string | null>) {
  const disabled = computed<boolean>(() => !toValue(departementId))
  const path = computed<string>(() => `departements/${toValue(departementId)}`)

  const { data, error, loading } = useData<Departement>(path, { disabled })

  return {
    departement: data,
    departementError: error,
    departementLoading: loading,
  }
}
