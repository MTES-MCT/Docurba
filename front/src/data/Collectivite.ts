export interface Collectivite {
  departementId: string
  id: string
  intercommunaliteId: string | null
  membersId: Array<string>
  name: string
  siren: string
  skillPLU: boolean
  skillSCoT: boolean
  type: CollectiviteType
}

export type CollectiviteLabel = 'Communes' | 'EPCIs' | 'Groupements'

export enum CollectiviteType {
  CA = 'CA',
  CC = 'CC',
  COM = 'COM',
  CU = 'CU',
  EPT = 'EPT',
  MET69 = 'MET69',
  METRO = 'METRO',
  PETR = 'PETR',
  POLEM = 'POLEM',
  SIVOM = 'SIVOM',
  SIVU = 'SIVU',
  SMF = 'SMF',
  SMO = 'SMO',
}

export const EPCI_TYPES = [
  CollectiviteType.CA,
  CollectiviteType.CC,
  CollectiviteType.CU,
  CollectiviteType.MET69,
  CollectiviteType.METRO,
]
