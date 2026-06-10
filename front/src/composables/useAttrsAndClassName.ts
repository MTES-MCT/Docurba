import type { Attrs } from 'vue'
import { computed, useAttrs } from 'vue'

export function useAttrsAndClassName() {
  const allAttrs = useAttrs()

  const attrs = computed<Attrs>(() => {
    const { class: _, ...attrs } = allAttrs

    return attrs
  })
  const className = computed<string>(() => allAttrs.class ? String(allAttrs.class) : '')

  return {
    attrs,
    className,
  }
}
