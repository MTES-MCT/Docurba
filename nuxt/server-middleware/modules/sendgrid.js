const userEnvironment = require('./userEnvironment.js')
const sgMail = require('@sendgrid/mail')
sgMail.setApiKey(process.env.SENDGRID_API_KEY)


module.exports = {
  sendEmail (message) {
    if (!process.env.SENDGRID_API_KEY) {
      console.log('The SENDGRID_API_KEY environment variable is not defined.')
      return
    }
    message.dynamic_template_data["subject_preposition"] = userEnvironment.messageProposition()
    return sgMail.send(Object.assign({
      from: {
        email: 'equipe@docurba.beta.gouv.fr',
        name: 'L‘équipe docurba'
      },
      replyTo: {
        email: 'contact@docurba.beta.gouv.fr',
        name: 'Equipe Docurba'
      }
    }, message))
  }
}
