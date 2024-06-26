export default {
  annee_cog: 'cog',
  code_insee: 'code',
  com_nom: 'intitule',
  com_code_departement: 'departementCode',
  com_nom_departement: 'departement.intitule',
  com_code_region: 'regionCode',
  com_nom_region: 'region.intitule',
  com_nouvelle: 'nouvelle',
  epci_reg: 'intercommunalite.regionCode',
  epci_region: 'intercommunalite.region.intitule',
  epci_dept: 'intercommunalite.departementCode',
  epci_departement: 'intercommunalite.departement.intitule',
  epci_type: 'intercommunalite.type',
  epci_nom: 'intercommunalite.intitule',
  epci_siren: 'intercommunalite.code',
  collectivite_porteuse: 'collectivitePorteuse',
  cp_type: 'porteuse.type',
  cp_code_region: 'porteuse.regionCode',
  cp_lib_region: 'porteuse.departement.region.intitule',
  cp_code_departement: 'porteuse.departementCode',
  cp_nom_departement: 'porteuse.departement.intitule',
  cp_nom: 'porteuse.intitule',
  cp_siren: 'porteuse.siren',
  cp_code_insee: 'porteuse.insee',
  // collectivite_porteuse_banatic: ''
  plan_code_etat_simplifie: 'sudocuhCodes.etat.code', //
  plan_libelle_code_etat_simplifie: 'sudocuhCodes.etat.label', //
  // plan_etat_code2: 'sudocuhCodes.etat2.code', //
  // plan_libelle_etat_code2: 'sudocuhCodes.etat2.label', //
  plan_code_etat_complet: 'sudocuhCodes.bcsi.code',
  plan_libelle_code_etat_complet: 'sudocuhCodes.bcsi.label',
  types_pc: 'currentsDocTypes',
  // type_pc_color: getStateColor(typesCurrentProc),
  pc_docurba_id: 'planCurrent.id',
  pc_num_procedure_sudocuh: 'planCurrent.from_sudocuh', //
  pc_nb_communes: 'planCurrent.current_perimetre.length',
  pc_type_document: 'planCurrent.docType',
  pc_type_procedure: 'planCurrent.type',
  pc_date_prescription: 'planCurrent.prescription.date_iso',
  pc_date_arret_projet: 'planCurrent.arret.date_iso',
  pc_date_pac: 'planCurrent.pac.date_iso',
  pc_date_pac_comp: 'planCurrent.pacComp.date_iso',
  pc_plui_valant_scot: 'planCurrent.is_scot',
  pc_pluih: 'planCurrent.is_pluih',
  // pc_pluih_num_procedure: '', // Pas de ref dans Docurba
  pc_sectoriel: 'planCurrent.isSectoriel',
  pc_pdu_tient_lieu: 'planCurrent.is_pdu',
  pc_pdu_obligatoire: 'planCurrent.mandatory_pdu',
  // {
  //   "coutplanht": null,
  //   "coutplanttc": null,
  //   "nomprestaexterne": ""
  // }
  // pc_psmv: '', //  A priori on l'a
  // pc_type_moe: '', // A priori on l'a
  pc_nom_sst: 'planCurrent.moe.nomprestaexterne',
  pc_cout_sst_ht: 'planCurrent.moe.coutplanht',
  pc_cout_sst_ttc: 'planCurrent.moe.coutplanttc',
  pc_trajectoire_ZAN: '',
  pc_zone_acceleration_ENR: '',
  pc_trait_de_cote: '',
  pc_feu_de_foret: '',
  pc_autre: '',
  pa_docurba_id: 'planOpposable.id',
  pa_num_procedure_sudocuh: 'planOpposable.from_sudocuh',
  pa_nb_communes: 'planOpposable.current_perimetre.length',
  pa_type_document: 'planOpposable.docType', //
  pa_type_procedure: 'planOpposable.type',
  pa_sectoriel: 'planOpposable.isSectoriel',
  pa_date_prescription: 'planOpposable.prescription.date_iso', //
  pa_date_arret_projet: 'planOpposable.arret.date_iso', //
  pa_date_pac: 'planOpposable.pac.date_iso', //
  pa_date_pac_comp: 'planOpposable.pacComp.date_iso', //
  pa_date_approbation: 'planOpposable.approbation.date_iso', //
  pa_annee_prescription: 'planOpposable.prescription.year', //
  pa_annee_approbation: 'planOpposable.approbation.year', //
  pa_date_executoire: 'planOpposable.exec.date_iso', //
  pa_delai_approbation: 'planOpposable.approbationDelay', //
  pa_plui_valant_scot: 'planOpposable.is_scot', //
  pa_pluih: 'planOpposable.is_pluih', //
  // pa_pluih_num_procedure_sudocuh: '', // // Pas de ref dans Docurba
  pa_pdu_tient_lieu: 'planOpposable.is_pdu', //
  pa_pdu_obligatoire: 'planOpposable.mandatory_pdu', //
  // pa_psmv: '', //  A priori on l'a
  // pa_type_moe: '', // A priori on l'a
  pa_nom_sst: 'planOpposable.moe.nomprestaexterne',
  pa_cout_sst_ht: 'planOpposable.moe.coutplanht',
  pa_cout_sst_ttc: 'planOpposable.moe.coutplanttc',
  pa_trajectoire_ZAN: '',
  pa_zone_acceleration_ENR: '',
  pa_trait_de_cote: '',
  pa_feu_de_foret: '',
  pa_autre: '',
  proc_nb_revisions: 'revisions.length', //
  proc_nb_modifications: 'modifications.length', //
  // proc_nb_proc_secondaires: opposableSecondaryProcedures.length,
  q_eval_environmnt: 'planOpposable.volet_qualitatif.eval_environmental' //
  // q_integ_loi_ene: 'planOpposable.volet_qualitatif.is_integ_loi_ene', //
  // q_environnement: 'planOpposable.volet_qualitatif.is_environnement', //
  // q_paysage: 'planOpposable.volet_qualitatif.is_paysage', //
  // q_entree_ville: 'planOpposable.volet_qualitatif.is_entree_ville', //
  // q_patrimoine: 'planOpposable.volet_qualitatif.is_patrimoine', //
  // q_lutte_insalubrite: 'planOpposable.volet_qualitatif.is_lutte_insalubrite', //
  // q_renouvel_urbain: 'planOpposable.volet_qualitatif.is_renouvel_urbain', //
  // q_developpement: 'planOpposable.volet_qualitatif.is_developpement', //
  // // q_mixite_fonctionnelle: '', // Ne pas prendre en compte
  // // q_ouverture_urbain: '', // A priori on l'a
  // q_peri_plafond_statmnt: 'planOpposable.volet_qualitatif.is_peri_plafond_statmnt', //
  // q_schema_amenagement: 'planOpposable.volet_qualitatif.is_schema_amenagement', //
  // q_schema_amenagement_ss_reg: 'planOpposable.volet_qualitatif.is_schema_amenagement_ss_reg', //
  // q_stecal: 'planOpposable.volet_qualitatif.is_stecal', //
  // q_nb_stecal: 'planOpposable.volet_qualitatif.nb_stecal', //
  // q_densite_mini: 'planOpposable.volet_qualitatif.is_densite_mini', //
  // q_aire_stationment_max: 'planOpposable.volet_qualitatif.is_aire_stationment_max', //
  // q_comm_electronique: 'planOpposable.volet_qualitatif.is_comm_electronique', //
  // q_renvoi_rnu: 'planOpposable.volet_qualitatif.is_renvoi_rnu', //
  // q_obligation_aire_statmnt: 'planOpposable.volet_qualitatif.is_obligation_aire_statmnt' //
}

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
