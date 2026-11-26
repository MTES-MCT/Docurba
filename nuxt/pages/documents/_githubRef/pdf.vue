<script>
import slugify from 'slugify'
import orderSections from '~/mixins/orderSections'

export default {
  mixins: [orderSections],
  layout: 'print',
  data () {
    return {
      docType: '',
      loading: true,
      name: '',
      sections: [],
      territorialAuthorityName: ''
    }
  },
  head () {
    return {
      titleTemplate: this.isProject
        ? `${this.docType} - ${this.name}`
        : this.title
    }
  },
  computed: {
    gitRef () {
      return this.$route.params.githubRef
    },
    isProject () {
      return this.gitRef.startsWith('projet')
    },
    title () {
      if (this.isProject) {
        return this.name
      }
      if (this.gitRef.startsWith('dept')) {
        return 'Trame départementale'
      }
      if (this.gitRef.startsWith('region')) {
        return 'Trame régionale'
      }
      if (this.gitRef === 'main') {
        return 'Trame nationale'
      }

      return ''
    }
  },
  watch: {
    gitRef: {
      async handler (value) {
        if (!value) {
          return
        }

        this.loading = true

        let project = null

        // Get project
        if (value.startsWith('projet')) {
          project = await this.$nuxtApi.get(`/api/projects/${value.replace('projet-', '')}`)

          if (!project) {
            this.loading = false

            return
          }

          this.docType = project.doc_type
          this.name = project.name
          this.territorialAuthorityName = (
            await this.$collectiviteApi.getFromCode(project.collectivite_id)
          ).intitule
        }

        // Get sections
        const sections = this.toSections(
          await this.$nuxtApi.get(`/api/trames/tree/${value}`),
          project
            ? ({ path }) => project.PAC.includes(path)
            : () => true
        )
        // order sections
        this.orderSections(sections, (
          await this.$supabase.from('pac_sections')
            .select('*')
            .in('ref', this.$options.filters.allHeadRefs(value, project))
        ).data)
        // Get sections contents
        this.sections = this.toContent(sections, Object.fromEntries(
          await Promise.all(
            this.toPaths(sections).map(async (path) => {
              try {
                return [path, (await this.$nuxtApi.get('/api/trames/file', {
                  path: `${path}${path.endsWith('.md') ? '' : '/intro.md'}`,
                  ref: value
                })).replace(/---([\s\S]*)---/, '')]
              } catch {
                return [path, '']
              }
            })
          )
        ))

        this.loading = false

        // Wait for children to render
        await this.$nextTick()
        // Wait for images to load
        await new Promise((resolve) => {
          const images = Array.from(this.$el.querySelectorAll('img'))
          const onLoad = () => {
            resolve()
            images.forEach((img) => {
              img.removeEventListener('load', onLoad)
            })
          }

          for (const img of images) {
            if (img.complete) {
              return resolve()
            }

            img.addEventListener('load', onLoad)
          }
        })
        window.print()
        // Delay close after print
        setTimeout(() => {
          window.close()
        }, 0)
      },
      immediate: true
    }
  },
  methods: {
    toContent (sections, contentByPath) {
      return sections.map(section => ({
        ...section,
        children: section.children
          ? this.toContent(section.children, contentByPath)
          : [],
        content: contentByPath[section.path] || ''
      }))
    },
    toPaths (sections) {
      return sections.flatMap(section => [
        section.path,
        ...this.toPaths(section.children || [])
      ])
    },
    toSections (rawSections, filter) {
      const sections = []

      rawSections.forEach((rawSection) => {
        if (!filter(rawSection)) {
          return
        }

        sections.push({
          children: rawSection.children
            ? this.toSections(rawSection.children, filter)
            : [],
          id: slugify(rawSection.path.replace(/\.md$/, '').replace(/\//g, '_')),
          label: rawSection.name,
          path: rawSection.path
        })
      })

      return sections
    }
  }
}
</script>

<template>
  <VGlobalLoader v-if="loading" />
  <DUPdf v-else>
    <template #header>
      <img
        alt="République française"
        src="~/assets/images/republique-francaise-short.svg"
      >
      <p v-if="isProject">
        Direction départementale des territoire
        <br>
        {{ territorialAuthorityName }}
      </p>
    </template>
    <template #title>
      {{ title }}
    </template>
    <template #default>
      <h2>Sommaire</h2>
      <DUPdfTree :value="sections" />
      <DUPdfSection
        v-for="section in sections"
        :id="section.id"
        :key="section.path"
        :children="section.children"
        :content="section.content"
        :label="section.label"
      />
    </template>
  </DUPdf>
</template>
