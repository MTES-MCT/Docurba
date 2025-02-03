import fs from 'fs'
import pg from 'pg'
const { Client } = pg

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
    '4-trigger_event_procedure_status_handler.sql'
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

export { createSudocuProcessedTables }
