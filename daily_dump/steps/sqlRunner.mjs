import fs from 'fs'
import pg from 'pg'
import { execute } from '@getvim/execute'
const { Client } = pg

async function clearDev (config) {
  try {
    const client = new Client(config)
    await client.connect()
    console.log('Clearing Docurba DEV database...')
    const sql = fs.readFileSync('./daily_dump/steps/sql/miscs/0-clearDevSchema.sql')
      .toString().replace(/(\r\n|\n|\r)/gm, ' ')
      .replace(/\s+/g, ' ')
    await client.query(sql)
    console.log('Docurba Dev Cleared.')
  } catch (error) {
    console.log(error)
  }
}

async function loadDump (config, dumpName) {
  try {
    console.log('[TODO] - Download the dump.')
    // TODO: Download the latest dump auto 2024_03_03_dump
    console.log('Restoring latest Sudocuh dump...')
    await execute(`pg_restore -h ${config.host} -d ${config.database} -U ${config.user} ./daily_dump/sudocuh_dumps/${dumpName}`)
    console.log('Sudocuh dump Restored.')
  } catch (error) {
    console.log(error)
  }
}

async function createSudocuProcessedTables (config) {
  const SQLS = [
    '1-EventsDetails.sql',
    '2-CollectiviteDetails.sql',
    '3-PerimetreProcedures.sql',
    '4-PerimetreSchema.sql',
    '5-ProcedurePlan.sql',
    '6-ProcedureSchemaDetails.sql',
    '7-PlanEvents.sql',
    '8-ScotEvents.sql'
    // TODO: Rajouter DGD
    // '9-InfosDgdProcedures.sql'
  ]
  try {
    const client = new Client(config)
    await client.connect()

    for (const sqlFilename of SQLS) {
      console.log(`Processing ${sqlFilename}...`)
      const sql = fs.readFileSync(`./daily_dump/steps/sql/inter_tables/${sqlFilename}`)
        .toString().replace(/(\r\n|\n|\r)/gm, ' ')
        .replace(/\s+/g, ' ')
      await client.query(sql)
    }
    await client.end()
    console.log('Intermediate tables written.')
  } catch (error) {
    console.log(error)
  }
}

async function setAllStatus (config) {
  const SQLS = [
    '1-get_event_impact.sql',
    '2-set_procedure_status.sql',
    '3-set_all_procedures_status.sql',
    '4-trigger_event_procedure_status_handler.sql',
    '5-run_status.sql',
    '6-trigger_definition.sql'
    // 'rpc_events_by_procedures_ids.sql',
    // 'rpc_procedures_by_insee_codes.sql'
  ]
  try {
    const client = new Client(config)
    await client.connect()

    console.log('Starting procedure status update.')
    for (const sqlFilename of SQLS) {
      console.log(`Processing ${sqlFilename}...`)
      const sql = fs.readFileSync(`./daily_dump/steps/sql/status_handler/${sqlFilename}`)
        .toString().replace(/(\r\n|\n|\r)/gm, ' ')
        .replace(/\s+/g, ' ')
      await client.query(sql)
    }
    await client.end()
    console.log('Procedures status updated.')
  } catch (error) {
    console.log(error)
  }
}

async function createOriginalSchema (config) {
  const SQLS = [
    '1-projects.sql',
    '2-procedures.sql',
    '3-procedures_perimetres.sql',
    '4-doc_frise_events.sql',
    '5-rules.sql'
  ]
  try {
    const client = new Client(config)
    await client.connect()

    console.log('Starting creating tables schema and relationships.')
    for (const sqlFilename of SQLS) {
      console.log(`Processing ${sqlFilename}...`)
      const sql = fs.readFileSync(`./daily_dump/steps/sql/original_schema/${sqlFilename}`)
        .toString().replace(/(\r\n|\n|\r)/gm, ' ')
        .replace(/\s+/g, ' ')
      await client.query(sql)
    }
    await client.end()
    console.log('Tables and relationships created.')
  } catch (error) {
    console.log(error)
  }
}

export { clearDev, loadDump, createSudocuProcessedTables, setAllStatus, createOriginalSchema }
