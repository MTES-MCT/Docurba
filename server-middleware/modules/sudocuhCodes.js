import groupements from '../Data/referentiels/groupements.json'
import BCSI from './Data/BCSI.json'

const codeEtaMap = {
  RNU: '9',
  CC: '1',
  POS: '2',
  PLU: '3',
  PLUi: '3',
  PLUiH: '3'
}

const codeEtatsLabels = {
  99: 'RNU ',
  91: 'CC en élaboration ',
  92: 'POS en élaboration ',
  93: 'PLU en élaboration',
  19: 'CC approuvée ',
  11: 'CC en révision ',
  13: 'CC approuvée – PLU en élaboration ',
  29: 'POS approuvé',
  21: 'POS approuvé - CC en élaboration',
  22: 'POS en révision ',
  23: 'POS approuvé - PLU en révision',
  39: 'PLU approuvé',
  31: 'PLU approuvé - CC en élaboration',
  33: 'PLU en révision'
}

function getProcedureType (procedure) {
  return procedure ? (procedure.doc_type || 'RNU') : 'RNU'
}

function getProcedureCode2 (procedure, porteuseId) {
  if (!procedure || !procedure.current_perimetre || !procedure.current_perimetre.length) {
    // Pas de communes
    return '9'
  } else if (procedure.current_perimetre.length > 1) {
    const group = groupements.find(g => g.code === porteuseId)
    const isSectoriel = group ? group.membres.filter(m => m.type === 'COM').length > procedure.current_perimetre.length : procedure.is_sectoriel
    if (isSectoriel) {
    // if (procedure.is_sectoriel) {
      return '3'
    } else {
      return '2'
    }
  } else {
    return '1'
  }
}

function getCodeComp (procedure, porteuseId) {
  if (!procedure || !procedure.collectivite_porteuse_id) { return '9' }

  const isEPCI = porteuseId.length > 5

  if (isEPCI) {
    if (procedure.current_perimetre.length > 1) {
      const group = groupements.find(g => g.code === porteuseId)
      const isSectoriel = group ? group.membres.filter(m => m.type === 'COM').length > procedure.current_perimetre.length : procedure.is_sectoriel
      if (isSectoriel) {
        return '3'
      }

      return '2'
    } else {
      return '4'
    }
  } else { return '1' }
}

export default {
  getCodeEtat (planOpposable, planCurrent) {
    const code = `${codeEtaMap[getProcedureType(planOpposable)]}${codeEtaMap[getProcedureType(planCurrent)]}`
    return {
      code,
      label: codeEtatsLabels[code]
    }
  },
  getCodeEtat2 (planOpposable, planCurrent, collectivitePorteuse) {
    const opposableCode = `${codeEtaMap[getProcedureType(planOpposable)]}${getProcedureCode2(planOpposable, collectivitePorteuse)}`
    const currentCode = `${codeEtaMap[getProcedureType(planCurrent)]}${getProcedureCode2(planCurrent, collectivitePorteuse)}`

    return { code: `${opposableCode}${currentCode}`, label: '' }
  },
  getCodeBcsi (planOpposable, planCurrent, collectivitePorteuse) {
    // console.log(getProcedureType(planOpposable), planOpposable)

    const codeOpposable = `${codeEtaMap[getProcedureType(planOpposable)]}${getCodeComp(planOpposable, collectivitePorteuse)}`
    const codeEnCour = `${codeEtaMap[getProcedureType(planCurrent)]}${getCodeComp(planCurrent, collectivitePorteuse)}`

    const code = `${codeOpposable}${codeEnCour}`

    return {
      code,
      label: BCSI.du_codeEtat[code]?.Lib_EtatD
    }
  },
  getAllCodes (planOpposable, planCurrent, collectivitePorteuse) {
    return {
      etat: this.getCodeEtat(planOpposable, planCurrent),
      etat2: this.getCodeEtat2(planOpposable, planCurrent, collectivitePorteuse),
      bcsi: this.getCodeBcsi(planOpposable, planCurrent, collectivitePorteuse)
    }
  },
  getCodesScot (scot) {
    let simple = ''

    if (scot.status === 'opposable') {
      simple = '30'
    } else if (scot.status === 'en cours') {
      if (scot.type === 'Révision') {
        simple = '20'
      } else {
        simple = '5'
      }
    }

    let detail = '2'

    if (scot.status === 'en cours') {
      if (scot.deliberation) {
        detail = '3'
      }

      if (scot.arret) {
        detail = '4'
      }
    }

    return {
      simple,
      detailed: `${simple}${detail}`
    }
  }
}
