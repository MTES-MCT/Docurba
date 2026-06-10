import type { MaybeRef } from 'vue'
import { ref, toValue, watchEffect } from 'vue'
import { useAuth } from '@/composables/useAuth'

export function useData<T>(path: MaybeRef<string>, options: {
  disabled: MaybeRef<boolean>
} = {
  disabled: false,
}) {
  const data = ref<T | null>(null)
  const error = ref<Error | null>(null)
  const loading = ref(false)

  const { headers } = useAuth()

  const fetchData = async () => {
    data.value = null
    error.value = null

    if (toValue(options.disabled)) return

    loading.value = true

    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/${toValue(path)}`, {
        headers: headers.value,
      })
      data.value = await res.json()
    } catch (err) {
      error.value = err as Error
    }

    loading.value = false
  }

  watchEffect(() => {
    fetchData()
  })

  return {
    data,
    error,
    loading,
  }
}
