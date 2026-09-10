/* eslint-disable no-console */
const _ = require('lodash')
const express = require('express')
const app = express()
app.use(express.json())

const sibApi = require('./modules/sibApi.js')

const supabase = require('./modules/supabase.js')

// modules
const sendgrid = require('./modules/sendgrid.js')
const pipedrive = require('./modules/pipedrive.js')
const slack = require('./modules/slack.js')

app.post('/password', async (req, res) => {
  // console.log('/password body', req.body)

  const { data: { properties }, error } = await supabase.auth.admin.generateLink({
    type: 'recovery',
    email: req.body.email
  })

  // The user will be redirected to this url in case of password recovery.
  // https://docurba.beta.gouv.fr/#access_token=XXX&expires_in=3600&refresh_token=XXX&token_type=bearer&type=recovery

  // https://ixxbyuandbmplfnqtxyw.supabase.co/auth/v1/verify?token=XXX&type=recovery&redirect_to=https://docurba.beta.gouv.fr/
  // console.log('user.action_link', user.action_link)

  if (!error && properties && properties.action_link) {
    const { data: profiles } = await supabase.from('profiles').select('firstname, lastname').eq('email', req.body.email)
    const profile = profiles[0]

    sendgrid.sendEmail({
      to: req.body.email,
      template_id: 'd-06e865fdc30d42a398fdc6bc532deb82',
      dynamic_template_data: {
        redirectURL: `${properties.action_link}%3Ftype=recovery`,
        firstname: profile?.firstname,
        lastname: profile?.lastname
      }
    })

    res.status(200).send('OK')
  } else {
    console.log('Error reset password', error)
    res.status(400).send(error)
  }
})

async function magicLinkSignIn ({ email, redirectBasePath }) {
  const { data: profiles } = await supabase.from('profiles').select('firstname, lastname, successfully_logged_once, collectivite_id').eq('email', email)
  const profile = profiles[0]

  if (!profile) {
    throw new Error('KO')
  } else {
    const { data: { user, properties }, error } = await supabase.auth.admin.generateLink({
      type: 'magiclink',
      email,
      options: {
        redirectTo: profile.successfully_logged_once ? `${process.env.APP_URL}/collectivites/${profile.collectivite_id}/` : redirectBasePath
      }
    })

    if (error) {
      throw error
    }

    if (properties && properties.action_link) {
      sendgrid.sendEmail({
        to: email,
        template_id: profile.successfully_logged_once ? 'd-7a75390ea3334b66a5d9cfb9fa76e077' : 'd-766d017b51124a108cabc985d0dbf451',
        dynamic_template_data: {
          redirectURL: properties.action_link,
          firstname: profile.firstname,
          lastname: profile.lastname
        }
      })
    }

    return user
  }
}

async function getRedirectPath (emailProfile) {
  const { data: rawProfile, error: errorProfile } = await supabase.from('profiles').select().eq('email', emailProfile)
  if (errorProfile) { throw errorProfile }
  if (rawProfile.length < 1) { throw new Error('KO') }
  const profile = rawProfile[0]
  return `/collectivites/${profile.collectivite_id}`
}

app.post('/signinCollectivite', async (req, res) => {
  try {
    const path = await getRedirectPath(req.body.email)

    await magicLinkSignIn({
      email: req.body.email,
      redirectBasePath: req.body.redirectTo + path
    })
  } catch (error) {
    console.log('ERROR /auth/signinCollectivite : ', error.message)
  }

  res.status(200).send('OK')
})

app.post('/signupCollectivite', async (req, res) => {
  const userData = _.pick(req.body.userData, [
    'collectivite_id',
    'departement',
    'email',
    'firstname',
    'lastname',
    'optin',
    'other_poste',
    'poste',
    'region',
    'tel'
  ])

  try {
    // Create user
    const { data: { user }, error: creationError } = await supabase.auth.admin.createUser({
      email: userData.email
    })

    if (creationError) {
      throw creationError
    }

    // Insert profile
    const { data: profile, error: profileInsertionError } = await supabase.from('profiles').insert({
      ...userData,
      side: 'collectivite',
      user_id: user.id
    }).select().limit(1).single()

    if (profileInsertionError) {
      throw profileInsertionError
    }

    // Subscribe to newsletter
    const listMap = {
      agence_urba: 21,
      autre: 34,
      be: 21,
      elu: 22,
      employe_mairie: 22
    }

    sibApi.optinNewsLetter(userData.email, userData.optin, [listMap[profile.poste]])

    // Send magic link
    await magicLinkSignIn({
      email: userData.email,
      redirectBasePath: `${req.body.redirectTo}/collectivites/${profile.collectivite_id}`
    })

    // Send access request to slack
    slack.requestCollectiviteAccess(profile)

    // Update pipedrive
    pipedrive.signupCollectivite({
      ...userData,
      detailsCollectivite: _.pick(req.body.detailsCollectivite, [
        'code',
        'codeInsee',
        'departementCode',
        'intercommunaliteCode',
        'intitule',
        'regionCode',
        'siren',
        'type'
      ])
    })

    res.status(200).send(user)
  } catch (error) {
    console.log('ERROR /auth/signupCollectivite : ', error.message)
    res.status(500).send({ message: error.message })
  }
})

app.post('/signupStateAgent', async (req, res) => {
  const userData = _.pick(req.body.userData, [
    'departement',
    'email',
    'firstname',
    'lastname',
    'optin',
    'other_poste',
    'poste',
    'region'
  ])

  try {
    // Create user
    const { data: { user }, error: signupError } = await supabase.auth.admin.createUser({
      email: userData.email,
      email_confirm: true,
      password: req.body.userData.password
    })

    if (signupError) {
      throw signupError
    }

    // Insert profile
    const { data: profile, error: profileInsertionError } = await supabase.from('profiles').insert({
      ...userData,
      side: 'etat',
      user_id: user.id
    }).select().limit(1).single()

    if (profileInsertionError) {
      throw profileInsertionError
    }

    // Set github roles
    if (profile.poste === 'ddt') {
      await supabase.from('github_ref_roles').insert([{
        ref: `dept-${profile.departement}`,
        role: 'user',
        user_id: user.id
      }])
    }

    // Subscribe to newsletter
    sibApi.optinNewsLetter(userData.email, userData.optin, [33])

    const profileAndUserData = { ...profile, ...userData }

    // Send access request to slack
    slack.requestStateAgentAccess(profileAndUserData)

    // Update pipedrive
    pipedrive.signupStateAgent(profileAndUserData)

    res.status(200).send(user)
  } catch (error) {
    console.log('ERROR /auth/signupStateAgent : ', error.message)
    res.status(500).send({ message: error.message })
  }
})

module.exports = app
