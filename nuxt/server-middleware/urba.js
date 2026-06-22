/* eslint-disable no-console */
import { AsyncParser } from '@json2csv/node'

// GEO DATA
import express from 'express'
import { mapValues, get, uniq } from 'lodash'
import allCommunes from './Data/referentiels/communes.json'
import groupements from './Data/referentiels/groupements.json'

import supabase from './modules/supabase.js'

// exports maps
import prescriptionsMap from './modules/exportMaps/prescriptions.js'

const csvParser = new AsyncParser()

const app = express()
app.use(express.json())

app.get('/exports/prescriptions', async (req, res) => {
  const { data: prescriptions } = await supabase.from('prescriptions').select('*')

  const userIds = uniq(prescriptions.map(p => p.user_id).filter(id => !!id))
  const { data: profiles } = await supabase.from('profiles').select('*').in('user_id', userIds)

  prescriptions.forEach((p) => {
    p.profile = profiles.find(profile => p.user_id === profile.user_id)
  })

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
