/* eslint-disable no-console */
const express = require('express')
const admin = require('./modules/admin.js')
const github = require('./modules/github/github.js')
const tree = require('./modules/github/tree.js')

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

app.post('/:ref', async (req, res) => {
  const { ref } = req.params
  const { commit } = req.body

  // Front is trying to update a section. But someone could be editing this section as well.
  // So the front can't guarantee its sha is correct.
  if (commit.sha) {
    const currentFile = await getFileContent(commit.path, ref, 'object')

    console.log('currentFile', commit.path)
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

async function getFileContent (path, ref, format = 'raw') {
  try {
    const { data: file } = await github(`GET /repos/UngererFabien/France-PAC/contents${encodeURIComponent(path)}?ref=${ref}`, {
      path,
      mediaType: {
        format
      }
    })

    // console.log('no error', file)

    return file
  } catch (err) {
    // If a file was saved as intro instead of intro.md we have this fail safe.
    // Need to clean all the branches to change that.
    const { data: file } = await github(`GET /repos/UngererFabien/France-PAC/contents${encodeURIComponent(path.replace('.md', ''))}?ref=${ref}`, {
      path,
      mediaType: {
        format
      }
    })

    // console.log('error', file)

    return file
  }
}

async function getFiles (path, ref, fetchContent = false) {
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
        if (intro) {
          file.introSha = intro.sha
          if (fetchContent) {
            file.content = await getFileContent(intro.path, ref)
          }
        }

        file.children = file.children.filter((child) => {
          return child.name !== 'intro'
        })
      } else if (fetchContent) {
        file.content = await getFileContent(file.path, ref)
      }

      return file.children
    }))
  } catch (err) {
    console.log(err)
  }

  return repo
}

app.get('/tree/:ref', async (req, res) => {
  const { content } = req.query
  // test should be replaced by region code.
  try {
    const repo = await getFiles('/PAC', req.params.ref, content)

    // if (!error) {
    res.status(200).send(repo)
  } catch (err) {
    console.log('Error getting tree', err, err.status)
  }
  // } else {
  //   // eslint-disable-next-line no-console
  //   console.log('error reading github:', error)
  //   req.status(400).send(error)
  // }
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

app.get('/compare', async (req, res) => {
  try {
    const { basehead } = req.query

    // https://docs.github.com/en/rest/commits/commits?apiVersion=2022-11-28#compare-two-commits
    const { data } = await github(`GET /repos/UngererFabien/France-PAC/compare/${basehead}`, {
      basehead,
      per_page: 10,
      page: 1
    })

    res.send(data.files)
  } catch (err) {
    console.log('err in compare', err)
  }
})

module.exports = app
