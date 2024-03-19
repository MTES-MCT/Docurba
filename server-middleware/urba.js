import { AsyncParser } from '@json2csv/node'

/* eslint-disable no-console */
import express from 'express'
import { mapValues, get, uniq } from 'lodash'
import supabase from './modules/supabase.js'
import urba from './modules/urba.js'
import sido from './modules/sido.js'
import procedures from './modules/procedures.js'
import departements from './Data/INSEE/departements.json'

// exports maps
import prescriptionsMap from './modules/exportMaps/prescriptions.js'
import sudocuhCommunes from './modules/exportMaps/sudocuhCommunes.js'

const csvParser = new AsyncParser()

const app = express()
app.use(express.json())

app.get('/documents/collectivites', async (req, res) => {
  try {
    const collectivites = await sido.getCollectivitiesDocumentsType()

    res.status(200).send(collectivites)
  } catch (err) {
    console.log('Error fetching all colectivities documents', err)
    res.status(400).send('')
  }
})

app.get('/sido_csv', async (req, res) => {
  console.log('OKOKOK')
  const sidoQuery = supabase.from('sido').select('*')
  if (req.query.communes) {
    const { data } = await sidoQuery.eq('collectivite_type', 'Commune').csv()
    res.send(data)
  } else if (req.query.epcis) {
    const { data } = await sidoQuery.neq('collectivite_type', 'Commune').csv()
    res.send(data)
  } else {
    const { data } = await sidoQuery.csv()
    res.send(data)
  }
})

app.get('/documents/count', async (req, res) => {
  try {
    const count = await sido.countDocuments(req.query)
    res.status(200).send({ count })
  } catch (err) {
    console.log('Error counting sido table', err)
    res.status(400).send(err)
  }
})

app.get('/state/:collectiviteCode', async (req, res) => {
  // console.log('/state/:collectiviteCode')

  try {
    const collectiviteState = await urba.getCollectiviteState(req.params.collectiviteCode)
    res.status(200).send(collectiviteState)
  } catch (err) {
    console.log('error', err)
    res.status(400).send(err)
  }
})

app.get('/exports/departements/:code', async (req, res) => {
  const communesCodes = departements.find(d => d.code === req.params.code).communes.map(c => c.code)
  const communes = await procedures.getCommunes(communesCodes)

  const mapedCommunes = communes.map((c) => {
    return mapValues(sudocuhCommunes, key => get(c, key, ''))
  })

  if (req.query.csv) {
    const csv = await csvParser.parse(mapedCommunes).promise()
    res.status(200).send(csv)
  } else {
    res.status(200).send(mapedCommunes)
  }
})

app.get('/exports/communes/:inseeCode', async (req, res) => {
  const commune = await procedures.getCommune(req.params.inseeCode)
  res.status(200).send(mapValues(sudocuhCommunes, key => get(commune, key, '')))
})

app.get('/exports/prescriptions', async (req, res) => {
  const { data: prescriptions } = await supabase.from('prescriptions').select('*')

  if (req.query.csv) {
    const mappedPrescriptions = prescriptions.map((prescription) => {
      return mapValues(prescriptionsMap, key => get(prescription, key, ''))
    })

    const csv = await csvParser.parse(mappedPrescriptions).promise()
    res.status(200).attachment('prescriptions.csv').send(csv)
  } else {
    res.status(200).send(prescriptions)
  }
})

module.exports = app
