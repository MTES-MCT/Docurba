/* eslint-disable no-console */
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

module.exports = {
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
  async addOrganzation (departementNumber) {
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
        limit: 1
      })

      if (personsData && !personsError) {
        if (personsData.items[0]) {
          const person = personsData.items[0].item

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
    const personData = pipedrive.NewPerson.constructFromObject({
      name: `${userData.firstname} ${userData.lastname}`,
      email: [{
        value: userData.email,
        primary: 'true',
        label: ''
      }]
      // primaryEmail: userData.email // This does not work -> https://devcommunity.pipedrive.com/t/persons-primary-email-error-bug/5784/3
    })

    const { data, error } = await personsApi.addPerson(personData)

    if (data && !error) {
      // console.log(data)

      return data
    } else { console.log('error', error) }
  },
  updatePerson (personId, data) {
    const newPersonData = pipedrive.UpdatePerson.constructFromObject(data)
    return personsApi.updatePerson(personId, newPersonData)
  },
  async addDeal (dealData) {
    const newDealData = pipedrive.NewDeal.constructFromObject(dealData)
    const { success, data } = await dealsApi.addDeal(newDealData)
    return { data, success }
  },
  updateDeal (dealId, data) {
    const newDealData = pipedrive.UpdateDealRequest.constructFromObject(data)
    return dealsApi.updateDeal(dealId, newDealData)
  },
  async signup (userData) {
    try {
      let { person } = await this.findPerson(userData.email)

      if (!person) {
        person = await this.addPerson(userData)
      }

      // Signup as DDT
      if (userData.departement && userData.departement.code_departement) {
      // eslint-disable-next-line prefer-const
        let { organization, deals: organizationDeals } = await this.findOrganization(userData.departement.code_departement)

        if (!organization) {
          organization = await this.addOrganzation(userData.departement.code_departement)
        }

        this.updatePerson(person.id, {
          orgId: organization.id
        })

        // Deal in prospect or Contacted goes to Inscrits
        if (organizationDeals && organizationDeals.length) {
          const deal = organizationDeals.find((d) => {
            return d.stage_id === 10 || d.stage_id === 11
          })

          if (deal) {
            const { data } = await this.updateDeal(deal.id, {
              stage_id: 12
            })

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
