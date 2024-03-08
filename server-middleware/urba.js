/* eslint-disable no-console */
import { AsyncParser } from '@json2csv/node'

import express from 'express'
import { mapValues, get } from 'lodash'
import procedures from './modules/procedures.js'
import departements from './Data/INSEE/departements.json'

import sudocuhCommunes from './modules/exportMaps/sudocuhCommunes.js'

const csvParser = new AsyncParser()

const app = express()
app.use(express.json())

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

app.get('/exports/communes', async (req, res) => {
  const inseeCodes = req.body.inseeCodes
  const communes = await procedures.getCommunes(inseeCodes)

  if (req.query.csv) {
    const mapedCommunes = communes.map((c) => {
      return mapValues(sudocuhCommunes, key => get(c, key, ''))
    })

    const csv = await csvParser.parse(mapedCommunes).promise()
    res.status(200).send(csv)
  } else {
    res.status(200).send(communes)
  }
})

app.get('/exports/communes/:inseeCode', async (req, res) => {
  const commune = await procedures.getCommune(req.params.inseeCode)

  res.status(200).send(mapValues(sudocuhCommunes, key => get(commune, key, '')))
})

module.exports = app
