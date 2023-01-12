const token = process.env.GITHUB_TOKEN
const { Octokit } = require('octokit')

const octokit = new Octokit({
  auth: token
})

module.exports = function (path, options) {
  return octokit.request(path, Object.assign({
    owner: 'UngererFabien',
    repo: 'France-PAC'
  }, options))
}
