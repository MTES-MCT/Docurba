const sgMail = require('@sendgrid/mail')
const preposition = process.env.NODE_ENV === 'development' ? '[Test] ' : ''
sgMail.setApiKey(process.env.SENDGRID_API_KEY)


module.exports = {
  sendEmail (message) {
    return sgMail.send(Object.assign({
      // from: 'fabien.ungerer@beta.gouv.fr' // This need to be a verified sender
      from: {
        email: 'equipe@docurba.beta.gouv.fr',
        name: 'L‘équipe docurba'
      },
      replyTo: {
        email: 'contact@docurba.beta.gouv.fr',
        name: 'Equipe Docurba'
      }
    }, preposition + message))
  }
}
