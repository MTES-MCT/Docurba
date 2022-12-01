const express = require('express')
const app = express()
app.use(express.json())

const axios = require('axios')

const geoRisques = axios.create({
  baseURL: 'https://www.georisques.gouv.fr/api/v1'
})

const geoRisquesParams = {
  page: 1,
  page_size: 10
}

app.get('/q', async (req, res) => {
  try {
    const { data } = await geoRisques({
      method: 'get',
      url: '/' + req.query.dataset,
      params: Object.assign({ code_insee: req.query.insee }, geoRisquesParams)
    })
    console.log('data: ', data)
    res.status(200).send(data)
  } catch (err) {
    console.log(err.message)
    res.status(400).send(err)
  }
})

module.exports = app
