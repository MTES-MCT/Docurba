import type { MaybeRef } from 'vue'
import { computed, toValue } from 'vue'
import { useData } from '@/composables/useData'
import type { Procedure } from '@/data/Procedure'

export function useProcedure(procedureId: MaybeRef<string | null>) {
  const disabled = computed<boolean>(() => !toValue(procedureId))
  const path = computed<string>(() => `procedures/${toValue(procedureId)}`)

  const { data, error, loading } = useData<Procedure>(path, { disabled })

  return {
    procedure: data,
    procedureError: error,
    procedureLoading: loading,
  }
}
