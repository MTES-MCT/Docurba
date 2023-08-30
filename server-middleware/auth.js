const express = require('express')
const app = express()
app.use(express.json())

const { createClient } = require('@supabase/supabase-js')
const supabase = createClient('https://ixxbyuandbmplfnqtxyw.supabase.co', process.env.SUPABASE_ADMIN_KEY)

// modules
const sendgrid = require('./modules/sendgrid.js')
const pipedrive = require('./modules/pipedrive.js')
const slack = require('./modules/slack.js')

app.post('/password', async (req, res) => {
  // console.log('/password body', req.body)

  const { data: user, error } = await supabase.auth.admin.generateLink({
    type: 'recovery',
    email: req.body.email
  })

  // The user will be redirected to this url in case of password recovery.
  // https://docurba.beta.gouv.fr/#access_token=XXX&expires_in=3600&refresh_token=XXX&token_type=bearer&type=recovery

  // https://ixxbyuandbmplfnqtxyw.supabase.co/auth/v1/verify?token=XXX&type=recovery&redirect_to=https://docurba.beta.gouv.fr/
  // console.log('user.action_link', user.action_link)

  if (!error && user && user.properties.action_link) {
    sendgrid.sendEmail({
      to: req.body.email,
      template_id: 'd-06e865fdc30d42a398fdc6bc532deb82',
      dynamic_template_data: {
        redirectURL: user.properties.action_link
      }
    })

    res.status(200).send('OK')
  } else {
    // eslint-disable-next-line no-console
    console.log('Error reset password', error)
    res.status(400).send(error)
  }
})

async function magicLinkSignIn ({ email, shouldExist, redirectBasePath }) {
  const { data: { user, properties }, error } = await supabase.auth.admin.generateLink(
    {
      type: 'magiclink',
      email,
      options: {
        redirectTo: redirectBasePath
      }
    }
  )
  if (error) {
    console.log('ERROR magicLinkSignIn: ', error)
    throw error
  }
  if (shouldExist && !user.email_confirmed_at) {
    throw new Error('Vous devez créer un compte avant de pouvoir vous connecter.')
  }
  if (properties && properties.action_link) {
    sendgrid.sendEmail({
      to: email,
      template_id: 'd-766d017b51124a108cabc985d0dbf451',
      dynamic_template_data: {
        redirectURL: properties.action_link
      }
    })
  }
  return user
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
    const user = await magicLinkSignIn({ email: req.body.email, shouldExist: true, redirectBasePath: req.body.redirectTo + path })
    res.status(200).send(user)
  } catch (error) {
    console.log('ERROR /auth/signinCollectivite : ', error.message)
    res.status(500).send({ message: error.message })
  }
})

app.post('/signupCollectivite', async (req, res) => {
  try {
    const user = await magicLinkSignIn({ email: req.body.userData.email, redirectBasePath: req.body.redirectTo })

    // SI pas de recovery_sent_at et pas de email_confirmed_at -> first co
    if (!user.email_confirmed_at && !user.recovery_sent_at) {
      const { data: insertedProfile, error: errorInsertProfile } = await supabase.from('profiles').insert({ ...req.body.userData, side: 'collectivite', user_id: user.id }).select()
      if (errorInsertProfile) { throw errorInsertProfile }
      slack.requestCollectiviteAccess(insertedProfile[0])
    } else {
      throw new Error('Vous avez déjà enregistrer un compte, nous vous avons renvoyé un email de connexion.')
    }
    res.status(200).send(user)
  } catch (error) {
    console.log('ERROR /auth/signupCollectivite : ', error.message)
    res.status(500).send({ message: error.message })
  }
})

app.post('/hooksSignupStateAgent', async (req, res) => {
  await slack.requestStateAgentAccess(req.body)
  // Push in the good pipedrive
  // TODO: Attention au changement de nom dept / departement dans Signin() (pipedrive.js) & dans la fonction updateUserRole() (admin.js)
  // Verifier le validation Slack par la suite
  await pipedrive.signup(req.body)

  res.status(200).send('OK')
})

module.exports = app
