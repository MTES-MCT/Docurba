const github = require('./github.js')

module.exports = {
  async createIssue (title, message, email, ref, path) {
    const issue = await github('POST /repos/{owner}/{repo}/issues', {
      title,
      body: `**👤 Utilisateur** : ${email}\n` +
        `**🗺️ Projet** : ${ref}\n` +
        `**📂 Section** : ${path}\n\n` +
        message
    })

    return issue
  }
}
