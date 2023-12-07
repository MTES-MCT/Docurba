/* eslint-disable camelcase */

import { createClient } from '@supabase/supabase-js'
import { groupBy, uniq } from 'lodash'
import dayjs from 'dayjs'
import communes from '../Data/EnrichedCommunes.json'
import intercommunalites from '../Data/EnrichedIntercommunalites.json'
// import regions from '../Data/INSEE/regions.json'
import departements from '../Data/INSEE/departements.json'

// import enqueteData from '../../static/json/communes.json'

const supabase = createClient('https://ixxbyuandbmplfnqtxyw.supabase.co', process.env.SUPABASE_ADMIN_KEY)

const codeEtaMap = {
  RNU: '9',
  CC: '1',
  POS: '2',
  PLU: '3'
}

function getColectiviteCode (procedure) {
  if (!procedure || !procedure.current_perimetre || !procedure.current_perimetre.length) {
    // Pas de communes
    return '9'
  } else if (procedure.current_perimetre.length > 1) {
    if (procedure.is_sectoriel) {
      return '3'
    } else {
      return '2'
    }
  } else {
    return '1'
  }
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

function getStateColor (docTypes) {
  let color = '#FFFFFF'

  if (docTypes.includes('CC')) {
    color = '#2095CF'

    if (docTypes.includes('PLU')) {
      color = '#8EC581'
    } else if (docTypes.includes('PLUi')) {
      color = '#7F5279'
    }

    if (docTypes.includes('PLU') && docTypes.includes('PLUi')) {
      color = '#A88861'
    }
  } else if (docTypes.includes('PLU')) {
    color = '#FBF432'

    if (docTypes.includes('PLUi')) {
      color = '#EC812B'
    }
  } else if (docTypes.includes('PLUi')) {
    color = '#DD0E23'
  }

  return color
}

function findCollectivite (code) {
  const collectivite = intercommunalites.find(i => i.code === code) || communes.find(c => c.code === code)
  const departement = departements.find(d => d.code === collectivite.departementCode)
  const region = departement.region

  return { collectivite, departement, region }
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
  },
  async getCollectiviteState (collectiviteCode) {
    // const calculatedData = enqueteData.find(c => c.code_insee === collectiviteCode)

    // if (calculatedData) {
    //   console.log('alreadyCalculated', collectiviteCode)
    //   return calculatedData
    // }

    console.log('getCollectiviteState', collectiviteCode)

    const communeData = communes.find(c => c.code === collectiviteCode)

    function findEventByType (events, types, procedure_id) {
      return events.find((e) => {
        return (procedure_id ? e.procedure_id === procedure_id : true) &&
          types.includes(e.type)
      })
    }

    // const { collectivite, departement, region } = findCollectivite(collectiviteCode)

    // console.log(collectivite, departement, region)

    try {
      const { data: procedures, error } = await supabase.from('procedures').select('*')
        .contains('current_perimetre', `[{ "inseeCode": "${collectiviteCode}" }]`)
        .neq('doc_type', 'SCOT')

      const principalsProcedures = procedures.filter(p => p.is_principale)

      const opposableProcedure = principalsProcedures.find(p => p.status === 'opposable')
      const currentProcedures = principalsProcedures.filter(p => p.status === 'en cours')

      const { data: events } = await supabase.from('doc_frise_events').select('*')
        .in('procedure_id', principalsProcedures.map(p => p.id))

      events.sort((a, b) => {
        const dateB = +dayjs(a.date_iso)
        const dateA = +dayjs(b.date_iso)

        return dateA - dateB
      })

      const lastPrescriptionEvent = events.filter((e) => {
        const procedure = currentProcedures.find(p => p.id === e.procedure_id)
        return procedure && e.type === 'Prescription'
      })[0]

      // console.log('lastPrescriptionEvent', lastPrescriptionEvent)
      // console.log('opposableProcedure', opposableProcedure)

      const lastCurrentProcedure = lastPrescriptionEvent ? currentProcedures.find(p => p.id === lastPrescriptionEvent.procedure_id) : undefined

      // const groupedEvents = groupBy(events, e => e.procedure_id)

      const opposableDocType = opposableProcedure ? opposableProcedure.doc_type : 'RNU'
      const currentDocType = lastCurrentProcedure ? lastCurrentProcedure.doc_type : 'RNU'
      const codeEtat = `${codeEtaMap[opposableDocType]}${codeEtaMap[currentDocType]}`
      const codeEtat2 = `${codeEtaMap[opposableDocType]}${getColectiviteCode(opposableProcedure)}${codeEtaMap[currentDocType]}${getColectiviteCode(currentProcedures)}`

      const approbationEventsType = ["Délibération d'approbation", "Arrêté d'abrogation", "Arrêté du Maire ou du Préfet ou de l'EPCI", 'Approbation du préfet']

      const currentArretEvent = lastCurrentProcedure ? findEventByType(events, ['Arrêt de projet'], lastCurrentProcedure.id) : {}
      const currentPAC = lastCurrentProcedure ? findEventByType(events, ['Porter à connaissance'], lastCurrentProcedure.id) : {}
      const currentPACcomp = lastCurrentProcedure ? findEventByType(events, ['Porter à connaissance complémentaire'], lastCurrentProcedure.id) : {}

      const opposableEvents = opposableProcedure ? events.filter(e => e.procedure_id === opposableProcedure.id) : []
      const opposablePrescriptionEvent = opposableProcedure ? findEventByType(opposableEvents, ['Prescription'], opposableProcedure.id) : {}
      const opposableArretEvent = opposableProcedure ? findEventByType(opposableEvents, ['Arrêt de projet'], opposableProcedure.id) : {}
      const opposabelAprobationEvent = opposableProcedure ? findEventByType(opposableEvents, approbationEventsType, opposableProcedure.id) : {}
      const opposableExecutoireEvent = opposableProcedure ? findEventByType(opposableEvents, ['Caractère exécutoire'], opposableProcedure.id) : {}
      const opposablePAC = opposableProcedure ? findEventByType(opposableEvents, ['Porter à connaissance'], opposableProcedure.id) : {}
      const opposablePACcomp = opposableProcedure ? findEventByType(opposableEvents, ['Porter à connaissance complémentaire'], opposableProcedure.id) : {}

      // console.log(opposableExecutoireEvent)

      // const opposableRevisions = opposableEvents.filter(e => e.type.includes())
      const opposableSecondaryProcedures = opposableProcedure ? procedures.filter(p => p.secondary_procedure_of === opposableProcedure.id) : []

      const voletQualitatif = opposableProcedure ? opposableProcedure.volet_qualitatif : {}

      const typesCurrentProc = uniq(currentProcedures.map(p => `${p.doc_type}${(p.doc_type === 'PLU' && p.current_perimetre.length > 1) ? 'i' : ''}`))

      const revisions = currentProcedures.filter(p => ['Révision', 'Révision allégée (ou RMS)', 'Révision simplifiée'].includes(p.type))
      const modifications = currentProcedures.filter(p => ['Modification', 'Modification simplifiée'].includes(p.type))

      const collectivitePorteuseId = (lastCurrentProcedure || opposableProcedure || {
        collectivite_porteuse_id: communeData.competencePLU ? collectiviteCode : communeData.intercommunaliteCode
      }).collectivite_porteuse_id

      const opposableDocLabel = opposableProcedure ? `${opposableProcedure.doc_type}${opposableProcedure.current_perimetre.length > 1 ? 'i' : ''}` : 'RNU'
      const currentDocLabel = lastCurrentProcedure ? `${lastCurrentProcedure.doc_type}${lastCurrentProcedure.current_perimetre.length > 1 ? 'i' : ''}` : 'RNU'

      return {
        epci_reg: '',
        epci_region: '',
        epci_dept: '',
        epci_departement: '',
        epci_type: '',
        epci_nom: '',
        epci_siren: communeData.intercommunaliteCode,
        code_insee: collectiviteCode,
        com_nom: '',
        collectivite_porteuse_sudocuh: collectivitePorteuseId,
        collectivite_porteuse_banatic: communeData.competencePLU ? collectiviteCode : communeData.intercommunaliteCode,
        plan_etat_code1: codeEtat, //
        plan_libelle_etat_code1: codeEtatsLabels[codeEtat], //
        plan_code_etat_bcsi: codeEtat2, // Avoir le nouveau mode de calcul
        plan_libelle_code_etat_bcsi: '', // Avoir le nouveau mode de calcul
        types_pc: typesCurrentProc.join(' '),
        type_pc_color: getStateColor(typesCurrentProc),
        pc_num_procedure: lastCurrentProcedure?.from_sudocuh || '', //
        pc_nb_communes: lastCurrentProcedure?.current_perimetre.length || '', //
        pc_type_document: currentDocLabel || '', //
        pc_type_procedure: lastCurrentProcedure?.type || '', //
        pc_date_prescription: lastPrescriptionEvent?.date_iso || '', //
        pc_date_arret_projet: currentArretEvent?.date_iso || '', //
        pc_date_pac: currentPAC?.date_iso || '', //
        pc_date_pac_comp: currentPACcomp?.date_iso || '', //
        pc_plui_valant_scot: lastCurrentProcedure?.is_scot || '', //
        pc_pluih: lastCurrentProcedure?.is_pluih || false, //
        pc_pluih_num_procedure: '', // Pas de ref dans Docurba
        pc_sectoriel: lastCurrentProcedure?.is_sectoriel || false, //
        pc_pdu_tient_lieu: lastCurrentProcedure?.is_pdu || false, //
        pc_pdu_obligatoire: lastCurrentProcedure?.mandatory_pdu || false, //
        pc_psmv: '', //  A priori on l'a
        pc_type_moe: '', // A priori on l'a
        pc_nom_sst: '', // A priori on l'a
        pc_cout_sst_ht: '', // A priori on l'a
        pc_cout_sst_ttc: '', // A priori on l'a
        pa_num_procedure: opposableProcedure?.from_sudocuh || '', //
        pa_nb_communes: opposableProcedure?.current_perimetre.length || '', //
        pa_type_document: opposableDocLabel, //
        pa_type_procedure: opposableProcedure?.type || '', //
        pa_sectoriel: opposableProcedure?.is_sectoriel || false, //
        pa_date_prescription: opposablePrescriptionEvent?.date_iso || '', //
        pa_date_arret_projet: opposableArretEvent?.date_iso || '', //
        pa_date_pac: opposablePAC?.date_iso, //
        pa_date_pac_comp: opposablePACcomp?.date_iso, //
        pa_date_approbation: opposabelAprobationEvent?.date_iso || '', //
        pa_annee_prescription: opposablePrescriptionEvent?.date_iso ? dayjs(opposablePrescriptionEvent?.date_iso).format('YYYY') : '', //
        pa_annee_approbation: opposableExecutoireEvent?.date_iso ? dayjs(opposableExecutoireEvent?.date_iso).format('YYYY') : '', //
        pa_date_executoire: opposableExecutoireEvent?.date_iso || '', //
        pa_delai_approbation: dayjs(opposableExecutoireEvent?.date_iso).diff(opposablePrescriptionEvent?.date_iso, 'day'), //
        pa_plui_valant_scot: opposableProcedure?.is_scot || false, //
        pa_pluih: opposableProcedure?.is_pluih || false, //
        pa_pluih_num_procedure: '', // // Pas de ref dans Docurba
        pa_pdu_tient_lieu: opposableProcedure?.is_pdu || false, //
        pa_pdu_obligatoire: opposableProcedure?.mandatory_pdu || false, //
        pa_psmv: '', //  A priori on l'a
        pa_type_moe: '', // A priori on l'a
        pa_nom_sst: '', // A priori on l'a
        pa_cout_sst_ht: '', // A priori on l'a
        pa_cout_sst_ttc: '', // A priori on l'a
        proc_nb_revisions: revisions.length || '', //
        proc_nb_modifications: modifications.length || '', //
        proc_nb_proc_secondaires: opposableSecondaryProcedures.length || '', //

        /*
        Volet Qualitatif
        {
          "is_stecal": false,
          "nb_stecal": 0,
          "is_paysage": false,
          "is_patrimoine": false,
          "is_renvoi_rnu": false,
          "is_densite_mini": false,
          "is_entree_ville": false,
          "is_developpement": false,
          "is_environnement": false,
          "is_integ_loi_ene": false,
          "eval_environmental": 0,
          "is_renouvel_urbain": false,
          "is_comm_electronique": null,
          "is_lutte_insalubrite": false,
          "is_schema_amenagement": false,
          "is_aire_stationment_max": false,
          "is_peri_plafond_statmnt": false,
          "is_obligation_aire_statmnt": false,
          "is_schema_amenagement_ss_reg": false
        }
        */

        q_eval_environmnt: voletQualitatif?.eval_environmental || '', //
        q_integ_loi_ene: voletQualitatif?.is_integ_loi_ene || '', //
        q_environnement: voletQualitatif?.is_environnement || '', //
        q_paysage: voletQualitatif?.is_paysage || '', //
        q_entree_ville: voletQualitatif?.is_entree_ville || '', //
        q_patrimoine: voletQualitatif?.is_patrimoine || '', //
        q_lutte_insalubrite: voletQualitatif?.is_lutte_insalubrite || '', //
        q_renouvel_urbain: voletQualitatif?.is_renouvel_urbain || '', //
        q_developpement: voletQualitatif?.is_developpement || '', //
        q_mixite_fonctionnelle: '', // Ne pas prendre en compte
        q_ouverture_urbain: '', // A priori on l'a
        q_peri_plafond_statmnt: voletQualitatif?.is_peri_plafond_statmnt || '', //
        q_schema_amenagement: voletQualitatif?.is_schema_amenagement || '', //
        q_schema_amenagement_ss_reg: voletQualitatif?.is_schema_amenagement_ss_reg || '', //
        q_stecal: voletQualitatif?.is_stecal || '', //
        q_nb_stecal: voletQualitatif?.nb_stecal || '', //
        q_densite_mini: voletQualitatif?.is_densite_mini || '', //
        q_aire_stationment_max: voletQualitatif?.is_aire_stationment_max || '', //
        q_comm_electronique: voletQualitatif?.is_comm_electronique || '', //
        q_renvoi_rnu: voletQualitatif?.is_renvoi_rnu || '', //
        q_obligation_aire_statmnt: voletQualitatif?.is_obligation_aire_statmnt || '' //
      }
    } catch (err) {
      console.log('error', err)
      return {}
    }
  }
}
