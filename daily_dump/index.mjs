import CONFIG from './pg_secret_config.mjs'
import { clearDev, loadDump, createSudocuProcessedTables, setAllStatus, createOriginalSchema } from './steps/sqlRunner.mjs'
import { sudocuhPlanToDocurba } from './steps/4-interTablesToDocurbaPlan.mjs'
import { sudocuhScotToDocurba } from './steps/5-interTablesToDocurbaScot.mjs'
import { updatePerimeterStatus } from './steps/6-setPerimeterStatus.mjs'
import { updateComDPerimeter } from './steps/7-updateComdPerimTable.mjs'
import { handleTrigger } from './steps/onOffTriggers.mjs'

/// /////////////////////
/// ///// INFO ////////
/// /////////////////////

// You need to setup .pgpass in your home if you don't want to enter the db password on pg_restaure
// https://tableplus.com/blog/2019/09/how-to-use-pgpass-in-postgresql.html

try {
  /// ////////////////////////////////////////
  /// ///// PART 1 - Prepare the data ////////
  /// ////////////////////////////////////////

  // Step 0 (Optionnal)
  // await clearDev(CONFIG.PG_DEV_CONFIG)
  // // // // Step 1 - Charge un dump particulier venant de l'export de Andy sur notre storage
  // await loadDump(CONFIG.PG_DEV_CONFIG, '2024_06_10_dump')
  // // // // // Step 2 - Créer les tables intermédiaires d'aggregation depuis la donnée Sudocuh
  // await createSudocuProcessedTables(CONFIG.PG_DEV_CONFIG)
  // // // // // Replique un schema de test (Optionnal)
  // await createOriginalSchema(CONFIG.PG_DEV_CONFIG)
  // // // // // Step 3 - Désactive du trigger de changement de status sur nouveaux events
  // await handleTrigger(CONFIG.PG_PROD_CONFIG, 'disable')

  // /// /////////////////////////////////////////////////////////////
  // /// ///// PART 2 - Sudocuh to Docurba daily differential ////////
  // /// /////////////////////////////////////////////////////////////

  // // Step 4 - Migre les nouvelles données plan entrées dans Sudocuh dans Docurba
  // await sudocuhPlanToDocurba(CONFIG.PG_DEV_CONFIG, CONFIG.PG_PROD_CONFIG)
  // // // Step 5 - Migre les nouvelles données SCoT entrées dans Sudocuh dans Docurba
  // await sudocuhScotToDocurba(CONFIG.PG_DEV_CONFIG, CONFIG.PG_PROD_CONFIG)
  // // // Step 6 - Définition des status de procédures au niveau event
  // await setAllStatus(CONFIG.PG_PROD_CONFIG)
  // // Step 6(Bis) - Définition des status de procédures en fonction des périmètres
  await updatePerimeterStatus(CONFIG.PG_PROD_CONFIG)
  // // Step 7 - Ralliement des communes fusionnées
  // await updateComDPerimeter(CONFIG.PG_PROD_CONFIG)
  // // Step 8 - Réactivation du trigger de changement de status sur nouveaux events
  // await handleTrigger(CONFIG.PG_PROD_CONFIG, 'enable')
} catch (error) {
  console.log(error)
}
