# docurba

## Build Setup

### Prerequisite

In dev you need to have a .env file at the root of the project with this keys:
- SENDGRID_API_KEY
- SUPABASE_ADMIN_KEY

This keys should not be public. After a build they should not be present in the .nuxt folder.

If you need to make public keys available refer to the documentation here: https://nuxtjs.org/tutorials/moving-from-nuxtjs-dotenv-to-runtime-config/#introducing-the-nuxt-runtime-config

```bash
# install dependencies
$ npm install

# serve with hot reload at localhost:3000
$ npm run dev

# build for production and launch server
$ npm run build
$ npm run start

# generate static project
$ npm run generate
```

For detailed explanation on how things work, check out [Nuxt.js docs](https://nuxtjs.org).

## deploy

The app.yaml is incomplete ! You need to make this keys available in process.env:
- SENDGRID_API_KEY
- SUPABASE_ADMIN_KEY

app.yaml is here as an example.

```bash
$ gcloud app deploy app.yaml --project docurba

$ gcloud app deploy app_dev.yaml --project docurba
```
