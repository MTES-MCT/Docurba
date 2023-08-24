const express = require('express')
const app = express()
app.use(express.json())

app.get('/communes', (req, res) => {

})

app.get('/communes/:code', (req, res) => {

})

app.get('/intercommunalites', (req, res) => {

})

app.get('/intercommunalites/:code', (req, res) => {

})

module.exports = app
