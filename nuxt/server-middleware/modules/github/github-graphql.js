const { Octokit } = require('octokit')

const octokit = new Octokit({
  auth: process.env.GITHUB_TOKEN
})

module.exports = async function (repoQuery) {
  return (await octokit.graphql(`query {
    repository(name: "${process.env.GITHUB_PAC_REPO_NAME}", owner: "${process.env.GITHUB_PAC_REPO_OWNER}") {
      ${repoQuery}
    }
  }`)).repository
}
