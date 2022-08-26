/* eslint-disable no-console */
const express = require('express')
const app = express()
app.use(express.json())

// const pipedrive = require('./modules/pipedrive.js')
// console.log(pipedrive)

// pipedrive.signup({
//   email: 'docurba_2@quantedsquare.com',
//   firstname: 'John',
//   lastname: 'Doe',
//   dept: {
//     code_departement: 'TEST_2',
//     nom_departement: 'TEST',
//     code_region: 84,
//     nom_region: 'Auvergne-Rhône-Alpes'
//   }
// })

// pipedrive.findPerson('sandrine.belloeil@puy-de-dome.gouv.fr')
// pipedrive.findOrganization(63)

// console.log('TEST')

// const pipedrive = require('pipedrive')

// const defaultClient = pipedrive.ApiClient.instance

// // Configure API key authorization: apiToken
// const apiToken = defaultClient.authentications.api_key
// apiToken.apiKey = '0dbcadd138e23efe28575e5ae98dbbdc8c194594'

// const DealsApi = new pipedrive.DealsApi()

// DealsApi.getDeals().then((deals) => {
//   console.log('Pipedrive Deals', deals)
// }).catch(err => console.log(err))

// const dealFieldsApi = new pipedrive.DealFieldsApi()

// dealFieldsApi.getDealFields().then((fields) => {
//   console.log(fields)
// }).catch(err => console.log(err))

module.exports = app
