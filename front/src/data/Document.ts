export enum DocumentType {
  CC = 'CC',
  PLU = 'PLU',
  PLUI = 'PLUI',
  PLUIH = 'PLUIH',
  PLUIHM = 'PLUIHM',
  PLUIM = 'PLUIM',
  SCOT = 'SCOT',
}

export interface DocumentTypesGroup {
  description: string
  id: string
  label: string
  types: Array<DocumentType>
}

export const LABEL_BY_DOCUMENT_TYPE: Record<DocumentType, string> = {
  [DocumentType.CC]: 'CC',
  [DocumentType.PLU]: 'PLU',
  [DocumentType.PLUI]: 'PLUi',
  [DocumentType.PLUIH]: 'PLUiH',
  [DocumentType.PLUIHM]: 'PLUiHM',
  [DocumentType.PLUIM]: 'PLUiM',
  [DocumentType.SCOT]: 'SCoT',
}

export const DOCUMENT_TYPES: Array<{
  label: string
  value: DocumentType
}> = [{
  label: LABEL_BY_DOCUMENT_TYPE[DocumentType.CC],
  value: DocumentType.CC,
}, {
  label: LABEL_BY_DOCUMENT_TYPE[DocumentType.PLU],
  value: DocumentType.PLU,
}, {
  label: LABEL_BY_DOCUMENT_TYPE[DocumentType.PLUI],
  value: DocumentType.PLUI,
}, {
  label: LABEL_BY_DOCUMENT_TYPE[DocumentType.PLUIH],
  value: DocumentType.PLUIH,
}, {
  label: LABEL_BY_DOCUMENT_TYPE[DocumentType.PLUIHM],
  value: DocumentType.PLUIHM,
}, {
  label: LABEL_BY_DOCUMENT_TYPE[DocumentType.PLUIM],
  value: DocumentType.PLUIM,
}, {
  label: LABEL_BY_DOCUMENT_TYPE[DocumentType.SCOT],
  value: DocumentType.SCOT,
}]

export const DOCUMENT_TYPES_GROUPS: Array<DocumentTypesGroup> = [{
  description: 'Plans locaux d\'urbanisme intercommunaux',
  id: 'plui',
  label: 'PLUi',
  types: [
    DocumentType.PLUI,
    DocumentType.PLUIH,
    DocumentType.PLUIHM,
    DocumentType.PLUIM,
  ],
}, {
  description: 'Documents d\'urbanisme communaux',
  id: '',
  label: 'DU communaux',
  types: [
    DocumentType.CC,
    DocumentType.PLU,
  ],
}, {
  description: 'Schémas de cohérence territoriale',
  id: 'scot',
  label: 'SCoT',
  types: [
    DocumentType.SCOT,
  ],
}]
