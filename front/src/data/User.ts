export interface User {
  departementId: string | null
  email: string
  firstname: string
  government: boolean
  id: string
  lastname: string
  regionId: string | null
  scope: UserScope | null
}

export enum UserScope {
  COLLECTIVITE = 'COLLECTIVITE',
  ETAT = 'ETAT',
  REGION = 'REGION',
}
