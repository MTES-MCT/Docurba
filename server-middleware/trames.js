/* eslint-disable no-console */
const express = require('express')
const admin = require('./modules/admin.js')
const github = require('./modules/github.js')

const app = express()

app.use(express.json())

// https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28#create-or-update-file-contents
/* commit:
{
  path: section path string,
  content: b64 string of content,
  sha: sha1 from reading the edited file
}
*/

async function getAllowedRole (userId, ref) {
  const userRoles = await admin.getUserAdminRoles(userId)
  const roles = userRoles.deptRoles.concat(userRoles.regionRoles)

  return roles.find(role => role.dept === ref || role.region === ref)
}

app.post('/:ref', async (req, res) => {
  const { ref } = req.params
  const { userId, commit } = req.body

  const allowedRole = await getAllowedRole(userId, ref)

  console.log(commit.path)

  // if (allowedRole) {
  // We assign the branch and commiter manually to make sure it cannot be overide in commit.
  // Someone miss using a userId should not be able to modify anithing else than what this userId is allowed.
  const commitRes = await github(`PUT /repos/UngererFabien/France-PAC/contents/${encodeURIComponent(commit.path)}`, Object.assign({}, commit, {
    branch: ref,
    committer: {
      name: 'Fabien', // allowedRole.user_email.replace(/@(.*)/, ''),
      email: 'fabien.ungerer@gmail.com' // allowedRole.user_email
    },
    message: `${commit.sha ? 'Edit' : 'Create'} ${commit.path} for ${ref} from Docurba`
  }))

  console.log(commitRes)

  res.status(200).send(commitRes)
  // } else {
  // res.status(403).send(`User not allowed to edit ${ref} trame.`)
  // }
})

app.delete('/:ref', async (req, res) => {
  const { ref } = req.params
  const { userId, commit } = req.body

  const allowedRole = await getAllowedRole(userId, ref)

  const commitRes = await github(`DELETE /repos/UngererFabien/France-PAC/contents/${encodeURIComponent(commit.path)}`, Object.assign({}, commit, {
    branch: ref,
    committer: {
      name: 'Fabien', // allowedRole.user_email.replace(/@(.*)/, ''),
      email: 'fabien.ungerer@gmail.com' // allowedRole.user_email
    },
    message: `Delete ${commit.path} for ${ref} from Docurba`
  }))

  console.log(commitRes)

  res.status(200).send(commitRes)
})

async function getFileContent (path, ref) {
  const { data: file } = await github(`GET /repos/UngererFabien/France-PAC/contents${encodeURIComponent(path)}?ref=${ref}`, {
    path,
    mediaType: {
      format: 'raw'
    }
  })

  // console.log(file)

  return file
}

async function getFiles (path, ref) {
  const { data: repo } = await github(`GET /repos/UngererFabien/France-PAC/contents${encodeURIComponent(path)}?ref=${ref}`, {
    path
  })

  try {
    await Promise.all(repo.map(async (file) => {
      file.name = file.name.replace('.md', '')

      if (file.type === 'dir') {
        file.children = await getFiles(file.path, ref)

        const intro = file.children.find(child => child.name === 'intro')

        // if intro is not found. It might be impossible to delete the folder in the UI.
        // Also clicking on the folder will fail to fetch a file intro.md.
        // TODO: if there is no intro.md we should create it ?
        if (intro) { file.sha = intro.sha }

        file.children = file.children.filter((child) => {
          return child.name !== 'intro'
        })
      }
      // else {
      //   file.content = await getFileContent(file.path, ref)
      // }

      return file.children
    }))
  } catch (err) {
    console.log(err)
  }

  return repo
}

app.get('/tree/:ref', async (req, res) => {
  // test should be replaced by region code.
  const repo = await getFiles('/PAC', req.params.ref)

  // if (!error) {
  res.status(200).send(repo)
  // } else {
  //   // eslint-disable-next-line no-console
  //   console.log('error reading github:', error)
  //   req.status(400).send(error)
  // }
})

app.get('/file', async (req, res) => {
  try {
    const { path, ref } = req.query

    // console.log('GET FILE CONTENT:', path)

    const file = await getFileContent(path, ref)

    res.status(200).send(file)
  } catch (err) {
    console.log(err)
    res.status(400).send(err)
  }
})

module.exports = app
