import axios from 'axios'
import pdfMake from 'pdfmake/build/pdfmake'
// import pdfFonts from 'pdfmake/build/vfs_fonts'
import orderSections from '@/mixins/orderSections.js'
import departements from '@/assets/data/INSEE/departements_small.json'

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

const SOURCE_LABEL = {
  BASE_TERRITORIALE: 'Base territoriale',
  GEORISQUES: 'GéoRisques',
  INPN: 'INPN'
}

export default ({ $md, $isDev, $supabase }, inject) => {
  const baseUrl = $isDev ? 'http://localhost:3000' : location.origin

  // see https://github.com/MTES-MCT/Docurba/issues/61#issuecomment-1781502206
  const IMAGE_SRC_TO_REPLACE = 'https://sante.gouv.fr/local/adapt-img/608/10x/IMG/jpg/Etat_de_sante_population.jpg?1680693100'
  const IMAGE_SRC_REPLACEMENT = `${baseUrl}/images/pac/Etat_de_sante_population.jpg`

  pdfMake.fonts = {
    Marianne: {
      normal: `${baseUrl}/fonts/Marianne/fontes_desktop/Marianne-Regular.otf`,
      bold: `${baseUrl}/fonts/Marianne/fontes_desktop/Marianne-Bold.otf`,
      italics: `${baseUrl}/fonts/Marianne/fontes_desktop/Marianne-RegularItalic.otf`,
      bolditalics: `${baseUrl}/fonts/Marianne/fontes_desktop/Marianne-BoldItalic.otf`
    }
  }

  const pdfMaker = {
    pdfFromContent (pdfData, filename = 'PAC') {
      Object.assign(pdfData, {
        pageSize: 'A4',
        pageMargins: 40,
        styles: {
          title: { fontSize: 40, alignment: 'center' },
          tocTitle: { fontSize: 18 },
          h1: { fontSize: 24, bold: true, alignment: 'left', margin: [0, 12, 0, 0] },
          h2: { fontSize: 20, bold: true, alignment: 'left', margin: [0, 12, 0, 0] },
          h3: { fontSize: 18, bold: true, alignment: 'left', margin: [0, 12, 0, 0] },
          h4: { fontSize: 16, bold: true, alignment: 'left', margin: [0, 12, 0, 0] },
          h5: { fontSize: 14, bold: true, alignment: 'left', margin: [0, 12, 0, 0] },
          h6: { fontSize: 12, bold: true, alignment: 'left', margin: [0, 12, 0, 0] },
          a: { decoration: 'underline', color: '#000091' },
          p: { fontSize: 10, alignment: 'justify', margin: [0, 10, 0, 0] },
          list: { margin: [0, 10, 0, 0] },
          footer: { fontSize: 10, alignment: 'right' },
          ddt: { fontSize: 10, alignment: 'right' }
        },
        defaultStyle: {
          font: 'Marianne',
          fontSize: 10,
          lineHeight: 1.1,
          alignment: 'justify'
        },
        footer (currentPage, pageCount) {
          return {
            text: currentPage > 1 ? `${currentPage.toString()}` : '', // /${pageCount}`,
            style: 'footer',
            margin: [40, 10]
          }
        },
        pageBreakBefore (currentNode, followingNodesOnPage, nodesOnNextPage, previousNodesOnPage) {
          const isBreakedTitle = typeof (currentNode.style) === 'string' && currentNode.style?.includes('h') && currentNode.pageNumbers.length > 1
          return currentNode.headlineLevel === 1 || !!previousNodesOnPage.find(n => n.style === 'title') || isBreakedTitle
        }
      })

      pdfMake.createPdf(pdfData).download(`${filename}.pdf`)
    },
    // fetchGithubRef could go into its own plugin/mixin.
    async fetchGithubRef (githubRef, project) {
      const { data: [{ PAC: selectedSections }] } = await $supabase.from('projects').select('PAC').eq('id', project.id)

      const { data: sections } = await axios({
        method: 'get',
        url: `${baseUrl}/api/trames/tree/${githubRef}?content=all`
      })

      function deptToRef (deptCode) {
        if (deptCode?.includes('A') || deptCode?.includes('B')) {
          return deptCode
        } else {
          return +deptCode
        }
      }

      const { data: supSections } = await $supabase.from('pac_sections').select('*').in('ref', [
        githubRef,
        `dept-${deptToRef(project?.trame)}`,
        `region-${project?.towns ? project.towns[0].regionCode : ''}`,
        'main'
      ])

      orderSections.methods.orderSections(sections, supSections)

      const { data: attachments } = await $supabase.from('pac_sections_data').select('*').eq('ref', githubRef)

      function pushAttachments (section) {
        const sectionAttachments = attachments.filter(a => a.path === section.path)
        if (sectionAttachments.length) {
          const attachmentElements = []

          for (const attachment of sectionAttachments) {
            attachmentElements.push(
              {
                type: 'element',
                tag: 'li',
                children: [
                  {
                    type: 'element',
                    tag: 'a',
                    props: {
                      href: attachment.url
                    },
                    children: [
                      {
                        type: 'text',
                        value: `${SOURCE_LABEL[attachment.source]} - ${attachment.category ? (attachment.category + ' - ') : ''}${attachment.title}`
                      }
                    ]
                  }
                ]
              }
            )
          }

          section.body.children.push({
            type: 'element',
            tag: 'ul',
            props: {},
            children: attachmentElements
          })
        }
      }

      function parseSection (section, paths) {
        if (section.content) {
          if (section.content.startsWith('<')) {
            section.body = $md.processHtml(section.content)
          } else {
            section.body = $md.processMarkdown(section.content)
          }
        }

        pushAttachments(section)

        if (section.children) {
          section.children = section.children.filter(c => paths.includes(c.path))
          section.children.forEach(c => parseSection(c, paths))
        }
      }

      const parsedSections = sections.filter(s => selectedSections.includes(s.path))
      parsedSections.forEach(s => parseSection(s, selectedSections))

      return parsedSections
    },
    async pdfFromRef (githubRef, project) {
      const roots = await this.fetchGithubRef(githubRef, project)

      const dept = departements.find(d => d.code === project.trame)

      const pdfContent = {
        content: [
          {
            columns: [{
              width: 100,
              fit: [100, 100],
              image: 'logo'
            }, {
              width: '*',
              text: `Direction départementale des territoires \n ${dept.intitule}`,
              style: 'ddt'
            }]
          },
          {
            text: project.name,
            style: 'title',
            margin: [0, 200, 0, 0]
          },
          {
            toc: { title: { text: 'SOMMAIRE' } }
          }
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

          if (element.tag === 'strong' || element.bold) {
            newParams.bold = true
          }

          if (element.tag === 'em' || element.italics) {
            newParams.italics = true
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
        } else if (/^h[1-6]$/.test(element.tag)) {
          const text = extractText(element.children)

          if (text.length) {
            pdfContent.content.push({
              text,
              style: element.tag,
              headlineLevel
            })
          }
        } else if (element.tag === 'ul' || element.tag === 'ol') {
          pdfContent.content.push({
            [element.tag]: extractText(element.children),
            headlineLevel,
            style: 'list'
          })
        } else if (element.tag === 'img') {
          if (element.props.src) {
            if (element.props.src === IMAGE_SRC_TO_REPLACE) {
              // see https://github.com/MTES-MCT/Docurba/issues/61#issuecomment-1781502206
              element.props.src = IMAGE_SRC_REPLACEMENT
            }

            pdfContent.content.push({
              image: `SRC:${element.props.src}`,
              width: 450,
              headlineLevel
            })

            pdfContent.images[`SRC:${element.props.src}`] = element.props.src.includes('http') ? element.props.src : `${baseUrl}${element.props.src}`
          }
        } else {
          pdfContent.content.push({
            stack: extractText(element.children),
            style: element.tag,
            headlineLevel
          })
        }
      }

      const elements = []
      const elementsTags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'img']
      // const textTags = ['strong', 'u', 'a']

      function pushElements (body, depth) {
        if (body?.children) {
          let text = { tag: 'p', children: [] }

          body.children.forEach((child) => {
            if (child.type === 'element') {
              if (elementsTags.includes(child.tag)) {
                if (/^h[1-6]$/.test(child.tag)) {
                  const headerLevel = Number(child.tag.charAt(1))
                  if (headerLevel <= depth) {
                    child.tag = `h${Math.min(depth + 1, 6)}`
                  }
                }

                if (text.children.length) {
                  elements.push(text)
                  text = { tag: 'p', children: [] }
                }
                elements.push(child)
              } else {
                text.children.push(child)
              }
            } else {
              text.children.push(child.value)
            }
          })

          if (text.children.length) {
            elements.push(text)
          }
        }
      }

      function findBodies (children, depth) {
        children.forEach((child) => {
          if (depth === 0) {
            elements.push({
              tag: 'pageBreak',
              children: []
            })
          }

          elements.push({
            tag: `h${depth + 1}`,
            children: [
              {
                text: child.name,
                tocItem: true,
                tocMargin: [16 * depth, 0, 0, 0],
                tocStyle: 'a'
              }
            ]
          })

          if (child.body) { pushElements(child.body, depth) }
          if (child.children) { findBodies(child.children, depth + 1) }
        })
      }

      findBodies(roots, 0)

      elements.forEach((element, index) => {
        if (element.tag === 'pageBreak') {
          elements[index + 1].headlineLevel = 1
        }
        addElementToContent(element)
      })

      await this.pdfFromContent(pdfContent, `${project.doc_type} - ${project.name}`)
    }
  }

  inject('pdf', pdfMaker)
}
