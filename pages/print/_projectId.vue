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
      <div v-if="project && loaded" class="ddt-text text-right">
        Direction départementale des territoires <br>
        {{ project.towns[0].nom_departement }}
      </div>
    </v-app-bar>
    <PACPDFPagesCounters v-if="project && loaded" :pac-data="project.PAC" content-id="pac-content-pdf" />
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
            <PACPDFGardeTemplate v-if="project && loaded" :project="project" />
          </td>
        </tr>
      </tbody>
    </table>
    <table>
      <tbody>
        <tr>
          <td>
            <PACPDFTableOfContent v-if="project && loaded" :pac-data="project.PAC" />
          </td>
        </tr>
      </tbody>
    </table>
    <table id="pac-content-pdf" ref="contentPages">
      <tbody>
        <tr>
          <td>
            <PACPDFPagesTemplate v-if="project && loaded" :pac-data="project.PAC" />
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

export default {
  layout: 'print',
  data () {
    return {
      project: null,
      loaded: false,
      PACroots: []
    }
  },
  head () {
    return {
      title: this.project ? this.project.name : 'PAC',
      titleTemplate: ''
    }
  },
  async mounted () {
    const projectId = this.$route.params.projectId

    const { data: projects } = await this.$supabase.from('projects').select('*').eq('id', projectId)
    this.project = projects[0]

    await this.setPACFromTrame()

    this.loaded = true
  },
  methods: {
    parseSection (section, paths) {
      if (section.content) { section.body = this.$md.compile(section.content) }

      if (section.children) {
        section.children = section.children.filter(c => paths.includes(c.path))
        section.children.forEach(c => this.parseSection(c, paths))
      }
    },
    async setPACFromTrame () {
      const { data: sections } = await axios({
        method: 'get',
        url: `/api/trames/tree/projet-${this.project.id}?content=all`
      })

      // console.log(sections)

      const sectionsPaths = this.project.PAC.map(p => p)
      this.project.PAC = sections.filter(s => sectionsPaths.includes(s.path))
      this.project.PAC.forEach(s => this.parseSection(s, sectionsPaths))

      this.$nextTick(() => {
        window.parent.postMessage('print', '*')
      })
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
   height: calc(10mm);
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
