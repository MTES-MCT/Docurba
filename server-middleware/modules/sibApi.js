const SibApiV3Sdk = require('sib-api-v3-sdk')

module.exports = {
  optinNewsLetter (email, optin, lists = []) {
    const defaultClient = SibApiV3Sdk.ApiClient.instance
    const apiKey = defaultClient.authentications['api-key']
    apiKey.apiKey = process.env.BREVO_API_KEY

    const apiInstance = new SibApiV3Sdk.ContactsApi()
    const createContact = new SibApiV3Sdk.CreateContact()

    createContact.email = email
    createContact.listIds = [27, ...lists]
    createContact.attributes = { NEWUSER_OPTIN: optin }

    apiInstance.createContact(createContact).then(function (data) {
      // eslint-disable-next-line no-console
      console.log('API called successfully. Returned data: ' + JSON.stringify(data))
    }, function (error) {
      // eslint-disable-next-line no-console
      console.error('createContact error', error)
    })
  }
}
