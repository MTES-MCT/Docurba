/* eslint-disable no-console */
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
        redirectURL: properties.action_link,
        firstname: profile.firstname,
        lastname: profile.lastname
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
    throw new Error('Vous devez créer un compte avant de pouvoir vous connecter.')
  } else {
    const { data: { user, properties }, error } = await supabase.auth.admin.generateLink({
      type: 'magiclink',
      email,
      options: {
        redirectTo: profile.successfully_logged_once ? `https://docurba.beta.gouv.fr/collectivites/${profile.collectivite_id}/` : redirectBasePath
      }
    })

    if (error) {
      console.log('ERROR magicLinkSignIn: ', error)
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
          // dashboard_url: `https://docurba.beta.gouv.fr/collectivites/${profile.collectivite_id}/`
        }
      })
    }

    return user
  }
}

async function getRedirectPath (emailProfile) {
  const { data: rawProfile, error: errorProfile } = await supabase.from('profiles').select().eq('email', emailProfile)
  if (errorProfile) { throw errorProfile }
  if (rawProfile.length < 1) { throw new Error("Nous n'avons pas trouvé d'utilisateur enregistrer avec cet adresse email. Veuillez créer un compte.") }
  const profile = rawProfile[0]
  return `/collectivites/${profile.collectivite_id}?isEpci=${profile.collectivite_id.length > 5}`
}

app.post('/signinCollectivite', async (req, res) => {
  try {
    const path = await getRedirectPath(req.body.email)

    const user = await magicLinkSignIn({
      email: req.body.email,
      redirectBasePath: req.body.redirectTo + path
    })

    res.status(200).send(user)
  } catch (error) {
    console.log('ERROR /auth/signinCollectivite : ', error.message)
    res.status(500).send({ message: error.message })
  }
})

app.post('/signupCollectivite', async (req, res) => {
  try {
    const { data: { user }, error: creationError } = await supabase.auth.admin.createUser({
      email: req.body.userData.email
    })

    if (creationError) { throw creationError }

    // Insert new profile
    const { data: insertedProfile, error: errorInsertProfile } = await supabase.from('profiles').insert({
      ...req.body.userData,
      side: 'collectivite',
      user_id: user.id
    }).select()

    if (errorInsertProfile) {
      // console.log('Error in profile creation', errorInsertProfile)
      throw errorInsertProfile
    }

    const profile = insertedProfile[0]

    const listMap = {
      be: 21,
      autre: 34,
      employe_mairie: 22,
      elu: 22,
      agence_urba: 21
    }

    sibApi.optinNewsLetter(req.body.userData.email, req.body.userData.optin, [
      listMap[profile.poste]
    ])

    // Send email to connect
    await magicLinkSignIn({
      email: req.body.userData.email,
      redirectBasePath: req.body.redirectTo + `/collectivites/${profile.collectivite_id}?isEpci=${profile.collectivite_id.length > 5}`
    })

    slack.requestCollectiviteAccess(insertedProfile[0])

    // SI pas de recovery_sent_at et pas de email_confirmed_at -> first co
    // if (!connectionUser.email_confirmed_at && !connectionUser.recovery_sent_at) {
    //   slack.requestCollectiviteAccess(insertedProfile[0])
    // } else {
    //   throw new Error('Vous avez déjà un compte associé à cette adresse email. Nous vous avons renvoyé un email de connexion.')
    // }

    // Update pipedrive
    await pipedrive.signupCollectivite({
      ...req.body.userData,
      detailsCollectivite: req.body.detailsCollectivite
    })

    res.status(200).send(user)
  } catch (error) {
    console.log('ERROR /auth/signupCollectivite : ', error.message)
    res.status(500).send({ message: error.message })
  }
})

app.post('/hooksSignupStateAgent', async (req, res) => {
  await slack.requestStateAgentAccess(req.body)

  sibApi.optinNewsLetter(req.body.email, req.body.optin, [33])
  // Push in the good pipedrive
  // TODO: Attention au changement de nom dept / departement dans Signin() (pipedrive.js) & dans la fonction updateUserRole() (admin.js)
  // Verifier le validation Slack par la suite
  console.log('hooksSignupStateAgent: ', req.body)
  await pipedrive.signupStateAgent(req.body)

  res.status(200).send('OK')
})

module.exports = app
