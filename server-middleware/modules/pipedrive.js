/* eslint-disable no-console */

// const fs = require('fs')
const _ = require('lodash')
const pipedrive = require('pipedrive')

const defaultClient = pipedrive.ApiClient.instance

// Configure API key authorization: apiToken
const apiToken = defaultClient.authentications.api_key
apiToken.apiKey = process.env.PIPEDRIVE_API_KEY
const personsApi = new pipedrive.PersonsApi()
const organizationsApi = new pipedrive.OrganizationsApi()
const dealsApi = new pipedrive.DealsApi()

// Uncomment this to fetch all status.
// const stageApi = new pipedrive.StagesApi()

// stageApi.getStages().then((stages) => {
//   console.log(stages)
// }).catch(err => console.log(err))
// const personFieldsApi = new pipedrive.PersonFieldsApi()
// personFieldsApi.getPersonFields().then((personFields) => {
//   const json = personFields.data.map((field) => {
//     const { id, name, field_type, key, options } = field

//     return { id, name, field_type, key, options }
//   })

//   fs.writeFileSync('./server-middleware/modules/Data/pipedriveFields.json', JSON.stringify(json, null, 2))
// }).catch(err => console.log(err))
// end infos

const fieldsMap = {
  // 'email': 'email',
  // departement: 'a92ba23ce78c8995ab7957ab70828023de6ebc1e' // Don't think I can just send a value when it's type enum.
  verified: {
    key: '8c176dd0608d98671ca116948a8091d6b30ac045',
    options: { true: 'Oui', false: 'Non' }
  },
  other_poste: {
    key: '945716c2fc1edf91e5e8c8aac47c73cbf7508e7e',
    set: {
      chef_unite: "Chef d'unité/de bureau/de service et adjoint",
      redacteur_pac: 'Rédacteur(ice) de PAC',
      suivi_procedures: "Chargé(e) de l'accompagnement des collectivités",
      referent_sudocuh: 'Référent Sudocuh'
    }
  },
  poste: {
    key: 'f6cac51c5bc627e57a84ce202f5fbeb59b821a87',
    options: {
      ddt: 'DDT/DEAL',
      dreal: 'DREAL',
      employe_mairie: 'Technicien(ne) ou employé(e)',
      agence_urba: "Agence d'urbanisme",
      elu: 'Elu(e)',
      be: "Bureau d'étude",
      autre: 'Autre'
    }
  },
  successfully_logged_once: {
    key: 'cf98dee8315494cec95609be9dfaef18343e6272',
    options: {
      true: 'Connecté.e',
      false: 'Non connecté.e'
    }
  },
  shared: {
    key: '9f1578c96655a81a330eb09912f0a9b5c1f40d8b'
  },
  write_frise: {
    key: '7689c2ed07954a7dc99d84b4a537532af46238f3'
  },
  read: {
    key: '9f250a47089cec1894bcfabd4eac6324a4d49b5d'
  },
  write: {
    key: '81af38758c248d593b9cbb80bb9467e8096fb801'
  }
}

// Custom Field CHARGE_DE -> Chargé de
// Chef d'unité/de bureau/de service (...) et adjoint -> Chef d'unité     -> id: 188
// Rédacteur(ice) de PAC                              -> PAC              -> id: 53
// Chargé(e) de l'accompagnement des collectivités    -> Suivi            -> id: 54
// Référent(e) Sudocuh                                -> Référent Sudocuh -> id: 189

// // TODO: remplacer les id en dur par les enums

module.exports = {
  COLLECTIVITE_DEAL: {
    TRY_INSCRIPTION: 81,
    INSCRIT: 79,
    DEPOT_ACTE: 68
  },
  STATE_DEAL: {
    DREAL: {
      LISTE: 31,
      CONTACTE: 32,
      DEMO: 49,
      EMBARQUE: 33,
      OK_REDAC: 34,
      PROCESS_MAJ: 35
    },
    EMBARQUEMENT: {
      A_TRAITE: 80
    }
  },
  CUSTOM_FIELDS: {
    CHARGE_DE: {
      key: '55b3f75345d2b8ee9851d6d743062f125678cc76',
      options: [
        { id: 188, appLabel: 'chef_unite' },
        { id: 53, appLabel: 'redacteur_pac' },
        { id: 54, appLabel: 'suivi_procedures' },
        { id: 189, appLabel: 'referent_sudocuh' }
      ]
    }
  },
  async getPersonDeals (idPerson) {
    const { data: personDeals } = await personsApi.getPersonDeals(idPerson)
    return personDeals
  },
  async findOrganization (departementNumber) {
    const {
      data: organizationsData,
      success: successOrg
    } = await organizationsApi.searchOrganization(`DDT ${departementNumber.toString()}`, {
      fields: 'name'
    })

    if (successOrg) {
      if (organizationsData.items[0]) {
        const organization = organizationsData.items[0].item

        const {
          data: organizationDeals,
          success
        } = await organizationsApi.getOrganizationDeals(organization.id)
        // console.log(organization, organizationDeals)

        if (success) {
          return {
            organization,
            deals: organizationDeals
          }
        }
      } else { return { organization: null, deals: [] } }
    } else { console.log('organizationsError') }
  },
  async addOrganization (departementNumber) {
    const newOrganization = pipedrive.NewOrganization.constructFromObject({
      name: `DDT ${departementNumber}`
    })

    const { data, error } = await organizationsApi.addOrganization(newOrganization)

    if (data && !error) {
      return data
    } else { console.log(error) }
  },
  async findPerson (email) {
    try {
      const { data: personsData, error: personsError } = await personsApi.searchPersons(email, {
        fields: 'email',
        limit: 10
      })

      if (personsData && !personsError) {
        const personItem = personsData.items.find((p) => {
          return p.item.primary_email === email
        })

        if (personItem) {
          const person = personItem.item
          const { data: personsDeals, success, additionalData } = await personsApi.getPersonDeals(person.id)

          // console.log('person', person, personsDeals)

          if (success) {
            // console.log(person, personsDeals)

            return {
              person,
              deals: personsDeals
            }
          } else { console.log('deals data', success, additionalData) }
        } else {
          return { person: null, deals: [] }
        }
      } else { console.log('personError', personsError) }
    } catch (err) {
      console.log(err.body, err.message)
    }
  },
  async addPerson (userData) {
    // console.log(' addPerson userData: ', userData)
    const personData = pipedrive.NewPerson.constructFromObject({
      name: `${userData.firstname} ${userData.lastname}`,
      phone: [{
        value: userData.tel,
        primary: 'true',
        label: ''
      }],
      email: [{
        value: userData.email,
        primary: 'true',
        label: ''
      }],
      [this.CUSTOM_FIELDS.CHARGE_DE.key]: userData.customRoles ?? []
      // primaryEmail: userData.email // This does not work -> https://devcommunity.pipedrive.com/t/persons-primary-email-error-bug/5784/3
    })
    // console.log('personData after: ', personData)
    const { data, error } = await personsApi.addPerson(personData)

    if (data && !error) {
      // console.log(data)

      return data
    } else { console.log('error', error) }
  },
  updatePerson (personId, data) {
    const personData = { '2a0f1211cad87a393283f3167a72832c53ed7966': '' }
    _.forEach(data, (val, key) => {
      const pipedriveFiel = fieldsMap[key]
      let pipedriveValue = val

      if (pipedriveFiel) {
        if (pipedriveFiel.options) {
          pipedriveValue = pipedriveFiel.options[val]
        }

        if (pipedriveFiel.set) {
          pipedriveValue = val?.map((v) => {
            if (pipedriveFiel.set[v]) {
              return pipedriveFiel.set[v]
            } else {
              personData['2a0f1211cad87a393283f3167a72832c53ed7966'] += ' ' + v
              return null
            }
          }).filter(v => !!v)
        }

        personData[pipedriveFiel.key] = pipedriveValue
      }
    })

    const newPersonData = pipedrive.UpdatePerson.constructFromObject(personData)
    return personsApi.updatePerson(personId, newPersonData)
  },
  async searchDeal (term) {
    const { data: { items } } = await dealsApi.searchDeals(term)
    console.log('ITEMS SEARCHED: ', items)
    return items
  },
  async addDeal (dealData) {
    const newDealData = pipedrive.NewDeal.constructFromObject(dealData)
    const { success, data } = await dealsApi.addDeal(newDealData)
    console.log(' success: ', success, 'data: ', data)
    return { data, success }
  },
  updateDeal (dealId, data) {
    const newDealData = pipedrive.UpdateDealRequest.constructFromObject(data)
    return dealsApi.updateDeal(dealId, newDealData)
  },
  async signupCollectivite (data) {
    console.log('-- SIGNUP COLLECTIVITE PIPEDRIVE --')
    let { person } = await this.findPerson(data.email)
    if (!person) {
      console.log('Person not found, creating one')
      person = await this.addPerson(data)
      const deal = {
        title: `${data.poste} de ${data.detailsCollectivite.intitule} (${data.detailsCollectivite.departementCode})`,
        personId: person.id,
        stageId: this.COLLECTIVITE_DEAL.TRY_INSCRIPTION
      }
      // console.log('deal, :', deal)
      await this.addDeal(deal)
    }
  },
  async movePersonDealTo (email, from, to) {
    const { person } = await this.findPerson(email)
    const personDeals = await this.getPersonDeals(person.id)
    // console.log('personDeals: ', personDeals)
    const dealIdToUpdate = personDeals.filter(e => e.stage_id === from)[0]?.id
    console.log('dealIdToUpdate: ', dealIdToUpdate)
    if (dealIdToUpdate) { await this.updateDeal(dealIdToUpdate, { stage_id: to }) }
  },
  async signupStateAgent (userData) {
    try {
      console.log('-- SIGNUP STATE AGENT PIPEDRIVE --')
      const self = this
      let { person } = await this.findPerson(userData.email)

      if (!person) {
        if (userData.poste !== 'dreal') {
          userData.customRoles = this.CUSTOM_FIELDS.CHARGE_DE.options.filter(e => userData.other_poste.includes(e.appLabel)).map(e => e.id)
        }
        person = await this.addPerson(userData)
      }

      // Handle DREAL
      if (userData.poste === 'dreal') {
        const drealDeal = await this.searchDeal(userData.region.code)
        const drealDealId = drealDeal.map(e => e.item).find(e => Object.values(this.STATE_DEAL.DREAL).includes(e.stage.id)).id

        const opts = pipedrive.AddDealParticipantRequest.constructFromObject({ person_id: person.id })
        await dealsApi.addDealParticipant(drealDealId, opts)
      // End Handle dreal
      } else {
        // eslint-disable-next-line prefer-const
        let { organization, deals: organizationDeals } = await this.findOrganization(userData.departement.code_departement)
        if (!organization) { organization = await this.addOrganization(userData.departement.code_departement) }

        this.updatePerson(person.id, { orgId: organization.id })

        // Add new user 'Elaboration PAC' pipeline
        const deal = {
          title: `${userData.departement.code_departement} ${userData.departement.nom_departement}`,
          personId: person.id
        }
        // Élaboration PAC - 55
        if (userData.other_poste.includes('redacteur_pac')) {
          const { data } = await this.addDeal({ ...deal, stageId: 55 })
          console.log('Deal New Redacteur Created', data)
        }
        // Suivi des procédures (DDT) - 61
        if (userData.other_poste.includes('suivi_procedures') || userData.other_poste.includes('referent_sudocuh')) {
          const { data } = await this.addDeal({ ...deal, stageId: 61 })
          console.log('Deal New Suivi de procedure Created', data)
        }

        // embarquement département et régions - ?
        if (userData.other_poste.includes('chef_unite')) {
          const { data } = await this.addDeal({ ...deal, stageId: self.STATE_DEAL.EMBARQUEMENT.A_TRAITE })
          console.log('Deal New chef d\'unité Created', data)
        }

        // Deal in prospect or Contacted goes to Inscrits
        if (organizationDeals && organizationDeals.length) {
          const deal = organizationDeals.find(d => d.stage_id === 10 || d.stage_id === 11)

          if (deal) {
            const { data } = await this.updateDeal(deal.id, { stage_id: 12 })
            console.log('Deal updated', data)
          }
        } else {
          const { data } = await this.addDeal({
            title: `${userData.departement.code_departement} ${userData.departement.nom_departement}`,
            orgId: organization.id,
            stageId: 12
          })

          console.log('Deal Created', data)
        }
      }
    } catch (err) {
      console.log(err)
    }
  }
}
