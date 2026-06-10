import type { DocumentType } from '@/data/Document'
import type { Option } from '@/data/Option'

export interface Procedure {
  approvalDate: string | null
  children: Array<Procedure>
  collectiviteId: string
  documentType: DocumentType
  events: Array<ProcedureEvent>
  id: string
  number: number | null
  parentId: string | null
  prescriptionDate: string | null
  status: ProcedureStatus
  type: ProcedureType
}

export interface ProcedureEvent {
  date: string
  description: string | null
  id: string
  type: ProcedureEventType
}

export enum ProcedureEventType {
  ABAND = 'ABAND',
  ADSPRESS = 'ADSPRESS',
  AFF = 'AFF',
  ANNULTA = 'ANNULTA',
  APPPREF = 'APPPREF',
  ARRABRO = 'ARRABRO',
  ARRENQ = 'ARRENQ',
  ARRLANC = 'ARRLANC',
  ARRMP = 'ARRMP',
  ARRPROJ = 'ARRPROJ',
  AUTRE = 'AUTRE',
  AVICDNPS = 'AVICDNPS',
  AVICDPENAF = 'AVICDPENAF',
  AVISENV = 'AVISENV',
  AVISETAT = 'AVISETAT',
  BACKAPPROB = 'BACKAPPROB',
  CADUC = 'CADUC',
  CONSCDNPS = 'CONSCDNPS',
  CONSENV = 'CONSENV',
  CONSENVCPC = 'CONSENVCPC',
  CONSPPA = 'CONSPPA',
  DEBATEPADD = 'DEBATEPADD',
  DEBENQ = 'DEBENQ',
  DEBINFO = 'DEBINFO',
  DEBPADD = 'DEBPADD',
  DELAPP = 'DELAPP',
  DELBILAN = 'DELBILAN',
  DELMEC = 'DELMEC',
  DELOMC = 'DELOMC',
  DEROG = 'DEROG',
  ECHSCH = 'ECHSCH',
  EXECUT = 'EXECUT',
  EXEMEVALENV = 'EXEMEVALENV',
  FINENQ = 'FINENQ',
  FININFO = 'FININFO',
  NOTMOD = 'NOTMOD',
  NOTPROJ = 'NOTPROJ',
  PAC = 'PAC',
  PACCOMP = 'PACCOMP',
  PRES = 'PRES',
  PUB = 'PUB',
  PUBPERI = 'PUBPERI',
  RECGRAC = 'RECGRAC',
  REUPPA = 'REUPPA',
  TRANSCONT = 'TRANSCONT',
  TRPREFAPP = 'TRPREFAPP',
}

export enum ProcedureStatus {
  ABANDONNEE = 'ABANDONNEE',
  ABROGEE = 'ABROGEE',
  ANNULEE = 'ANNULEE',
  APPROUVEE = 'APPROUVEE',
  CADUC = 'CADUC',
  EN_COURS = 'EN_COURS',
  EN_PROJET = 'EN_PROJET',
  OPPOSABLE = 'OPPOSABLE',
  PRECEDENTE = 'PRECEDENTE',
}

export enum ProcedureType {
  ABROGATION = 'ABROGATION',
  ELABORATION = 'ELABORATION',
  MISE_A_JOUR = 'MISE_A_JOUR',
  MISE_EN_COMPATIBILITE = 'MISE_EN_COMPATIBILITE',
  MODIFICATION = 'MODIFICATION',
  MODIFICATION_SIMPLIFIEE = 'MODIFICATION_SIMPLIFIEE',
  REVISION = 'REVISION',
  REVISION_ALLEGEE = 'REVISION_ALLEGEE',
  REVISION_SIMPLIFIEE = 'REVISION_SIMPLIFIEE',
}

export const LABEL_BY_PROCEDURE_STATUS: Record<ProcedureStatus, string> = {
  [ProcedureStatus.ABANDONNEE]: 'Abandonnée',
  [ProcedureStatus.ABROGEE]: 'Abrogée',
  [ProcedureStatus.ANNULEE]: 'Annulée',
  [ProcedureStatus.APPROUVEE]: 'Approuvée',
  [ProcedureStatus.CADUC]: 'Caduc',
  [ProcedureStatus.EN_COURS]: 'En cours',
  [ProcedureStatus.EN_PROJET]: 'En projet',
  [ProcedureStatus.OPPOSABLE]: 'Opposable',
  [ProcedureStatus.PRECEDENTE]: 'Précédente',
}

export const LABEL_BY_PROCEDURE_TYPE: Record<ProcedureType, string> = {
  [ProcedureType.ABROGATION]: 'Abrogation',
  [ProcedureType.ELABORATION]: 'Elaboration',
  [ProcedureType.MISE_A_JOUR]: 'Mise à jour',
  [ProcedureType.MISE_EN_COMPATIBILITE]: 'Mise en compatibilité',
  [ProcedureType.MODIFICATION]: 'Modification',
  [ProcedureType.MODIFICATION_SIMPLIFIEE]: 'Modification simplifiée',
  [ProcedureType.REVISION]: 'Révision',
  [ProcedureType.REVISION_ALLEGEE]: 'Révision allégée (ou RMS)',
  [ProcedureType.REVISION_SIMPLIFIEE]: 'Révision simplifiée',
}

export const PROCEDURE_STATUSES: Array<Option<ProcedureStatus>> = [{
  label: LABEL_BY_PROCEDURE_STATUS[ProcedureStatus.EN_PROJET],
  value: ProcedureStatus.EN_PROJET,
}, {
  label: LABEL_BY_PROCEDURE_STATUS[ProcedureStatus.EN_COURS],
  value: ProcedureStatus.EN_COURS,
}, {
  label: LABEL_BY_PROCEDURE_STATUS[ProcedureStatus.APPROUVEE],
  value: ProcedureStatus.APPROUVEE,
}, {
  label: LABEL_BY_PROCEDURE_STATUS[ProcedureStatus.OPPOSABLE],
  value: ProcedureStatus.OPPOSABLE,
}, {
  label: LABEL_BY_PROCEDURE_STATUS[ProcedureStatus.PRECEDENTE],
  value: ProcedureStatus.PRECEDENTE,
}, {
  label: LABEL_BY_PROCEDURE_STATUS[ProcedureStatus.ABANDONNEE],
  value: ProcedureStatus.ABANDONNEE,
}, {
  label: LABEL_BY_PROCEDURE_STATUS[ProcedureStatus.ANNULEE],
  value: ProcedureStatus.ANNULEE,
}, {
  label: LABEL_BY_PROCEDURE_STATUS[ProcedureStatus.ABROGEE],
  value: ProcedureStatus.ABROGEE,
}, {
  label: LABEL_BY_PROCEDURE_STATUS[ProcedureStatus.CADUC],
  value: ProcedureStatus.CADUC,
}]
