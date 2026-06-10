export function displayDate(value: string | null): string {
  return value
    ? value.split('-').reverse().join('/')
    : ''
}

export function displayNumber(value: number | null): string {
  return value === null ? '' : String(value)
}
