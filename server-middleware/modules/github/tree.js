/* eslint-disable no-console */
const { createClient } = require('@supabase/supabase-js')
const github = require('./github.js')

const supabase = createClient('https://ixxbyuandbmplfnqtxyw.supabase.co', process.env.SUPABASE_ADMIN_KEY)

module.exports = {
  async changeName (ref, section, newName) {
    // console.log(ref, section, newName)

    const { data: head } = await github(`GET /repos/UngererFabien/France-PAC/git/ref/heads/${ref}`, {
      ref
    })

    // console.log(head)

    const baseTree = head.object.sha

    const nameIndex = section.path.lastIndexOf(section.name)
    const newPath = `${section.path.substring(0, nameIndex)}${newName}${section.type === 'file' ? '.md' : ''}`

    let filesToDelete = []

    if (section.type === 'dir') {
      const { data } = await github(`GET /repos/{owner}/{repo}/git/trees/${section.sha}?recursive=1`, {
        tree_sha: section.sha
      })

      const subTree = data.tree

      subTree.forEach((subSection) => {
        supabase.from('pac_sections').update({
          path: `${newPath.replace('.md', '')}/${subSection.path}`
        }).match({
          path: `${section.path}/${subSection.path}`,
          ref
        }).then()
      })

      filesToDelete = subTree.filter(f => f.type === 'blob').map((f) => {
        const { path, mode, type } = f
        return { path: `${section.path}/${path}`, mode, type, sha: null }
      })
    } else {
      filesToDelete.push({
        path: section.path,
        mode: '100644',
        type: 'blob',
        sha: null
      })
    }

    // https://docs.github.com/en/rest/git/trees?apiVersion=2022-11-28#create-a-tree
    const { data: newTree } = await github('POST /repos/{owner}/{repo}/git/trees', {
      base_tree: baseTree,
      tree: [{
        path: newPath,
        mode: section.type === 'dir' ? '040000' : '100644',
        type: section.type === 'dir' ? 'tree' : 'blob',
        sha: section.sha // This will duplicate all subfiles.
      }, ...filesToDelete]
    })

    // console.log('new tree:', newTree)

    const { data: commit } = await github('POST /repos/{owner}/{repo}/git/commits', {
      message: `Change ${section.path} to ${newPath}`,
      tree: newTree.sha,
      parents: [baseTree]
    })

    // console.log('commit:', commit)

    try {
      const merge = await github(`PATCH /repos/{owner}/{repo}/git/refs/heads/${ref}`, {
        ref: `refs/heads/${ref}`,
        sha: commit.sha,
        force: true
      })

      // console.log('merge:', merge)
      return merge
    } catch (err) {
      console.log(err, err.status)
    }
  }
}
