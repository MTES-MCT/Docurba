const express = require('express')
const admin = require('./modules/admin.js')
const github = require('./modules/github.js')

const app = express()

app.use(express.json())

app.post('/regions/:regionCode', async (req, res) => {
  const { regionCode } = req.params
  const { userId, githubReq } = req.body

  const userRoles = await admin.getUserAdminRoles(userId)
  const isAllowed = !!userRoles.find(role => role.region === regionCode)

  if (isAllowed) {
    github(githubReq)
  } else {
    res.status(403).send(`User not allowed to edit region ${regionCode} trame.`)
  }
})

app.post('/departement/:departementCode', async (req, res) => {
  const { departementCode } = req.params
  const { userId, githubReq } = req.body

  const userRoles = await admin.getUserAdminRoles(userId)
  const isAllowed = !!userRoles.find(role => role.dept === departementCode)

  if (isAllowed) {
    github(githubReq)
  } else {
    res.status(403).send(`User not allowed to edit region ${departementCode} trame.`)
  }
})

app.get('/regions/:regionCode', async (req, res) => {
  const { data, error } = await github('GET /repos/UngererFabien/France-PAC/contents/Trame?ref=test', {
    path: 'Trame'
  })

  if (!error) {
    res.status(200).send(data)
  } else {
    // eslint-disable-next-line no-console
    console.log('error reading github:', error)
    req.status(400).send(error)
  }
})

app.get('/departements/:departementCode/', async (req, res) => {
  const { data, error } = await github('GET /repos/UngererFabien/France-PAC/contents/Trame?ref=test', {
    path: 'Trame'
  })

  if (!error) {
    res.status(200).send(data)
  } else {
    res.status(400).send(error)
  }
})

app.get('/document/:documentId/', async (req, res) => {
  const { data, error } = await github('GET /repos/UngererFabien/France-PAC/contents/Trame?ref=test', {
    path: 'Trame'
  })

  if (!error) {
    res.status(200).send(data)
  } else {
    res.status(400).send(error)
  }
})

module.exports = app
