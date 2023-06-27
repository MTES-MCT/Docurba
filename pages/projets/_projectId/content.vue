<template>
  <v-container v-if="loaded">
    <iframe v-if="pdfUrl" :src="pdfUrl" style="width: 100%;height: calc(100vh - 200px);border: none;" />
    <PACTreeviewContent
      v-if="project && !pdfUrl"
      :pac-data="project.PAC"
      :git-ref="`projet-${project.id}`"
      :project="project"
      @read="savePacItem"
    />
    <client-only>
      <v-btn
        v-if="!pdfUrl"
        depressed
        fab
        fixed
        bottom
        right
        :loading="printing"
        color="primary"
        :href="`/api/pdf/${project.id}`"
      >
        <v-icon>{{ icons.mdiDownload }}</v-icon>
      </v-btn>
    </client-only>
  </v-container>
  <VGlobalLoader v-else />
</template>
<script>
import { mdiDownload } from '@mdi/js'
import axios from 'axios'

export default {
  data () {
    return {
      project: null,
      pdfUrl: null,
      loaded: false,
      printing: false,
      icons: {
        mdiDownload
      }
    }
  },
  async mounted () {
    const projectId = this.$route.params.projectId

    const { data: projects } = await this.$supabase.from('projects').select('*').eq('id', projectId)
    const project = projects ? projects[0] : null

    this.project = project

    if (this.project.trame) {
      await this.setPACFromTrame()
    } else {
      await this.loadPACFile()
    }

    // Start Analytics
    this.$matomo([
      'trackEvent', 'Projet PAC', 'Content',
          `${this.project.doc_type} - ${this.project.epci ? this.project.epci.label : this.project.towns[0].nom_commune}`
    ])
    // End Analytics

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
        url: `/api/trames/tree/projet-${this.project.id}?content=true`
      })

      // console.log(sections)

      const sectionsPaths = this.project.PAC.map(p => p)
      this.project.PAC = sections.filter(s => sectionsPaths.includes(s.path))
      this.project.PAC.forEach(s => this.parseSection(s, sectionsPaths))
    },
    async loadPACFile () {
      const { signedURL: pdfUrl, err } = await this.$supabase.storage
        .from('projects-pac')
        .createSignedUrl(`${this.project.id}/pac.pdf`, 60 * 60)

      if (!err) {
        this.pdfUrl = pdfUrl
      } else {
        // eslint-disable-next-line no-console
        console.log('err loading pdf', err)
      }
    },
    savePacItem (pacItem) {
      // TODO: This need to be changed into its own table.
      const { PAC } = this.project

      const projectPacItem = PAC.find(item => item.path === pacItem.path)
      projectPacItem.checked = pacItem.checked
      // Object.assign(projectPacItem, pacItem)

      // console.log(pacItem, projectPacItem)

      // await this.$supabase.from('projects').update({ PAC }).eq('id', this.project.id)
    }
    // async print () {
    //   this.printing = true
    //   // this.$print(`/print/${this.project.id}`).then(() => {
    //   //   this.printing = false
    //   // })
    //   const pdf = await axios({
    //     url: `/api/pdf/${this.project.id}`,
    //     method: 'get'
    //   })

    //   console.log(pdf)

    //   this.printing = false
    // }
  }
}
</script>
