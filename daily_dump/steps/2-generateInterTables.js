
// import dotenv from 'dotenv'

(async () => {
  const fs = require('fs')
  const { Client } = require('pg')
  const { PG_DEV_CONFIG } = require('./pg_secret_config.json')

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

  async function createSudocuProcessedTables (config) {
    try {
      console.log(`Starting createSudocuProcessedTables for: ${JSON.stringify(config)}`)
      const client = new Client(config)
      await client.connect()

      for (const sqlFilename of SQLS) {
        console.log(`Processing ${sqlFilename}...`)
        const sql = fs.readFileSync(`./database/sql2/${sqlFilename}`)
          .toString().replace(/(\r\n|\n|\r)/gm, ' ')
          .replace(/\s+/g, ' ')
        const ret = await client.query(sql)
        console.log(`Result for file ${sqlFilename}: `, ret)
      }
      await client.end()
    } catch (error) {
      console.log(error)
    }
  }
  await createSudocuProcessedTables(PG_DEV_CONFIG)
})()
