/* eslint-disable no-console */
const express = require('express')
const app = express()
app.use(express.json())
const { createClient } = require('@supabase/supabase-js')

const supabase = createClient('https://ixxbyuandbmplfnqtxyw.supabase.co', process.env.SUPABASE_ADMIN_KEY)
const sudocu = require('./modules/sudocu.js')
const sido = require('./modules/sido.js')

// app.get('/communes', (req, res) => {

// })

app.get('/documents/collectivites', async (req, res) => {
  try {
    const collectivites = await sido.getCollectivitiesDocumentsType()

    res.status(200).send(collectivites)
  } catch (err) {
    console.log('Error fetching all colectivities documents', err)
    res.status(400).send('')
  }
})

app.get('/collectivites/:code', async (req, res) => {
  try {
    const collectiviteDetails = await sudocu.getProceduresCollectivite(req.params.code)
    res.status(200).send(collectiviteDetails)
  } catch (error) {
    console.log(error)
    res.status(404).send(error)
  }
})

app.get('/sido_csv', async (req, res) => {
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

// app.get('/intercommunalites', (req, res) => {

// })

// app.get('/intercommunalites/:code', (req, res) => {

// })

app.get('/documents/count', async (req, res) => {
  try {
    const count = await sido.countDocuments(req.query)
    res.status(200).send({ count })
  } catch (err) {
    console.log('Error counting sido table', err)
    res.status(400).send(err)
  }
})

module.exports = app