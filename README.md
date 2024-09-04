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
```

## Daily Script Execution

### Running the Daily Dump Script

To ensure the procedures daily updates from Sudocuh, follow these steps to run the `index.mjs` script located in the `daily_dump` folder:

1. **Download the Daily Dump:**
   - Before running the script, download the latest data dump for the day from Supabase. Ensure you are using the correct credentials to access this data.

2. **Verify the Environment:**
   - Confirm that the `.env` file contains the correct `SUPABASE_ADMIN_KEY` needed to authenticate and interact with the Supabase database.

3. **Running the Script:**
   - Navigate to the `daily_dump` folder and run the script by executing:
     ```bash
     $ node index.mjs
     ```
   - Ensure that the script is pointing to the newly downloaded dump file. This may involve adjusting the script or settings to target the correct file path.

### Important Notes:
- It's crucial to maintain the confidentiality of the `SUPABASE_ADMIN_KEY` and ensure it's not exposed in public repositories or shared environments.
- Regularly check and update the script if there are changes in the data structure or API from Supabase to avoid disruptions in daily updates.
