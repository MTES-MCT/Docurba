/* eslint-disable no-console */
const github = require('./github.js')

async function getFileContent (path, ref, format = 'raw') {
  // console.log('Get File', format, path)

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
        file.children = await getFiles(file.path, ref, fetchContent === 'all' ? fetchContent : false)
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

module.exports = {
  getFileContent,
  getFiles
}