import { mkdirSync } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import CONFIG from './database_config.mjs'
import { downloadDump } from './steps/1-downloadDump.mjs'
import { sudocuhPlanToDocurba } from './steps/4-interTablesToDocurbaPlan.mjs'
import { sudocuhScotToDocurba } from './steps/5-interTablesToDocurbaScot.mjs'
import { updatePerimeterStatus } from './steps/6-setPerimeterStatus.mjs'
import { migrateDgd } from './steps/8-migrateDgd.mjs'
import { handleTrigger } from './steps/onOffTriggers.mjs'
import {
  clearDev,
  createOriginalSchema,
  createSudocuProcessedTables,
  loadDump,
  setAllStatus
} from './steps/sqlRunner.mjs'
// import { updateProcedureSec } from './updateProcedureSec.mjs'
const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

mkdirSync(path.join(__dirname, 'sudocuh_dumps'), { recursive: true })
CONFIG.PG_DEV_CONFIG.user = process.env.DEV_SUPABASE_USER
CONFIG.PG_DEV_CONFIG.admin_key = process.env.DEV_SUPABASE_ADMIN_KEY
CONFIG.PG_DEV_CONFIG.password = process.env.DEV_SUPABASE_PASSWORD
CONFIG.PG_PROD_CONFIG.user = process.env.PROD_SUPABASE_USER
CONFIG.PG_PROD_CONFIG.admin_key = process.env.PROD_SUPABASE_ADMIN_KEY
CONFIG.PG_PROD_CONFIG.password = process.env.PROD_SUPABASE_PASSWORD

/// /////////////////////
/// ///// INFO ////////
/// /////////////////////
const latestDumpName = await downloadDump(CONFIG.PG_PROD_CONFIG, __dirname)

// You need to setup .pgpass in your home if you don't want to enter the db password on pg_restaure
// https://tableplus.com/blog/2019/09/how-to-use-pgpass-in-postgresql.html

/// ////////////////////////////////////////
/// ///// PART 1 - Prepare the data ////////
/// ////////////////////////////////////////

// Step 0 (Optionnal)
await clearDev(CONFIG.PG_DEV_CONFIG)
// // // // // Step 1 - Charge un dump particulier venant de l'export de Andy sur notre storage

await loadDump(CONFIG.PG_DEV_CONFIG, latestDumpName)
// // // // // // Step 2 - Créer les tables intermédiaires d'aggregation depuis la donnée Sudocuh
await createSudocuProcessedTables(CONFIG.PG_DEV_CONFIG)
// // // // // // Replique un schema de test (Optionnal)
await createOriginalSchema(CONFIG.PG_DEV_CONFIG)
// // // // // // Step 3 - Désactive du trigger de changement de status sur nouveaux events
await handleTrigger(CONFIG.PG_PROD_CONFIG, 'disable')

// // /// /////////////////////////////////////////////////////////////
// // /// ///// PART 2 - Sudocuh to Docurba daily differential ////////
// // /// /////////////////////////////////////////////////////////////

// // // Step 4 - Migre les nouvelles données plan entrées dans Sudocuh dans Docurba
await sudocuhPlanToDocurba(CONFIG.PG_DEV_CONFIG, CONFIG.PG_PROD_CONFIG)
// // // // Step 5 - Migre les nouvelles données SCoT entrées dans Sudocuh dans Docurba
await sudocuhScotToDocurba(CONFIG.PG_DEV_CONFIG, CONFIG.PG_PROD_CONFIG)
// // // // Step 6 - Définition des status de procédures au niveau event
await setAllStatus(CONFIG.PG_PROD_CONFIG)
// // Step 6(Bis) - Définition des status de procédures en fonction des périmètres
await updatePerimeterStatus(CONFIG.PG_PROD_CONFIG)
// // Step 7 - Ralliement des communes fusionnées
// await updateComDPerimeter(CONFIG.PG_PROD_CONFIG)
//
await migrateDgd(CONFIG.PG_DEV_CONFIG, CONFIG.PG_PROD_CONFIG)
// // Step 8 - Réactivation du trigger de changement de status sur nouveaux events
await handleTrigger(CONFIG.PG_PROD_CONFIG, 'enable')

// Pour une raison que nous ne connaissons pas, le process Node ne se termine pas.
// process.exit le force.
process.exit(0)
