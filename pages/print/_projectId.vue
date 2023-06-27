<template>
  <div>
    <v-app-bar
      elevation="0"
      color="white"
      class="fr-header"
      height="68px"
      absolute
    >
      <div class="fr-header__body">
        <div class="fr-container">
          <div class="fr-header__body-row">
            <div class="fr-header__brand fr-enlarge-link">
              <div class="fr-header__brand-top">
                <div class="fr-header__logo">
                  <a href="/" title="Accueil - Docurba">
                    <p class="fr-logo">
                      république
                      <br>française
                    </p>
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <v-spacer />
      <div class="ddt-text text-right">
        Direction départementale des territoires <br>
        {{ project.towns[0].nom_departement }}
      </div>
    </v-app-bar>
    <PACPDFPagesCounters :pac-data="project.PAC" content-id="pac-content-pdf" />
    <table>
      <thead>
        <tr>
          <td>
            <div class="header-space" />
          </td>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>
            <PACPDFGardeTemplate :project="project" />
          </td>
        </tr>
      </tbody>
    </table>
    <table>
      <tbody>
        <tr>
          <td>
            <PACPDFTableOfContent :pac-data="project.PAC" />
          </td>
        </tr>
      </tbody>
    </table>
    <table id="pac-content-pdf" ref="contentPages">
      <tbody>
        <tr>
          <td>
            <PACPDFPagesTemplate :pac-data="project.PAC" />
          </td>
        </tr>
      </tbody>
      <tfoot>
        <tr>
          <td>
            <div class="footer-space" />
          </td>
        </tr>
      </tfoot>
    </table>
  </div>
</template>

<script>
import axios from 'axios'
import orderSections from '@/mixins/orderSections.js'

export default {
  layout: 'print',
  async asyncData ({ $supAdmin, $md, route, $isDev }) {
    const projectId = route.params.projectId

    if (process.server) {
      try {
        const { data: projects } = await $supAdmin.from('projects').select('*').eq('id', projectId)
        const project = projects[0]

        const baseUrl = $isDev ? 'http://localhost:3000' : 'https://docurba.beta.gouv.fr'

        const { data: sections } = await axios({
          method: 'get',
          url: `${baseUrl}/api/trames/tree/projet-${projectId}?content=all`
        })

        const { data: supSections } = await $supAdmin.from('pac_sections').select('*').in('ref', [
          `projet-${project.id}`,
          `dept-${project.towns ? project.towns[0].code_departement : ''}`,
          `region-${project.towns ? project.towns[0].code_region : ''}`,
          'main'
        ])

        orderSections.methods.orderSections(sections, supSections)

        function parseSection (section, paths) {
          if (section.content) { section.body = $md.compile(section.content) }

          if (section.children) {
            section.children = section.children.filter(c => paths.includes(c.path))
            section.children.forEach(c => parseSection(c, paths))
          }
        }

        const sectionsPaths = project.PAC.map(p => p)
        project.PAC = sections.filter(s => sectionsPaths.includes(s.path))
        project.PAC.forEach(s => parseSection(s, sectionsPaths))

        return {
          project,
          loaded: true
        }
      } catch (err) {
        // eslint-disable-next-line no-console
        console.log('error printing', err)
      }
    }
  }
}
</script>

<style scoped>
  table {
    max-width: 176mm;
    width: 100%;
    table-layout: fixed;
  }

  table, tr, td {
    page-break-inside: avoid;
    /* vertical-align: middle; */
  }

  .ddt-text {
    font-size: 14pt;
    font-weight: 700;
  }

 .header-space {
   height: calc(68px + 8.5mm);
 }

 .footer-space {
   /* height: calc(68px + 8.5mm); */
   /* height: calc(10mm); */
   height: 17mm;
 }

.fr-header .fr-header__body-row, .fr-header .fr-header__logo, .fr-header .fr-logo {
  padding: 0mm !important;
  margin: 0mm !important
}

.fr-header a {
  color: #1e1e1e;
  text-decoration: none;
}
</style>
