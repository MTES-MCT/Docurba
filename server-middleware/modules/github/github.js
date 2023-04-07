/* eslint-disable no-console */
const token = process.env.GITHUB_TOKEN
const { Octokit } = require('octokit')

const octokit = new Octokit({
  auth: token
})

const { createClient } = require('@supabase/supabase-js')
const supabase = createClient('https://ixxbyuandbmplfnqtxyw.supabase.co', process.env.SUPABASE_ADMIN_KEY)

module.exports = async function (path, options = {}) {
  const headers = {}
  let cachedRes = null

  const format = (options.mediaType ? options.mediaType.format : 'default') || 'default'

  // console.log('github request format', format)

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
      owner: 'UngererFabien',
      repo: 'France-PAC'
    }, options))

    if (path.includes('GET') && !path.includes('/compare/')) {
      supabase.from('github_cache').upsert([{
        path,
        format,
        etag: res.headers.etag,
        data: res
      }]).then((data) => {
        // console.log('cache saved', data)
      })
    }

    return res
  } catch (err) {
    if (err.status === 304) {
      // console.log('Cache Working')
      return cachedRes.data
    } else {
      // console.log('error in github', err)
    }
  }
}
