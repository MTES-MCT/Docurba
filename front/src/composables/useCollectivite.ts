import type { MaybeRef } from 'vue'
import { computed, toValue } from 'vue'
import { useData } from '@/composables/useData'
import type { Collectivite } from '@/data/Collectivite'

export function useCollectivite(collectiviteId: MaybeRef<string | null>) {
  const disabled = computed<boolean>(() => !toValue(collectiviteId))
  const path = computed<string>(() => `collectivites/${toValue(collectiviteId)}`)

  const { data, error, loading } = useData<Collectivite>(path, { disabled })

  return {
    collectivite: data,
    collectiviteError: error,
    collectiviteLoading: loading,
  }
}
