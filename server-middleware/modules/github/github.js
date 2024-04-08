/* eslint-disable no-console */
const token = process.env.GITHUB_TOKEN
const { Octokit } = require('octokit')

const octokit = new Octokit({
  auth: token
})

const supabase = require('../supabase.js')

module.exports = async function (path, options = {}) {
  const headers = {}
  let cachedRes = null

  const format = (options.mediaType ? options.mediaType.format : 'default') || 'default'

  // console.log('github request format', format, path)

  if (path.includes('GET') && !path.includes('/compare/')) {
    const { data: cache } = await supabase.from('github_cache').select('*').match({
      path,
      format
    })

    if (cache && cache[0]) {
      cachedRes = cache[0]
      headers['If-None-Match'] = cachedRes.etag
    }
  }

  try {
    const res = await octokit.request(path, Object.assign({
      headers,
      owner: process.env.GITHUB_PAC_REPO_OWNER,
      repo: process.env.GITHUB_PAC_REPO_NAME
    }, options))

    // console.log('github res --> ', res)

    if (path.includes('GET') && !path.includes('/compare/')) {
      supabase.from('github_cache').upsert([{
        path,
        format,
        etag: res.headers.etag,
        data: res
      }]).then((data) => {
        // console.log('cache saved', data)
      }).catch(err => console.log('supabase err', err))
    }

    return res
  } catch (err) {
    if (err.status === 304) {
      // console.log('Cache Working')
      return cachedRes.data
    } else {
      console.log('error in github', path, err)
    }
  }
}
