/* eslint-disable no-console */
const axios = require('axios')
const geo = require('./geo.js')
const supabase = require('./supabase.js')
const preposition = process.env.NODE_ENV === 'development' ? '[Test] ' : ''

module.exports = {
  shareProcedure ({ from, to, type, procedure, pac }) {
    console.log('from: ', from.poste)
    return axios({
      url: process.env.SLACK_WEBHOOK,
      method: 'post',
      data: {
        blocks: [
          {
            type: 'header',
            text: {
              type: 'plain_text',
              text: preposition + `Partage d'${type === 'frp' ? 'une FRP' : 'un PaC'}: ${procedure.name}`
            }
          },
          {
            type: 'section',
            text: {
              type: 'plain_text',
              text: `${!from.firstname || !from.lastname ? from.email : from.firstname + ' ' + from.lastname}, ${from.poste ? from.poste : 'role inconnu'}, a partagé ${type === 'frp' ? 'une FRP' : 'un PaC'} à ${to.emailsFormatted}`
            }
          },
          {
            type: 'section',
            text: {
              type: 'mrkdwn',
              text: preposition + `Lien: ${process.env.APP_URL}${procedure.url}`
            }
          }
        ]
      }
    })
  },
  requestDepotActe (userData) {
    return axios({
      url: process.env.SLACK_WEBHOOK,
      method: 'post',
      data: {
        text: `Vérification de l'email ${userData.email} pour le depot d'acte de ${userData.isEpci ? 'l\'EPCI' : 'la commune'}:  ${userData.collectivite.intitule} (${userData.collectivite.region.intitule})`,
        blocks: [
          {
            type: 'header',
            text: {
              type: 'plain_text',
              text: `Vérification de l'email ${userData.email} pour le depot d'acte de ${userData.isEpci ? 'l\'EPCI' : 'la commune'}:  ${userData.collectivite.intitule} (${userData.collectivite.region.intitule})`
            }
          },
          {
            type: 'section',
            text: {
              type: 'mrkdwn',
              text: preposition + `https://docurba.beta.gouv.fr/collectivites/${userData.collectivite.code}/prescriptions`
            }
          }
        ]
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
              text: preposition + `Demande d'accès Collectivité de ${userData.firstname} ${userData.lastname} ayant pour poste ${userData.poste}`
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
              text: preposition + `Demande d'accès ${userData.poste === 'dreal' ? 'DREAL' : 'DDT'} de ${userData.firstname} ${userData.lastname}`
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
              text: preposition + `Demande de PAC de ${user_metadata.firstname} ${user_metadata.lastname}`
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
  },
  async notifyFrpEvent ({
    eventData,
    userData,
    procedureData
  }) {
    const collectivitePorteuse = geo.getCollectivite(procedureData.collectivite_porteuse_id)

    const { data: procedures } = await supabase.from('procedures').select('*')
      .eq('id', eventData.procedure_id)

    const procedure = procedures[0]

    const { data: perim } = await supabase.from('procedures_perimetres').select('*')
      .eq('procedure_id', eventData.procedure_id)

    let perimText = ''

    if (perim.length > 1) {
      perimText = `- Collectivites concernées: ${perim.map(p => p.collectivite_code).join(', ')}`
    } else {
      const commune = geo.getCommune(perim[0].collectivite_code)
      perimText = `- Commune concernée: ${commune.code} ${commune.intitule}`
    }

    const data = {
      text: `Nouvel event ${eventData.type}`,
      blocks: [
        {
          type: 'header',
          text: {
            type: 'plain_text',
            text: preposition + `Nouvel event ${eventData.type}`
          }
        },
        {
          type: 'section',
          text: {
            type: 'mrkdwn',
            text: `- Procedure: ${procedure.type} ${procedure.doc_type}`
          }
        },
        {
          type: 'section',
          text: {
            type: 'mrkdwn',
            text: `- Frise: https://docurba.beta.gouv.fr/frise/${eventData.procedure_id}`
          }
        },
        {
          type: 'section',
          text: {
            type: 'mrkdwn',
            text: `- User: ${userData.email}, ${userData.poste}`
          }
        },
        {
          type: 'section',
          text: {
            type: 'mrkdwn',
            text: perimText
          }
        },
        {
          type: 'section',
          text: {
            type: 'mrkdwn',
            text: `- Collectivite porteuse: ${collectivitePorteuse.intitule}(${collectivitePorteuse.code}), departement ${collectivitePorteuse.departementCode}`
          }
        },
        {
          type: 'divider'
        }
      ]
    }

    return axios({
      url: process.env.SLACK_EVENT_CTBE,
      method: 'post',
      data
    })
  }
}
