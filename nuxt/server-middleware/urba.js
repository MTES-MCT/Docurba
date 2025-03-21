/* eslint-disable no-console */
import { AsyncParser } from '@json2csv/node'

// GEO DATA
import express from 'express'
import { mapValues, get, uniq } from 'lodash'
import allCommunes from './Data/referentiels/communes.json'
import groupements from './Data/referentiels/groupements.json'
import departements from './Data/INSEE/departements.json'

import procedures from './modules/procedures.js'
import supabase from './modules/supabase.js'

// exports maps
import prescriptionsMap from './modules/exportMaps/prescriptions.js'
import sudocuhCommunes from './modules/exportMaps/sudocuhCommunes.js'

const csvParser = new AsyncParser()

const app = express()
app.use(express.json())

// TOTO: Pour le dump journalier - connecter a la base de dev
app.get('/departements/:code', async (req, res) => {
  const communesCodes = departements.find(d => d.code === req.params.code).communes.map(c => c.code)
  const communes = await procedures.getCommunes(communesCodes)

  res.status(200).send(communes)
})

app.get('/communes/:inseeCode', async (req, res) => {
  const commune = await procedures.getCommune(req.params.inseeCode)
  res.status(200).send(commune)
})

app.get('/exports/departements/:code', async (req, res) => {
  const departement = departements.find(d => d.code === req.params.code)

  await supabase.from('analytics_events').insert([{
    user_id: null,
    category: 'api',
    name: 'exports communes',
    value: req.fullPath,
    path: req.fullPath,
    dept: req.params.code,
    region: departement.region.code
  }])

  if (req.query.csv) {
    res.redirect(`https://nuxt3.docurba.incubateur.net/api/urba/exports/communes?departementCode=${req.params.code}`)
    // const csv = await csvParser.parse(mapedCommunes).promise()
    // res.status(200).attachment(`${req.params.code}_${departement.intitule}.csv`).send(csv)
  } else {
    const communesCodes = departement.communes.map(c => c.code)
    const communes = await procedures.getCommunes(communesCodes)

    const mapedCommunes = communes.map((c) => {
      return mapValues(sudocuhCommunes, key => get(c, key, ''))
    })
    res.status(200).send(mapedCommunes)
  }
})

app.get('/exports/communes', async (req, res) => {
  const inseeCodes = req.body.inseeCodes
  const communes = await procedures.getCommunes(inseeCodes)

  const mapedCommunes = communes.map((c) => {
    return mapValues(sudocuhCommunes, key => get(c, key, ''))
  })

  if (req.query.csv) {
    const csv = await csvParser.parse(mapedCommunes).promise()
    res.status(200).attachment('communes.csv').send(csv)
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
