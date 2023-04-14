const axios = require('axios')

module.exports = {
  requestDepotActe (userData) {
    return axios({
      url: process.env.SLACK_WEBHOOK,
      method: 'post',
      data: {
        text: `Vérification de l'email ${userData.email} pour le depot d'acte de ${userData.isEpci ? 'l\'EPCI' : 'la commune'}:  ${userData.collectivite.name} (${userData.region.name})`
      }
    })
  },
  requestDepartementAccess (userData) {
    return axios({
      url: process.env.SLACK_WEBHOOK,
      method: 'post',
      data: {
        text: `Demande d'accès DDT de ${userData.firstname} ${userData.lastname}`,
        blocks: [
          {
            type: 'header',
            text: {
              type: 'plain_text',
              text: `Demande d'accès DDT de ${userData.firstname} ${userData.lastname}`
            }
          },
          {
            type: 'section',
            text: {
              type: 'mrkdwn',
              text: `- departement: ${userData.dept.nom_departement} - ${userData.dept.code_departement} \n - email: ${userData.email}`
            }
          },
          {
            type: 'actions',
            block_id: 'actions1',
            elements: [
              {
                type: 'button',
                text: {
                  type: 'plain_text',
                  text: `Valider ${userData.email}`
                },
                value: JSON.stringify(userData),
                action_id: 'ddt_validation'
              }
            ]
          },
          {
            type: 'divider'
          }
        ]
      }
    })
  },
  requestPAC (userData, pacData) {
    // eslint-disable-next-line camelcase
    const { user_metadata } = userData

    return axios({
      url: process.env.SLACK_WEBHOOK,
      method: 'post',
      data: {
        text: `Demande de PAC de ${user_metadata.firstname} ${user_metadata.lastname}`,
        blocks: [
          {
            type: 'header',
            text: {
              type: 'plain_text',
              text: `Demande de PAC de ${user_metadata.firstname} ${user_metadata.lastname}`
            }
          },
          {
            type: 'section',
            text: {
              type: 'mrkdwn',
              text: `- Commune: ${pacData.town.nom_commune} - ${pacData.town.nom_departement} ${pacData.town.code_departement} \n - Email: ${userData.email}`
            }
          },
          {
            type: 'section',
            text: {
              type: 'mrkdwn',
              text: `- Type: ${pacData.doc_type} \n - Nom: ${pacData.name}`
            }
          },
          {
            type: 'divider'
          }
        ]
      }
    })
  }
}
