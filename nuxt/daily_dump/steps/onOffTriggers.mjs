import fs from 'fs'
import pg from 'pg'
const { Client } = pg

async function handleTrigger (config, state) {
  try {
    const client = new Client(config)
    await client.connect()
    console.log(`Starting ${state} triggers...`)
    const sql = fs.readFileSync(`./daily_dump/steps/sql/on_off_triggers/${state === 'disable' ? '1' : '2'}-${state}_trigger.sql`)
      .toString().replace(/(\r\n|\n|\r)/gm, ' ')
      .replace(/\s+/g, ' ')
    await client.query(sql)

    await client.end()
    console.log(`Triggers ${state}.`)
  } catch (error) {
    console.log(error)
  }
}
export { handleTrigger }
