import CONFIG from './pg_secret_config.mjs'
import { clearDev, loadDump, createSudocuProcessedTables, setAllStatus, createOriginalSchema } from './steps/sqlRunner.mjs'
import { sudocuhPlanToDocurba } from './steps/4-interTablesToDocurbaPlan.mjs'
// import { sudocuhScotToDocurba } from './steps/5-interTablesToDocurbaScot.mjs'
// import { updateComDPerimeter } from './steps/7-setPerimeterStatus.mjs'
// import { updatePerimeterStatus } from './steps/8-updateComdPerimTable.mjs'
import { handleTrigger } from './steps/onOffTriggers.mjs'

/// /////////////////////
/// ///// INFO ////////
/// /////////////////////

// You need to setup .pgpass in your home if you don't want to enter the db password on pg_restaure
// https://tableplus.com/blog/2019/09/how-to-use-pgpass-in-postgresql.html

try {
  /// /////////////////////
  /// ///// PART 1 ////////
  /// /////////////////////

  // TODO: On ne clearDev pas si jamais on veux test
  // await clearDev(CONFIG.PG_DEV_CONFIG)
  // await loadDump(CONFIG.PG_DEV_CONFIG, '2024_03_03_dump')
  // await createSudocuProcessedTables(CONFIG.PG_DEV_CONFIG)

  // // Useful only on DEV for test purpose.
  // await createOriginalSchema(CONFIG.PG_DEV_CONFIG)
  // await handleTrigger(CONFIG.PG_DEV_CONFIG, 'disable')

  /// /////////////////////
  /// ///// PART 2 ////////
  /// /////////////////////

  await sudocuhPlanToDocurba(CONFIG.PG_DEV_CONFIG, CONFIG.PG_DEV_CONFIG)

  // await sudocuhScotToDocurba(CONFIG.PG_DEV_CONFIG, CONFIG.PG_DEV_CONFIG)
  // await setAllStatus(CONFIG.PG_DEV_CONFIG)
  // TODO: Script de Fabien pour les communes fusionnées
  // updateComDPerimeter(CONFIG.PG_DEV_CONFIG)
  // TODO: Script de Fabien pour setup les status des perimetres
  // updatePerimeterStatus(CONFIG.PG_DEV_CONFIG)
  // await handleTrigger(CONFIG.PG_DEV_CONFIG, 'enable')
} catch (error) {
  console.log(error)
}
