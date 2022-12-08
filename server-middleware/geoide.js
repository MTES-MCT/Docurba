const express = require('express')
const app = express()
app.use(express.json())

const axios = require('axios')

const geoIdeParams = {
  _content_type: 'json',
  resultType: 'details',
  fast: 'index'
}

const PLATFORMS_BASE = {
  national: {
    baseUrl: 'http://catalogue.geo-ide.developpement-durable.gouv.fr',
    searchPath: '/catalogue/srv/eng/q'
  },
  bretagne: {
    baseUrl: 'https://geobretagne.fr',
    searchPath: '/geonetwork/srv/fre/q'
  }
}

// Should be /api/geoide/q from front.
app.get('/q', async (req, res) => {
  try {
    console.log('Platform back: ', req.query.platform)
    const platform = req.query.platform ?? 'national'

    delete req.query.platform
    const axiosParams = {
      method: 'get',
      // url: '/catalogue/srv/eng/q',
      url: PLATFORMS_BASE[platform].baseUrl + PLATFORMS_BASE[platform].searchPath,
      params: Object.assign({}, req.query, geoIdeParams)
    }

    const { data } = await axios(axiosParams)

    res.status(200).send(data)
  } catch (err) {
    res.status(400).send(err)
  }
})

module.exports = app
