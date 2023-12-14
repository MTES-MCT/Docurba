/* eslint-disable no-console */
const express = require('express')
const admin = require('./modules/admin.js')
const github = require('./modules/github/github.js')
const tree = require('./modules/github/tree.js')
const { getFileContent, getFiles, addGhostSections } = require('./modules/github/files.js')

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

app.post('/projects/:parentRef', async (req, res) => {
  const { parentRef } = req.params
  const { userId, projectId } = req.body

  const { data: parentBranch } = await github(`GET /repos/UngererFabien/France-PAC/git/ref/heads/${parentRef}`, {
    ref: parentRef
  })

  try {
    const newProjectBranch = await github('POST /repos/UngererFabien/France-PAC/git/refs', {
      ref: `refs/heads/projet-${projectId}`,
      sha: parentBranch.object.sha
    })

    res.status(200).send(newProjectBranch)
  } catch (err) {
    res.status(400).send(err)
  }
})

app.put('/:ref/copy', async (req, res) => {
  const { path, ghostRef } = req.body
  // test should be replaced by region code.
  try {
    await tree.copy(req.params.ref, ghostRef, path)
    res.status(200).end()
  } catch (err) {
    console.log('Error getting tree', err, err.status)
  }
})

app.post('/:ref', async (req, res) => {
  const { ref } = req.params
  const { commit } = req.body

  // Front is trying to update a section. But someone could be editing this section as well.
  // So the front can't guarantee its sha is correct.
  if (commit.sha) {
    const currentFile = await getFileContent(commit.path, ref, 'object')

    // console.log('currentFile', commit.path)
    // console.log('currentFile', currentFile)

    commit.sha = currentFile.sha
  }

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

  res.status(200).send(commitRes)
})

app.delete('/:ref', async (req, res) => {
  const { ref } = req.params
  const { userId, commit } = req.body

  const commitRes = await github(`DELETE /repos/UngererFabien/France-PAC/contents/${encodeURIComponent(commit.path)}`, Object.assign({}, commit, {
    branch: ref,
    committer: {
      name: 'Fabien', // allowedRole.user_email.replace(/@(.*)/, ''),
      email: 'fabien.ungerer@gmail.com' // allowedRole.user_email
    },
    message: `Delete ${commit.path} for ${ref} from Docurba`
  }))

  res.status(200).send(commitRes)
})

app.get('/tree/:ref', async (req, res) => {
  const { content, ghostRef, path = 'PAC' } = req.query

  try {
    if (content) {
      const repo = await getFiles('/PAC', req.params.ref, content)
      res.status(200).send(repo)
      return
    }

    const [repo, ghostRepo] = await Promise.all([
      tree.getTree(req.params.ref, path),
      ghostRef ? tree.getTree(ghostRef, path) : undefined
    ])

    if (ghostRef) {
      addGhostSections(repo, ghostRepo)
    }

    res.status(200).send(repo)
  } catch (err) {
    console.log('Error getting tree', err, err.status)
  }
})

app.post('/tree/:ref', async (req, res) => {
  const { section, newName } = req.body

  try {
    await tree.changeName(req.params.ref, section, newName)
    res.status(200).send('OK')
  } catch (err) {
    console.log(err)
    res.status(400).send(err)
  }
})

app.get('/file', async (req, res) => {
  try {
    const { path, ref } = req.query

    // console.log('GET FILE CONTENT:', path)

    const file = await getFileContent(path, ref)

    res.status(200).send(file)
  } catch (err) {
    console.log('error getting file', err)
    res.status(400).send(err)
  }
})

app.get('/history', async (req, res) => {
  try {
    const { path, ref } = req.query

    const { data: commits } = await github('GET /repos/{owner}/{repo}/commits', {
      path,
      sha: ref,
      per_page: 1
    })

    res.status(200).send(commits[0])
  } catch (err) {
    console.log('error getting history', err)
    res.status(400).send(err)
  }
})

app.get('/compare', async (req, res) => {
  try {
    const { basehead } = req.query

    // https://docs.github.com/en/rest/commits/commits?apiVersion=2022-11-28#compare-two-commits
    const { data } = await github(`GET /repos/UngererFabien/France-PAC/compare/${basehead}`, {
      basehead,
      per_page: 10,
      page: 1
    })

    res.send(data)
  } catch (err) {
    console.log('err in compare', err)
  }
})

module.exports = app
