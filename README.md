# docurba

## Overview

Docurba's mission is to facilitate the development and monitoring of urban planning documents in order to more quickly and effectively address environmental issues. This documentation will guide you through the setup, development, and deployment processes.

## Tech Stack

`docurba` is built using a Vue2 tech stack designed for rapid development and scalability:

- **[Nuxt 2](https://v2.nuxt.com/):** A powerful Vue.js framework that enables server-side rendering (SSR), static site generation (SSG), and seamless development experiences.
- **[Vuetify 2](https://vuetifyjs.com/en/):** A Vue.js UI library that we have customized to align with the [French Government's Design System](https://www.systeme-de-design.gouv.fr/).
- **[Supabase](https://supabase.com/docs):** An open-source Firebase alternative that provides a PostgreSQL database, authentication, and real-time subscriptions.

## Build Setup

### Prerequisites

Before you start, ensure you have a `.env` file at the root of the project with the following keys:

- `SENDGRID_API_KEY`
- `SUPABASE_ADMIN_KEY`
- `SLACK_WEBHOOK`
- `SLACK_EVENT_CTBE`
- `PIPEDRIVE_API_KEY`
- `BREVO_API_KEY`
- `GITHUB_PAC_REPO_NAME`
- `GITHUB_PAC_REPO_OWNER`

**Important:** These keys are sensitive and should never be made public. After building the project, ensure they are not included in the `.nuxt` folder. For making public keys available, refer to the [Nuxt.js runtime config documentation](https://nuxtjs.org/tutorials/moving-from-nuxtjs-dotenv-to-runtime-config/#introducing-the-nuxt-runtime-config).

### Installation

Follow these steps to set up the project locally:

```bash
# Install dependencies
$ npm install

# Serve with hot reload at localhost:3000
$ npm run dev

# Build for production
$ npm run build

# Launch the production server
$ npm run start
