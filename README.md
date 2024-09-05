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

## PostgreSQL Database Structure

### Procedures Hierarchy and opposability

The data within our PostgreSQL database is structured with a clear hierarchy to organize the urban planning documents efficiently:

- **Projects**: This is the top-level entity representing overarching urban planning initiatives. It serves as a center point for all ressources, PAC, procedures and more in the future.
- **Procedures**: Nested within Projects, these are the specific sets of metadata regarding a procedure.
- **Procedures Events and Perimeters (`procedures_events` = `procedures_perimetres`)**: These are further nested within Procedures, detailing the events and geographical perimeters that are pertinent to each procedure.

### Opposability in Procedures

Opposability is a key concept in our data model, reflecting the legal enforceability of a procedure within specific perimeters. Here’s how opposability works:

- **Event-Driven Opposability**:
  - A procedure becomes opposable when it includes an event that legally enforces it. However, the opposability of a procedure is not uniformly applicable across all geographical perimeters.
  - This means that a procedure might be opposable in one part of its perimeter but not in another, depending on the specific legal events associated with each section.

### Determining Opposability in Communes

- **Most Recent Opposable Event**: For a commune, the opposable procedure is generally the one associated with the most recent opposable event. This recent event takes precedence in determining the legal enforceability of the procedure within the commune.
- **Implementation Details**: The full system, including any exceptions to how opposability is determined, can be retro-engineered by examining the `procedure.js` module located in the `server-middleware` folder. This module contains the logic that manages the relationships and status determinations based on procedures events.

You can find exemples in this videos:
- [Opposability for a commune](https://www.loom.com/share/a04e1829ac364663835406d714bd94cb?sid=89cab719-7a42-4963-839b-e5815154a977)
- [Oposability for a commune D](https://www.loom.com/share/a9cb048098934a439891910a10fb95f8?sid=0e764640-b885-4cd0-98da-58122f4741a2)
- [Groups of groups](https://www.loom.com/share/71eaa777ef6d488b8ade65a24625514d?sid=68ae4ee1-99da-484b-bb92-a37d746e87bb)

### Practical Implications

- **Selective Enforcement**: It’s crucial to note that the status of a procedure being opposable due to an event does not automatically apply to all perimeters within that procedure. Each perimeter must be evaluated based on the events that pertain to it.
- **Data Management**: When managing this data, ensure that each perimeter within a procedure is accurately tagged with its opposability status based on the events recorded. This selective tagging helps in maintaining precise control over where and how the legal implications of the procedures apply. (See the daily dump section to maintain opposability up to date with events from Sudocuh)

This structured approach allows us to maintain a high level of detail and accuracy in managing the legal statuses of urban planning documents with very few complexity in our data model.

## Documents Versioning with Git

### Overview

For managing the versioning of documents related to Porté à connaissance (PAC), `docurba` utilizes a dedicated Git repository. This setup allows us to track changes and maintain updates efficiently across different administrative levels.

### Repository Structure

- **Branch Hierarchy**: Each French département has its own branch in the repository, which is automaticaly updated to reflect the latest changes from its region or the national version. This hierarchical branching ensures that each département can access the most current and relevant information.
- **Project Branches**: When a DDT (Direction Départementale des Territoires) creates a project, a new branch is created for that specific project. This branch is generated from a checkout of the départemental branch, using the project ID to name the branch, ensuring a direct and traceable link to the originating information.

### Implementation Details

- **Service and Code Location**:
  - The main functionalities of this Git-based versioning system are handled by the `trame.js` service, located within the `server-middleware` directory of the project.
  - Additionally, it utilizes GitHub-specific functionality managed through modules located in the `modules/github` directory. These modules are designed to facilitate operations such as branch management, file handling, and other Git operations.

### Goals for Repository Independence

- **Reusable System**: One of the primary goals for using a Git repository is to keep the document versioning system as independent as possible from the rest of the `docurba` application. This independence ensures that the system can be reused or integrated into other projects or frameworks without requiring the entire `docurba` platform.
- **Identification by Filename**: Within this repository, PAC sections are uniquely identified by their filenames, rather than database IDs. This method avoids the complexities of database management and enhances the portability of the repository for use in different contexts.

## Data Integration in Docurba

### Overview

Initially, Docurba was created as a platform to provide easy access to essential data needed to produce urban planning documents. While the data requirements are nearly always consistent, the sources of this data vary by region and département.

### Mission and Methodology

- **Indexing over Hosting**: The mission of Docurba is not to centralize the hosting of data but rather to index and make it more easily accessible. This approach ensures that Docurba can serve as a dynamic hub for urban planning data, linking users to the most relevant and current data sources.

### Integrated Data Sources

1. **Base Territorial**:
   - Handled specifically by each region. Implementation examples can be found in the `daturba.js` plugin, which indexes and retrieves data as required by regional specifications.

2. **Geo-IDE**:
   - Integrated within the `daturba.js` plugin. This source is managed with the `geoide api` located in the service middleware, facilitating the access to geographical data interfaces provided by Geo-IDE.

3. **Geo Risque**:
   - Also managed through the `daturba.js` plugin in conjunction with the `geoide api` service middleware.

4. **INPN**:
   - Directly implemented in the `INPNTable` component. This national API provides access to detailed environmental and ecological data across France.

5. **GPU**:
   - Implemented in the `gpu.vue` page. This source uses a national API.
