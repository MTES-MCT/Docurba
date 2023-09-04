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
  requestCollectiviteAccess (userData) {
    return axios({
      url: process.env.SLACK_WEBHOOK,
      method: 'post',
      data: {
        text: `Demande d'accès Collectivité de ${userData.firstname} ${userData.lastname} ayant pour poste ${userData.poste}`,
        blocks: [
          {
            type: 'header',
            text: {
              type: 'plain_text',
              text: `Demande d'accès Collectivité de ${userData.firstname} ${userData.lastname} ayant pour poste ${userData.poste}`
            }
          },
          {
            type: 'section',
            text: {
              type: 'mrkdwn',
              text: `- collectivité code INSEE: ${userData.collectivite_id} (departement: ${userData.departement}) \n - email: ${userData.email}`
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
                action_id: 'collectivite_validation'
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
  requestStateAgentAccess (userData) {
    console.log('requestStateAgentAccess userData: ', userData)
    let textContent = ''
    if (userData.poste === 'ddt') {
      textContent = `- departement: ${userData.departement.nom_departement} - ${userData.departement.code_departement} \n - email: ${userData.email}`
    } else if (userData.poste === 'dreal') {
      textContent = `- region: ${userData.region.name} - ${userData.region.code} \n - email: ${userData.email}`
    }
    return axios({
      url: process.env.SLACK_WEBHOOK,
      method: 'post',
      data: {
        text: `Demande d'accès ${userData.poste === 'dreal' ? 'DREAL' : 'DDT'} de ${userData.firstname} ${userData.lastname}`,
        blocks: [
          {
            type: 'header',
            text: {
              type: 'plain_text',
              text: `Demande d'accès ${userData.poste === 'dreal' ? 'DREAL' : 'DDT'} de ${userData.firstname} ${userData.lastname}`
            }
          },
          {
            type: 'section',
            text: {
              type: 'mrkdwn',
              text: textContent
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
