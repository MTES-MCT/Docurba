const { Octokit } = require('octokit')

const octokit = new Octokit({
  auth: process.env.GITHUB_TOKEN
})

module.exports = async function (repoQuery) {
  return (await octokit.graphql(`query {
    repository(name: "France-PAC", owner: "nyko28") {
      ${repoQuery}
    }
  }`)).repository
}
