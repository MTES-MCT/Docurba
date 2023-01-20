const express = require('express')
const admin = require('./modules/admin.js')
const github = require('./modules/github.js')

const app = express()

app.use(express.json())

// https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28#create-or-update-file-contents
/* commit:
{
  path: section path string,
  committer: {
    name: user name string,
    email: user email string
  },
  content: b64 string of content,
  sha: sha1 from reading the edited file
}
*/
app.post('/regions/:regionCode', async (req, res) => {
  const { regionCode } = req.params
  const { userId, commit } = req.body

  const userRoles = await admin.getUserAdminRoles(userId)
  const isAllowed = !!userRoles.find(role => role.region === regionCode)

  if (isAllowed) {
    github(commit)
  } else {
    res.status(403).send(`User not allowed to edit region ${regionCode} trame.`)
  }
})

app.post('/departement/:departementCode', async (req, res) => {
  const { departementCode } = req.params
  const { userId, commit } = req.body

  const userRoles = await admin.getUserAdminRoles(userId)
  const isAllowed = !!userRoles.find(role => role.dept === departementCode)

  if (isAllowed) {
    // We assign the branch manually to make sure it cannot be overide in commit.
    // Someone miss using a userId should not be able to modify anithing else than what this userId is allowed.
    github(`PUT /repos/UngererFabien/France-PAC/contents/${commit.path}`, Object.assign({}, commit, {
      branch: `departement-${departementCode}`
    }))
  } else {
    res.status(403).send(`User not allowed to edit region ${departementCode} trame.`)
  }
})

async function getFileContent (path, ref) {
  const { data: file } = await github(`GET /repos/UngererFabien/France-PAC/contents${path}?ref=${ref}`, {
    path
  })

  return file.content
}

async function getFiles (path, ref) {
  const { data: repo } = await github(`GET /repos/UngererFabien/France-PAC/contents${path}?ref=${ref}`, {
    path
  })

  try {
    await Promise.all(repo.map(async (file) => {
      file.name = file.name.replace('.md', '')

      if (file.type === 'dir') {
        file.children = (await getFiles(file.path, ref)).filter((child) => {
          return child.name !== 'intro'
        })
      }
      // else {
      //   file.content = await getFileContent(file.path, ref)
      // }

      return file.children
    }))
  } catch (err) {
    // eslint-disable-next-line no-console
    console.log(err)
  }

  return repo
}

app.get('/regions/:regionCode', async (req, res) => {
  // test should be replaced by region code.
  const repo = await getFiles('/Trame', 'test')

  // if (!error) {
  res.status(200).send(repo)
  // } else {
  //   // eslint-disable-next-line no-console
  //   console.log('error reading github:', error)
  //   req.status(400).send(error)
  // }
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
