const express = require('express')
const app = express()
app.use(express.json())

const axios = require('axios')

const geoIde = axios.create({
  baseURL: 'http://catalogue.geo-ide.developpement-durable.gouv.fr'
})

const geoIdeParams = {
  _content_type: 'json',
  resultType: 'details',
  fast: 'index'
}

// Should be /api/geoide/q from front.
app.get('/q', async (req, res) => {
  try {
    const { data } = await geoIde({
      method: 'get',
      url: '/catalogue/srv/eng/q',
      params: Object.assign({}, req.query, geoIdeParams)
    })

    res.status(200).send(data)
  } catch (err) {
    res.status(400).send(err)
  }
})

module.exports = app
