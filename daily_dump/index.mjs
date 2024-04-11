import CONFIG from './pg_secret_config.mjs'
import { clearDev, loadDump, createSudocuProcessedTables, setAllStatus, createOriginalSchema } from './steps/sqlRunner.mjs'
import { sudocuhPlanToDocurba } from './steps/4-interTablesToDocurba.mjs'
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

  await clearDev(CONFIG.PG_DEV_CONFIG)
  await loadDump(CONFIG.PG_DEV_CONFIG, '2024_03_03_dump')
  await createSudocuProcessedTables(CONFIG.PG_DEV_CONFIG)
  await createOriginalSchema(CONFIG.PG_DEV_CONFIG)

  // TODO: Cibler le bon trigger sur la prod en tant voulu dans les sql scripts
  // TODO: Faire un if exist dans le cas ou il n'existe pas encore (cas du full process)
  await handleTrigger(CONFIG.PG_DEV_CONFIG, 'disable')

  /// /////////////////////
  /// ///// PART 2 ////////
  /// /////////////////////

  await sudocuhPlanToDocurba(CONFIG.PG_DEV_CONFIG, CONFIG.PG_DEV_CONFIG)
  // await sudocuhScotToDocurba(CONFIG.PG_DEV_CONFIG, CONFIG.PG_DEV_CONFIG)
  // await setAllStatus(CONFIG.PG_DEV_CONFIG)
  // TODO: Launch one_shot_event pour avoir les status
  // TODO: Script de Fabien pour setup les status des perimetres

  /// /////////////////////
  /// ///// PART 3 ////////
  /// /////////////////////

  // await handleTrigger(CONFIG.PG_DEV_CONFIG, 'enable')
} catch (error) {
  console.log(error)
}
