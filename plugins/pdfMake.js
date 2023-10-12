import axios from 'axios'
import pdfMake from 'pdfmake/build/pdfmake'
// import pdfFonts from 'pdfmake/build/vfs_fonts'
import orderSections from '@/mixins/orderSections.js'

// pdfMake.vfs = pdfFonts.pdfMake.vfs

// This is only to speed up in test. Do not push in prod.
// import sections from '@/assets/test/sections.json'

pdfMake.fonts = {
  Marianne: {
    normal: 'https://docurba.beta.gouv.fr/fonts/Marianne/fontes_desktop/Marianne-Regular.otf',
    bold: 'https://docurba.beta.gouv.fr/fonts/Marianne/fontes_desktop/Marianne-Bold.otf',
    italics: 'https://docurba.beta.gouv.fr/fonts/Marianne/fontes_desktop/Marianne-RegularItalic.otf',
    bolditalics: 'https://docurba.beta.gouv.fr/fonts/Marianne/fontes_desktop/Marianne-BoldItalic.otf'
  }
}

export default ({ $md, $isDev, $supabase }, inject) => {
  const baseUrl = $isDev ? 'http://localhost:3000' : location.origin

  pdfMake.fonts = {
    Marianne: {
      normal: `${baseUrl}/fonts/Marianne/fontes_desktop/Marianne-Regular.otf`,
      bold: `${baseUrl}/fonts/Marianne/fontes_desktop/Marianne-Bold.otf`,
      italics: `${baseUrl}/fonts/Marianne/fontes_desktop/Marianne-RegularItalic.otf`,
      bolditalics: `${baseUrl}/fonts/Marianne/fontes_desktop/Marianne-BoldItalic.otf`
    }
  }

  const pdfMaker = {
    pdfFromContent (pdfData) {
      Object.assign(pdfData, {
        pageSize: 'A4',
        pageMargins: 65,
        styles: {
          title: { fontSize: 40, alignment: 'center' },
          tocTitle: { fontSize: 18 },
          h1: { fontSize: 40, alignment: 'left' },
          h2: { fontSize: 32, alignment: 'left' },
          h3: { fontSize: 28, alignment: 'left' },
          h4: { fontSize: 24, alignment: 'left' },
          h5: { fontSize: 22, alignment: 'left' },
          h6: { fontSize: 20, alignment: 'left' },
          a: { decoration: 'underline', color: '#000091' },
          p: { fontSize: 14, alignment: 'justify' },
          footer: { fontSize: 12, alignment: 'right' },
          ddt: { fontSize: 14, alignment: 'right' }
        },
        defaultStyle: {
          font: 'Marianne',
          fontSize: 14,
          alignment: 'justify'
        },
        footer (currentPage, pageCount) {
          return {
            text: currentPage > 1 ? `${currentPage.toString()}` : '', // /${pageCount}`,
            style: 'footer',
            margin: [65, 10]
          }
        },
        pageBreakBefore (currentNode, followingNodesOnPage, nodesOnNextPage, previousNodesOnPage) {
          const isBreakedTitle = typeof (currentNode.style) === 'string' && currentNode.style?.includes('h') && currentNode.pageNumbers.length > 1
          return currentNode.headlineLevel === 1 || !!previousNodesOnPage.find(n => n.style === 'title') || isBreakedTitle
        }
      })

      pdfMake.createPdf(pdfData).download('file.pdf')
    },
    // fetchGithubRef could go into its own plugin/mixin.
    async fetchGithubRef (githubRef, project) {
      const { data: sections } = await axios({
        method: 'get',
        url: `${baseUrl}/api/trames/tree/${githubRef}?content=all`
      })

      function deptToRef (deptCode) {
        if (deptCode.includes('A') || deptCode.includes('B')) {
          return deptCode
        } else {
          return +deptCode
        }
      }

      const { data: supSections } = await $supabase.from('pac_sections').select('*').in('ref', [
        githubRef,
        `dept-${project?.towns ? deptToRef(project.towns[0].departementCode) : ''}`,
        `region-${project?.towns ? project.towns[0].regionCode : ''}`,
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
      const parsedSections = sections.filter(s => sectionsPaths.includes(s.path))
      parsedSections.forEach(s => parseSection(s, sectionsPaths))

      return parsedSections
    },
    async pdfFromRef (githubRef, project) {
      const roots = await this.fetchGithubRef(githubRef, project)

      const pdfContent = {
        content: [
          {
            columns: [{
              width: 100,
              fit: [100, 100],
              image: 'logo'
            }, {
              width: '*',
              text: `Direction départementale \n des territoires du ${project.towns[0].departementCode}`,
              style: 'ddt'
            }]
          },
          {
            text: project.name,
            style: 'title',
            margin: [0, 200, 0, 0]
          }
          // {
          //   toc: { title: { text: project.name, style: 'h1' } }
          // }
        ],
        images: {
          logo: `${baseUrl}/images/Republique_Francaise.jpg`
        }
      }

      function extractText (elements, params = {}) {
        return elements.map((element) => {
          const content = Object.assign({
            text: '\n',
            style: element.tag
          }, params)

          const newParams = {}

          if (element.tag === 'a' || params.tag === 'a') {
            content.link = element.props.href || params.link
            newParams.link = element.props.href || params.link
            newParams.style = 'a'
          }

          if (element.tag === 'li') {
            if (element.children[0].value === '\n') {
              element.children.splice(0, 1)
            }
          }

          if (element.children && element.children.length) {
            content.text = extractText(element.children, Object.assign({}, params, newParams))
          } else if (!element.children) {
            content.text = element.value || element
          }

          return content
        })
      }

      function addElementToContent (element) {
        const headlineLevel = element.headlineLevel

        if (!element.tag) {
          pdfContent.content.push({
            text: element.value || element,
            headlineLevel
          })
        } else if (element.tag.includes('h')) {
          const text = extractText(element.children)

          const isToc = ['h1', 'h2', 'h3'].includes(element.tag)

          if (text.length) {
            pdfContent.content.push({
              text,
              style: element.tag,
              tocItem: isToc ? element.tocId : false,
              tocMargin: element.tocMargin,
              headlineLevel,
              margin: [0, 10, 0, 0]
            })
          }
        } else if (element.tag === 'ul' || element.tag === 'ol') {
          pdfContent.content.push({
            [element.tag]: extractText(element.children.filter(c => c !== '\n' && c.value !== '\n')),
            headlineLevel
          })
        } else if (element.tag === 'img') {
          if (element.props.src) {
            pdfContent.content.push({
              image: `SRC:${element.props.src}`,
              width: 450,
              headlineLevel
            })

            pdfContent.images[`SRC:${element.props.src}`] = element.props.src.includes('http') ? element.props.src : `${baseUrl}${element.props.src}`
          }
        } else {
          pdfContent.content.push({
            text: extractText(element.children),
            style: element.tag,
            headlineLevel
          })
        }
      }

      const elements = []
      const elementsTags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'img']
      // const textTags = ['strong', 'u', 'a']

      const tocs = []

      function pushElements (body, tocId, tocMargin) {
        if (body.children) {
          let text = { tag: 'p', children: [] }

          body.children.forEach((child) => {
            if (child.type === 'element') {
              if (elementsTags.includes(child.tag)) {
                if (text.children.length) {
                  elements.push(text)
                  text = { tag: 'p', children: [] }
                }
                elements.push(Object.assign(child, { tocId, tocMargin }))
              } else {
                text.children.push(child)
              }
            } else { text.children.push(child.value) }
          })

          if (text.children.length) {
            elements.push(text)
          }
        }
      }

      function findBodies (children, level) {
        children.forEach((child, index) => {
          tocs.push({
            toc: {
              id: `${level}-${child.path}`,
              title: {
                text: '',
                style: 'tocTitle'
              }
            }
          })

          if (child.body) { pushElements(child.body, `${level}-${child.path}`, [15 * level, 0, 0, 0]) }
          if (child.children) { findBodies(child.children, level + 1) }
        })
      }

      roots.forEach((root) => {
        if (root.path !== 'PAC/Introduction') {
          tocs.push({
            toc: {
              id: root.name,
              title: {
                text: root.name, style: 'h6'
              }
            }
          })
        }

        elements.push({ tag: 'pageBreak', children: [] })
        pushElements(root.body, root.name)
        findBodies(root.children, 0)
      })

      pdfContent.content.push(...tocs)

      elements.forEach((element, index) => {
        if (element.tag === 'pageBreak') {
          elements[index + 1].headlineLevel = 1
        }
        addElementToContent(element)
      })

      // console.log(JSON.stringify(pdfContent.content, null, 2))

      await this.pdfFromContent(pdfContent)
    }
  }

  inject('pdf', pdfMaker)
}
