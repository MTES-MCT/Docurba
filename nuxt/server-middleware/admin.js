const express = require('express')
const app = express()
app.use(express.json())

const issues = require('./modules/github/issues.js')
const { requireRefRoles } = require('./modules/auth.js')

app.post('/help/pac', async (req, res) => {
  try {
    await requireRefRoles(req, ['write'])
  } catch (error) {
    return res.status(403).send({ message: error.message })
  }

  const { title, message, email, ref, path } = req.body
  await issues.createIssue(title, message, email, ref, path)
  res.status(200).send('OK')
})

module.exports = app
