export interface Option<T> {
  disabled?: boolean
  label: string
  value: T
}

export interface OptionGroup<T> {
  label: string
  options: Array<Option<T>>
}

export type Options<T> = Array<Option<T> | OptionGroup<T>>
