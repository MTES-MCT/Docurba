
// import dotenv from 'dotenv'

(async () => {
  const { execute } = require('@getvim/execute')
  const { PG_DEV_CONFIG } = require('./pg_secret_config.json')

  async function loadDump (config) {
    try {
      // TODO: Clear DEV with sql script
      const test = await execute(`pg_restore -h ${config.host} -d ${config.database} -U ${config.user} ./database/dump/2024_03_03_dump`)
      console.log('Restored: ', test)
    } catch (error) {
      console.log(error)
    }
  }

  await loadDump(PG_DEV_CONFIG)
})()
