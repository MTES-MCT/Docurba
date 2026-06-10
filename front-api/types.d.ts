export interface Collectivite {
  departementId: string
  id: string
  membersId: Array<string>
  name: string
  siren: string
  skillPLU: boolean
  skillSCoT: boolean
  type: CollectiviteType
}

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

export interface Departement {
  creationDate: string
  id: string
  name: string
  regionId: string
}

export interface Region {
  creationDate: string
  id: string
  iso: string
  name: string
}
