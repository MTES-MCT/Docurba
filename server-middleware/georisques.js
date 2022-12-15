const express = require('express')
const app = express()
app.use(express.json())
const axios = require('axios')
const GEORISQUES_MAP = require('../assets/data/GeoRisquesMap.json')

const geoRisques = axios.create({
  baseURL: 'https://www.georisques.gouv.fr/api/v1'
})

const geoRisquesParams = {
  page: 1,
  page_size: 10
}

app.get('/q', async (req, res) => {
  try {
    console.log('GEORISQUES_MAP: ', GEORISQUES_MAP)
    // const proms = []
    // GEORISQUES_MAP.forEach((e) => {
    //   const prom = geoRisques({
    //     method: 'get',
    //     url: '/' + e.endpoint,
    //     params: Object.assign({ code_insee: req.query.insee }, geoRisquesParams)
    //   })
    //   proms.push(prom)
    // })
    // const allData = await Promise.all(proms)
    // const structuredRisques = allData.map((e, i) => {
    //   return {
    //     type: GEORISQUES_MAP[i],
    //     data: e.data
    //   }
    // })
    // console.log('allData: ', structuredRisques)
    const { data } = await geoRisques({
      method: 'get',
      url: '/' + req.query.dataset,
      params: Object.assign({ code_insee: req.query.insee }, geoRisquesParams)
    })
    console.log('data: ', data)
    // res.set('Cache-Control', 'public, max-age=3600')
    // res.status(200).send({ success: true })
    res.status(200).send(data)
  } catch (err) {
    console.log(err.message)
    res.status(400).send(err)
  }
})

module.exports = app
