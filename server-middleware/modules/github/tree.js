/* eslint-disable no-console */
const github = require('./github.js')

module.exports = {
  async changeName (ref, section, newName) {
    // console.log(ref, section, newName)

    const { data: head } = await github(`GET /repos/UngererFabien/France-PAC/git/ref/heads/${ref}`, {
      ref
    })

    console.log(head)

    const baseTree = head.object.sha

    const nameIndex = section.path.lastIndexOf(section.name)
    const newPath = `${section.path.substring(0, nameIndex)}${newName}${section.type === 'file' ? '.md' : ''}`

    console.log(section.path)

    try {
    // https://docs.github.com/en/rest/git/trees?apiVersion=2022-11-28#create-a-tree
      const newTree = await github('POST /repos/{owner}/{repo}/git/trees', {
        base_tree: baseTree,
        tree: [{
          path: newPath,
          mode: section.type === 'dir' ? '040000' : '100644',
          type: section.type === 'dir' ? 'tree' : 'blob',
          sha: section.sha // This will duplicate all subfiles.
        }, {
          path: section.path,
          mode: section.type === 'dir' ? '040000' : '100644',
          type: section.type === 'dir' ? 'tree' : 'blob',
          sha: null // this delete the previous version.
        }]
      })

      console.log('new tree:', newTree)
    } catch (err) {
      console.log(err)
    }

    // const { data: commit } = await github('POST /repos/{owner}/{repo}/git/commits', {
    //   message: `Change ${section.path} to ${newPath}`,
    //   tree: newTree.sha,
    //   parents: [baseTree]
    // })

    // console.log('commit:', commit)

    // try {
    //   const merge = await github(`PATCH /repos/{owner}/{repo}/git/refs/heads/${ref}`, {
    //     ref: `refs/heads/${ref}`,
    //     sha: commit.sha,
    //     force: true
    //   })

    //   console.log('merge:', merge)
    //   return merge
    // } catch (err) {
    //   console.log(err, err.status)
    // }
  }
}
