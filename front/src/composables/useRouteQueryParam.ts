import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

export function useRouteQueryParam<T>(name: string, { fromQuery, toQuery }: {
  fromQuery: (query: string | undefined) => T
  toQuery: (value: T) => string | undefined
} = {
  fromQuery: (query: string | undefined) => (query ?? null) as T,
  toQuery: (value: T) => (value || undefined) as string | undefined,
}) {
  const route = useRoute()
  const router = useRouter()

  const value = computed<T>({
    get() {
      return fromQuery(
        route.query[name]
          ? String(route.query[name])
          : undefined
      )
    },
    set(newValue) {
      router.replace({
        ...route,
        query: {
          ...route.query,
          [name]: toQuery(newValue),
        },
      })
    },
  })

  return value
}
