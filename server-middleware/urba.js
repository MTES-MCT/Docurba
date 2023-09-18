const express = require('express')
const app = express()
app.use(express.json())

const sudocu = require('./modules/sudocu.js')

// app.get('/communes', (req, res) => {

// })

app.get('/collectivites/:code', async (req, res) => {
  try {
    const collectiviteDetails = await sudocu.getProceduresCollectivite(req.params.code)
    res.status(200).send(collectiviteDetails)
  } catch (error) {
    console.log(error)
    res.status(404).send(error)
  }
})

// app.get('/intercommunalites', (req, res) => {

// })

// app.get('/intercommunalites/:code', (req, res) => {

// })

module.exports = app
