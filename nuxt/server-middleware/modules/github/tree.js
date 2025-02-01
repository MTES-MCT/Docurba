/* eslint-disable no-console */
const crypto = require('crypto')
const supabase = require('../supabase.js')
const github = require('./github.js')
const githubGql = require('./github-graphql.js')
const { getFileContent } = require('./files.js')

module.exports = {
  async changeName (ref, section, newName) {
    // console.log(ref, section, newName)

    const { data: head } = await github(`GET /repos/{owner}/{repo}/git/ref/heads/${ref}`, {
      ref
    })

    // console.log(head)

    const baseTree = head.object.sha

    const nameIndex = section.path.lastIndexOf(section.name)
    const newPath = `${section.path.substring(0, nameIndex)}${newName}${section.type === 'file' ? '.md' : ''}`

    let filesToDelete = []

    // need to fetch section again because section.sha cannot be trusted. Also, type could be updated to dir with path unchanged.
    const currentFile = await getFileContent(section.type === 'dir' ? section.path.replace('.md', '') : section.path, ref, 'object')

    if (section.type === 'dir') {
      const { data } = await github(`GET /repos/{owner}/{repo}/git/trees/${currentFile.sha}?recursive=1`, {
        tree_sha: currentFile.sha
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
        path: currentFile.path,
        mode: '100644',
        type: 'blob',
        sha: null
      })
    }

    try {
    // https://docs.github.com/en/rest/git/trees?apiVersion=2022-11-28#create-a-tree
      const data = await github('POST /repos/{owner}/{repo}/git/trees', {
        base_tree: baseTree,
        tree: [{
          path: newPath,
          mode: section.type === 'dir' ? '040000' : '100644',
          type: section.type === 'dir' ? 'tree' : 'blob',
          sha: currentFile.sha // This will duplicate all subfiles.
        }, ...filesToDelete]
      })

      const newTree = data.data

      // console.log('new tree:', newTree)

      const { data: commit } = await github('POST /repos/{owner}/{repo}/git/commits', {
        message: `Change ${section.path} to ${newPath}`,
        tree: newTree.sha,
        parents: [baseTree]
      })

      // console.log('commit:', commit)

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
  },
  async copy (toRef, fromRef, path) {
    const { data: fromHead } = await github('GET /repos/{owner}/{repo}/git/ref/heads/{ref}', {
      ref: fromRef
    })

    const { data: toHead } = await github('GET /repos/{owner}/{repo}/git/ref/heads/{ref}', {
      ref: toRef
    })

    const fromTreeSha = fromHead.object.sha
    const toTreeSha = toHead.object.sha

    const { data: fromTree } = await github('GET /repos/{owner}/{repo}/git/trees/{tree_sha}?recursive=1', {
      tree_sha: fromTreeSha
    })

    const { data: toTree } = await github('GET /repos/{owner}/{repo}/git/trees/{tree_sha}?recursive=1', {
      tree_sha: toTreeSha
    })

    const objectToCopy = fromTree.tree.find(o => o.path === path)

    if (!objectToCopy) {
      throw new Error('Object to copy not found')
    }

    const treeOverride = [
      {
        path: objectToCopy.path,
        mode: objectToCopy.mode,
        type: objectToCopy.type,
        sha: objectToCopy.sha
      }
    ]

    const parentPath = path.substring(0, path.lastIndexOf('/'))
    const introToMove = toTree.tree.find(o => o.path === `${parentPath}.md`)

    // if the parent section is not a dir in the destination tree, we need to move it as an intro
    if (introToMove) {
      treeOverride.push(
        // copy intro from '{path}.md' to '{path}/intro.md'
        {
          path: `${parentPath}/intro.md`,
          mode: introToMove.mode,
          type: introToMove.type,
          sha: introToMove.sha
        },
        // remove old intro '{path}.md'
        {
          path: `${parentPath}.md`,
          mode: introToMove.mode,
          type: introToMove.type,
          sha: null // passing null deletes the file
        }
      )
    }

    const { data: newTree } = await github('POST /repos/{owner}/{repo}/git/trees', {
      base_tree: toTreeSha,
      tree: treeOverride
    })

    const { data: commit } = await github('POST /repos/{owner}/{repo}/git/commits', {
      message: `Copy ${path} from ${fromRef}`,
      tree: newTree.sha,
      parents: [toTreeSha]
    })

    const { data: merge } = await github(`PATCH /repos/{owner}/{repo}/git/refs/heads/${toRef}`, {
      ref: `refs/heads/${toRef}`,
      sha: commit.sha,
      force: true
    })

    return merge
  },
  findTree (tree, splitPath) {
    if (!splitPath.length) {
      return tree
    }

    const name = splitPath.shift()
    const object = tree.children.find(o => o.name === name)

    return this.findTree(object, splitPath)
  },
  async getTree (ref, path) {
    const { data: rootTree } = await github('GET /repos/{owner}/{repo}/git/trees/{ref}?recursive=1', {
      ref
    })

    const branches = rootTree.tree.filter(b => b.path.startsWith(path)).map((branche) => {
      const splitPath = branche.path.split('/')
      const name = splitPath.pop()

      return {
        name: name.replace('.md', ''),
        depth: splitPath.length,
        path: branche.path,
        type: branche.type === 'tree' ? 'dir' : 'file',
        sha: branche.sha,
        url: branche.url,
        children: branche.type === 'tree' ? [] : undefined
      }
    }).filter(b => b.depth > 0)

    branches.forEach((branche) => {
      const parent = branches.find((b) => {
        return b.type === 'dir' && b.depth === (branche.depth - 1) &&
          branche.path.includes(`${b.path}/${branche.name}`)
      })

      if (branche.name === 'intro.md' || branche.name === 'intro') {
        parent.introSha = branche.sha
      } else if (parent) {
        parent.children.push(branche)
      }
    })

    return branches.filter(b => b.depth === 1)

    // console.log(branches.filter(b => b.depth === 1))

    // const objects = rootTree.tree.sort((a, b) => {
    //   if (a.type === 'tree' && b.type !== 'tree') {
    //     return -1
    //   }
    //   if (a.type !== 'tree' && b.type === 'tree') {
    //     return 1
    //   }

    //   return a.path.localeCompare(b.path)
    // })

    // const root = {
    //   path: '',
    //   children: []
    // }

    // for (const object of objects) {
    //   const splitPath = object.path.split('/')
    //   const name = splitPath.pop()

    //   const parent = this.findTree(root, splitPath)

    //   if (name === 'intro.md' || name === 'intro') {
    //     parent.introSha = object.sha
    //     continue
    //   }

    //   parent.children.push({
    //     name: name.replace('.md', ''),
    //     path: object.path,
    //     type: object.type === 'tree' ? 'dir' : 'file',
    //     sha: object.sha,
    //     url: object.url,
    //     children: object.type === 'tree' ? [] : undefined
    //   })
    // }

    // return this.findTree(root, path.split('/')).children ?? []
  },
  async getHistories (ref, paths) {
    function hash (string) {
      return crypto.createHash('shake256', { outputLength: 8 }).update(string).digest('hex')
    }

    const gqlQuery = `ref(qualifiedName: "${ref}") {
      target {
        ... on Commit {
          ${
            paths
              .map(path => `${'hash_' + hash(path)}: blame(path: "${path.replaceAll('"', '\\"')}") {
                ranges {
                  commit {
                    committedDate
                  }
                }
              }`)
              .join('\n')
          }
        }
      }
    }`

    const blameRangesByFile = (await githubGql(gqlQuery)).ref.target

    return paths.map((path) => {
      const blame = blameRangesByFile['hash_' + hash(path)]
      const commit = blame?.ranges[0]?.commit

      if (!commit) {
        return { path }
      }

      return {
        path,
        commit: {
          date: commit.committedDate
        }
      }
    })
  }
}
