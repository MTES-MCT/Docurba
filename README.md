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

## Dev

### Manipulating PAC Data
A PAC can be composed of multiple Trame. A Trame is a combination of multiple Sections.

Sections overide each others keys using their path as identifier. Overide respect this hierarchie:
project > departement > region > national

To merge sections a component should mixin unifiedPac.js

A component that merge Sections into a tram should be a Page and also subscribe to the real time DB to update the PAC if it's interacted with.

This way the app can respect the flux patern where data updates flow from the parent to all its children.

To limit confusion, component that need to handle a Tram should mixin the pacContent.js file.

Finally, component that allow editing can mixin the pacEditing.js file. In the best case, their parent should handle data updates and they should not update the state of the data by themselves.
