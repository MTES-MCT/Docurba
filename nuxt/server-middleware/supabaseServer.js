const express = require('express')
const app = express()

const { createServerClient, parseCookieHeader, serializeCookieHeader } = require('@supabase/ssr')

const supabaseUrl = 'https://supabase.docurba.beta.gouv.fr'
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYW5vbiIsImlhdCI6MTYzNDk3NTU3NiwiZXhwIjoxOTUwNTUxNTc2fQ.zvgWeMG3sKSwBKv8uGm5uy82cEyMyEMivQvNIDFhBkA'

function createClient (context) {
  return createServerClient(supabaseUrl, supabaseAnonKey, {
    cookies: {
      getAll () {
        return parseCookieHeader(context.req.headers.cookie ?? '')
      },
      setAll (cookiesToSet) {
        cookiesToSet.forEach(({ name, value, options }) =>
          context.res.appendHeader('Set-Cookie', serializeCookieHeader(name, value, options))
        )
      }
    }
  })
}

app.all('*', (req, res, next) => {
  createClient({ req, res })
  next()
})

module.exports = app
