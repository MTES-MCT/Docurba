/* eslint-disable camelcase */

const { createClient } = require('@supabase/supabase-js')
const communes = require('../Data/EnrichedCommunes.json')
const intercommunalites = require('../Data/EnrichedIntercommunalites.json')
// const regions = require('../Data/INSEE/regions.json')
const departements = require('../Data/INSEE/departements.json')

const supabase = createClient('https://ixxbyuandbmplfnqtxyw.supabase.co', process.env.SUPABASE_ADMIN_KEY)

const codeEtaMap = {
  RNU: '9',
  CC: '1',
  POS: '2',
  PLU: '3'
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
  21: 'POS approuvé CC en élaboration',
  22: 'POS en révision ',
  23: 'POS approuvé PLU en révision',
  39: 'PLU approuvé',
  31: 'PLU approuvé CC en élaboration',
  33: 'PLU en révision'
}

module.exports = {
  async getCommuneState (communeCode) {
    const commune = communes.find(c => c.code === communeCode)
    const intercomunalite = intercommunalites.find(i => i.code === commune.intercommunaliteCode)
    const departement = departements.find(d => d.code === commune.departementCode)
    const region = departement.region

    // Fetch Historical Sudocuh Data
    const { data: [{ id_procedure_approved, id_procedure_ongoing }] } = await supabase.from('sudocu_procedures_etats')
      .select('id_procedure_approved, id_procedure_ongoing').eq('insee_code', commune.code)

    // console.log('id_procedure_approved', id_procedure_approved, 'id_procedure_ongoing', id_procedure_ongoing)

    const { data: codetypedocuments } = await supabase.from('distinct_procedures_events')
      .select('noserieprocedure, codetypedocument').in('noserieprocedure', [id_procedure_approved, id_procedure_ongoing].filter(i => !!i))

    // console.log('codetypedocuments', codetypedocuments)

    const approvedDu = codetypedocuments.find(d => d.noserieprocedure === id_procedure_approved)
    const ongoingDu = codetypedocuments.find(d => d.noserieprocedure === id_procedure_ongoing)

    const approvedDuType = approvedDu.codetypedocument || 'RNU'
    const ongoingDuType = ongoingDu ? ongoingDu.codetypedocument : ''

    const { data: ongoingPerimeters } = await supabase.from('sudocu_procedures_perimetres')
      .select('nb_communes').eq('procedure_id', id_procedure_ongoing)

    // console.log('perimeter', id_procedure_ongoing, ongoingPerimeters)

    const perimeterLength = ongoingPerimeters ? ongoingPerimeters[0].nb_communes : null

    const state_code = codeEtaMap[approvedDuType] + codeEtaMap[ongoingDuType || 'RNU']

    return {
      // Missing: ANNE_COG
      region_name: region.intitule, // eq: EPCI_REGION2016
      interco_departement_code: intercomunalite.departementCode, // eq: EPCI_DEPT
      commune_departement_code: commune.departementCode, // eq: INSEE_DEPT
      commune_name: commune.intitule, // eq: INSEE_COMMUNE
      interco_siren: commune.intercommunaliteCode, // eq: EPCI_SIREN
      interco_name: intercomunalite.intitule, // eq: EPCI_NOM
      interco_competence_scot: intercomunalite.competences.scot, // ADDED
      interco_competence_secteur: intercomunalite.competences.secteur, // ADDED
      interco_competence_plu: intercomunalite.competences.plu, // ADDED
      commune_du_opposable: approvedDuType || 'RNU', // eq: DU_OPPOSABLE
      commune_du_in_progress: (ongoingDuType + (perimeterLength ? 'i' : '')) || '', // ADDED
      state_code, // eq: DU_CODE_ETATS
      state_label: codeEtatsLabels[state_code] // eq: DU_LIBELLE_ETATS
    }
  },
  async getIntercomunaliteState (intercoCode) {
    const intercomunalite = intercommunalites.find(i => i.code === intercoCode)
    const communes = intercomunalite.filter(c => c.type === 'Commune')
    const departement = departements.find(d => d.code === intercomunalite.departementCode)

    for (let index = 0; index < communes.length; index++) {
      const commune = communes[index]

      if (!commune.state) {
        commune.state = await this.getCommuneState(commune.code)
      }
    }

    return {
      region_name: departement.region.intitule, // eq: Région de l'EPCI
      departement_code: intercomunalite.departementCode, // eq: Dépt EPCI
      juridique_type: intercomunalite.labelJuridique, // eq: Type EPCI
      intercomunalite_namme: intercomunalite.intitule, // eq: Nom EPCI
      intercomunalite_code: intercomunalite.code, // eq: SIREN EPCI
      intercomunalite_nb_communes: communes.length // eq: Nb communes
      // Missing Superficies
      // Missing PLUiH true/false
      // Missing Tien lieu de PDU

    }
  }
}
