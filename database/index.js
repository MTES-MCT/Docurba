
// import dotenv from 'dotenv'

(async () => {
  const fs = require('fs')
  const { Client } = require('pg')
  const { execute } = require('@getvim/execute')
  const { PG_TEST_CONFIG, PG_DEV_CONFIG, PG_PROD_CONFIG } = require('./pg_secret_config.json')

  const SQLS = [
    '1-EventsDetails.sql',
    '2-CollectiviteDetails.sql',
    '3-ProcedurePlanDetails.sql',
    '4-ProcedureSchemaDetails.sql',
    '5-PlanEvents.sql',
    '6-ScotEvents.sql',
    '7-PerimetreProcedures.sql',
    '8-PerimetreSchema.sql',
    '9-InfosDgdProcedures.sql'
  ]

  const TABLES_TO_EXPORT = ['sudocu_procedure_events', 'sudocu_schemas_events', 'sudocu_procedures_perimetres', 'sudocu_procedures_infosdgd']
  const OUTPUTDIR = '/tmp/sudocudump'

  async function createSudocuProcessedTables (config) {
    try {
      console.log(`Starting createSudocuProcessedTables for: ${JSON.stringify(config)}`)
      const client = new Client(config)
      await client.connect()

      for (const sqlFilename of SQLS) {
        console.log(`Processing ${sqlFilename}...`)
        const sql = fs.readFileSync(`./database/sql/${sqlFilename}`)
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

  async function exportProcessedSudocu (config) {
    try {
      console.log(`Start exporting Processed Sudocu to: ${OUTPUTDIR}`)
      for (const tableName of TABLES_TO_EXPORT) {
        console.log(tableName)
        await execute(`PGPASSWORD="${config.password}" pg_dump -h ${config.host} -p ${config.port} -d ${config.database} -U ${config.user} --table public.${tableName} -Fc --verbose --file "${OUTPUTDIR}/${tableName}"`)
        console.log(`${tableName} exported.`)
      }
    } catch (error) {
      console.error(error)
    }
  }

  async function importToDocurba (config) {
    try {
      console.log(`Start importing to Docurba from table dump: ${OUTPUTDIR}`)
      // TODO: Maybe delete the existing table in Docurba first ?
      const client = new Client(config)
      await client.connect()
      // await client.query(`
      // DROP materialized view IF EXISTS distinct_procedures_events;
      // DROP materialized view IF EXISTS distinct_procedures_schema_events;
      // `)

      for (const tableName of TABLES_TO_EXPORT) {
        console.log(tableName)
        await execute(`PGPASSWORD="${config.password}" pg_restore --clean -h ${config.host} -p ${config.port} -d ${config.database} -U ${config.user} -t ${tableName} -Fc ${OUTPUTDIR}/${tableName}`)
        console.log(`${tableName} imported.`)
      }

      await createMaterializedViewProcedures(config)
    } catch (error) {
      console.error(error)
    }
  }

  async function createMaterializedViewProcedures (config) {
    const client = new Client(config)
    await client.connect()
    console.log('Creating MV...')

    const mv1Sql = fs.readFileSync('./database/sql/D1-MVPlanProcedures.sql').toString().replace(/(\r\n|\n|\r)/gm, ' ').replace(/\s+/g, ' ')
    const mv2Sql = fs.readFileSync('./database/sql/D2-MVSchemaProcedures.sql').toString().replace(/(\r\n|\n|\r)/gm, ' ').replace(/\s+/g, ' ')
    await client.query(mv1Sql)
    await client.query(mv2Sql)
    console.log('Materialized View Done.')
  }

  async function loadDump (config) {
    try {
      // DROP SCHEMA sudocu CASCADE;
      // DROP SCHEMA public CASCADE;
      // grant usage on schema public to postgres, anon, authenticated, service_role;
      // grant select on all tables in schema public to postgres, anon, authenticated, service_role, supabase_admin;
      const test = await execute(`pg_restore -h ${config.host} -d ${config.database} -U ${config.user} ./database/dump/2023_12_13_dump`)
      console.log('Restored: ', test)
    } catch (error) {
      console.log(error)
    }
  }

  await loadDump(PG_DEV_CONFIG)

  await createSudocuProcessedTables(PG_DEV_CONFIG)
  await createMaterializedViewProcedures(PG_DEV_CONFIG)

  // await exportProcessedSudocu(PG_TEST_CONFIG)
  // await importToDocurba(PG_PROD_CONFIG)
  // console.log('PG_TEST_CONFIG: ', PG_TEST_CONFIG)
})()
