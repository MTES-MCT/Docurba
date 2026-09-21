/* eslint-disable no-console */
import { AsyncParser } from '@json2csv/node'

// GEO DATA
import express from 'express'
import allCommunes from './Data/referentiels/communes.json'
import groupements from './Data/referentiels/groupements.json'

const csvParser = new AsyncParser()

const app = express()
app.use(express.json())

app.get('/exports/gpu/maillages', async (req, res) => {
  const groupementsCompetents = groupements.filter(
    groupement => groupement.competencePLU || groupement.competenceSCOT
  )
  const collectivites = [...allCommunes, ...groupementsCompetents]

  const mapedCommunes = collectivites.map((c) => {
    const parents = []
    if (c.departementCode) {
      parents.push(c.departementCode)
    }
    if (c.intercommunaliteCode) {
      parents.push(c.intercommunaliteCode)
    }
    if (c.codeParent) {
      parents.push(c.codeParent)
    }

    return {
      name: c.code,
      title: c.intitule,
      type: c.type,
      parents: parents.join(' '),
      administered_by: c.code.length > 5 ? c.departementCode : '',
      competencePLU: c.competencePLU,
      competenceSCOT: c.competenceSCOT
    }
  })

  const csv = await csvParser.parse(mapedCommunes).promise()
  res.status(200).type('text/csv').send(csv)
})

module.exports = app
