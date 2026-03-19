module.exports = {
  authorizedEnvironments: {
    development: 'développement',
    review_app: 'recette jetable',
    demo: 'démonstration',
    production: 'production',
  },
  diplayName () {
    return this.authorizedEnvironments[process.env.USER_ENVIRONMENT]
  },
  messageProposition() {
    if (['development', 'review_app', 'demo'].includes(process.env.USER_ENVIRONMENT)) {
      return `(Test en ${this.diplayName()})`
    }
  },
}
