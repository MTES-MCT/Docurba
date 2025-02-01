const express = require('express')
const app = express()
app.use(express.json())

const issues = require('./modules/github/issues.js')

app.post('/help/pac', async (req, res) => {
  const { title, message, email, ref, path } = req.body
  await issues.createIssue(title, message, email, ref, path)
  res.status(200).send('OK')
})

module.exports = app
