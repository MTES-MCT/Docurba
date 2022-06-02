const sgMail = require('@sendgrid/mail')
sgMail.setApiKey(process.env.SENDGRID_API_KEY)

module.exports = {
  sendEmail (message) {
    return sgMail.send(Object.assign({
      from: 'fabien.ungerer@beta.gouv.fr' // This need to be a verified sender
    }, message))
  }
}
