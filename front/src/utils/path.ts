export function fromPath(path: string): {
  parts: [string, ...Array<string>]
  query: Record<string, boolean | string | Array<string>>
} {
  const [partsString, queryString] = path.split('?')
  const [firstPart, ...otherParts] = partsString ? partsString.split('/') : ['']
  const parts: [string, ...Array<string>] = [firstPart ?? '', ...otherParts]
  const query: Record<string, boolean | string | Array<string>> = {}

  if (!queryString) {
    return { parts, query }
  }
  for (const item of queryString.split('&')) {
    if (!item.includes('=')) {
      query[item] = true
    }

    const [key, value] = item.split('=')

    if (!key || !value) continue

    query[key] = value.includes(',') ? value.split(',') : value
  }

  return { parts, query }
}

export function toPath(
  parts: [string, ...Array<string>],
  query: Record<string, boolean | string | Array<string>>,
): string {
  const items: Array<string> = []

  Object.entries(query).forEach(([key, value]) => {
    switch (typeof value) {
      case 'boolean':
        return value && items.push(key)
      case 'string':
        return items.push(`${key}=${value}`)
      default:
        return items.push(value.map((item) => `${key}=${item}`).join('&'))
    }
  })

  return `${parts.join('/')}${items.length ? `?${items.join('&')}` : ''}`
}
